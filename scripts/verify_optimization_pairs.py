"""Compile and run both halves of a recursion/iteration pair, keep only the ones that agree.

The `improved_code` targets in the existing corpus were LLM-written and never
executed, so the model learned tidying rather than algorithmic change (see the
note in `prompt.py`). This script exists so that mistake is not repeated: a
hand-collected pair earns its place in the dataset by compiling, running, and
producing byte-identical output to the version it replaces.

    uv run python scripts/verify_optimization_pairs.py my_data_annotation/recursion_optimization

Writes `pairs.jsonl` (rows training reads directly) and `rejected.jsonl` (every
dropped pair with the reason), next to the inputs.

Four checks, in the order that fails cheapest first:

    1. side A is actually recursive        - otherwise there is nothing to optimise
    2. side B is not recursive             - otherwise nothing was optimised
    3. both compile                        - a target that does not build is not a target
    4. both produce the same stdout        - the only check that catches a wrong rewrite

Check 4 needs an entry point. A bare `class Solution` body has none, and used to
be rejected for it - 20 of 62 rejections, none of them a bad rewrite, only an
un-runnable one. Those now fall through to `verification.verify`, which builds a
driver from the function signature and feeds it generated arguments. The gate is
unchanged in what it demands: both versions still compile, still run, and still
have to print the same thing. Only the `main` is supplied.

What is *not* supplied is input. A program waiting on `cin` is still rejected
without a recorded `stdin`, because feeding it nothing is a false pass rather
than a check - see the note on `_READS_STDIN`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

from qwen_cpp_review.verification import verify

#: Words that look like a call but are not, so a self-call check does not fire
#: on `if (...)` inside a function called `if`-something.
_NOT_CALLS = {"if", "for", "while", "switch", "catch", "return", "sizeof", "main"}

_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)


def strip_comments(code: str) -> str:
    """Comments out, before anything reads the code.

    Complexity notes are the reason this is not optional: `//S.C : O(26)` scans as
    a function `O(26){...}` whose body mentions `O(n)`, so a file with no recursion
    in it is reported as recursive. The same class of mistake as scoring a rewrite
    from the word "cache" in a comment - prose being read as code.
    """
    return _COMMENT.sub(" ", code)


_FUNCTION = re.compile(r"(\w+)\s*\(([^;{}]*)\)\s*(?:const\s*)?\{")
#: `function<void(int)> name = [&](...)` - the lambda form used for recursion
#: in a few of the collected samples, which the plain function scan misses.
_LAMBDA = re.compile(r"\b(\w+)\s*=\s*\[[^\]]*\]")


def _body(text: str, start: int) -> str:
    """The braced block beginning at `start`, or the rest of the text if unbalanced."""
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index]
    return text[start:]


def recursive_functions(code: str) -> list[str]:
    """Names of functions that call themselves, including `function<>` lambdas."""
    code = strip_comments(code)
    found = []
    for match in _FUNCTION.finditer(code):
        name = match.group(1)
        if name in _NOT_CALLS:
            continue
        if re.search(rf"\b{re.escape(name)}\s*\(", _body(code, match.end() - 1)):
            found.append(name)
    for match in _LAMBDA.finditer(code):
        name = match.group(1)
        brace = code.find("{", match.end())
        if brace != -1 and re.search(rf"\b{re.escape(name)}\s*\(", _body(code, brace)):
            found.append(name)
    return sorted(set(found))


def load_pairs(directory: Path) -> list[dict[str, str]]:
    """Every pair in the directory, as `{source, code, improved_code, stdin, ...}`.

    Three formats are read. `seed.jsonl` is the one to write new pairs in: real
    JSONL, one object per line, carrying the `stdin` the programs need. The other
    two are the originally collected files, kept readable so nothing is lost. `DATASET.json` is a valid array of
    two-element groups. `dataset.jsonl` is neither JSONL nor valid JSON - its
    records are `{"<code>"}`, a string with no key - so its code is recovered by
    pulling the string literals out in order. Both are read rather than fixed by
    hand so that re-collecting is repeatable.
    """
    pairs: list[dict[str, str]] = []

    seed = directory / "seed.jsonl"
    if seed.exists():
        for line in seed.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                pairs.append({"source": seed.name, **row})

    strict = directory / "DATASET.json"
    if strict.exists():
        for group in json.loads(strict.read_text(encoding="utf-8")):
            if len(group) == 2:
                pairs.append({"source": strict.name, "code": group[0]["code"],
                              "improved_code": group[1]["code"], "stdin": ""})

    loose = directory / "dataset.jsonl"
    if loose.exists():
        literals = re.findall(
            r'\{\s*("(?:[^"\\]|\\.)*")\s*\}', loose.read_text(encoding="utf-8")
        )
        codes = [json.loads(literal) for literal in literals]
        for index in range(0, len(codes) - 1, 2):
            pairs.append({"source": loose.name, "code": codes[index],
                          "improved_code": codes[index + 1], "stdin": ""})

    return pairs


#: `bits/stdc++.h` is a libstdc++ implementation detail that competitive-programming
#: sources use constantly and Apple's libc++ does not ship. Rejecting those samples
#: would be measuring the toolchain rather than the data, so a shim supplies it.
STDCXX_SHIM = """\
#pragma once
#include <algorithm>
#include <bitset>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <climits>
#include <deque>
#include <functional>
#include <iostream>
#include <iomanip>
#include <map>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
"""

#: A program that waits on `cin` cannot be checked without knowing what to type at
#: it. Feeding it nothing does not make it safe to keep: `cin >> n` on end-of-file
#: leaves n at 0 since C++11, so both versions would print nothing, agree, and pass
#: as verified. That is a false pass, which is worse than a rejection.
_READS_STDIN = re.compile(r"\bcin\s*>>|\bgetline\s*\(\s*cin\b|\bscanf\s*\(|\bgets\s*\(")


def make_include_dir(workdir: Path) -> Path:
    include = workdir / "include" / "bits"
    include.mkdir(parents=True, exist_ok=True)
    (include / "stdc++.h").write_text(STDCXX_SHIM, encoding="utf-8")
    return workdir / "include"


def build_and_run(
    code: str, workdir: Path, stem: str, timeout: int, feed: str = ""
) -> tuple[str | None, str]:
    """Return (stdout, "") on success, or (None, reason) on failure."""
    source = workdir / f"{stem}.cpp"
    source.write_text(code, encoding="utf-8")
    binary = workdir / stem

    compiled = subprocess.run(
        ["g++", "-std=c++17", "-w", "-I", str(workdir / "include"), "-o", str(binary), str(source)],
        capture_output=True, text=True, timeout=120,
    )
    if compiled.returncode != 0:
        first = next(
            (line for line in compiled.stderr.splitlines() if ": error:" in line), ""
        )
        return None, f"{stem} does not compile: {first.strip()[:160] or 'unknown error'}"

    try:
        ran = subprocess.run(
            [str(binary)], capture_output=True, text=True,
            input=feed, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, f"{stem} did not finish within {timeout}s"
    if ran.returncode != 0:
        return None, f"{stem} exited with status {ran.returncode}"
    return ran.stdout, ""


def check(
    recursive: str, iterative: str, workdir: Path, timeout: int, feed: str = ""
) -> str | None:
    """Why this pair cannot be used, or None if it is fine."""
    if not recursive_functions(recursive):
        return "the first version is not recursive, so there is nothing to optimise"
    still = recursive_functions(iterative)
    if still:
        return f"the second version still recurses: {', '.join(still)}"
    # A pair with no `main` is not unusable, only un-runnable as written: the
    # LeetCode-shaped `class Solution` snippets are the whole of that bucket.
    # `verification.verify` builds a driver from the function signature and
    # feeds it generated arguments, so the gate stays a gate - both versions are
    # still compiled, run, and compared - and only the entry point is supplied.
    # 20 of the 62 rejections were this, and none of them was a bad rewrite.
    if not all(re.search(r"\bint\s+main\s*\(", code) for code in (recursive, iterative)):
        report = verify(recursive, iterative, timeout=timeout)
        if report.error:
            return f"no main, and no driver could be built: {report.error}"
        if not report.compiled_original:
            return "no main, and the recursive version does not compile"
        if not report.compiled_optimized:
            return "no main, and the iterative version does not compile"
        if not report.equivalent:
            return "the two versions print different output, so the rewrite changed behaviour"
        return None

    for name, code in (("recursive", recursive), ("iterative", iterative)):
        if _READS_STDIN.search(code) and not feed:
            return f"{name} version reads its input from stdin, and no input was recorded with the pair"

    before, problem = build_and_run(recursive, workdir, "recursive", timeout, feed)
    if problem:
        return problem
    after, problem = build_and_run(iterative, workdir, "iterative", timeout, feed)
    if problem:
        return problem
    if before != after:
        return "the two versions print different output, so the rewrite changed behaviour"
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("directory", type=Path)
    parser.add_argument("--timeout", type=int, default=10, help="seconds each program may run")
    args = parser.parse_args()

    pairs = load_pairs(args.directory)
    if not pairs:
        raise SystemExit(f"no pairs found in {args.directory}")
    print(f"{len(pairs)} pairs\n")

    kept: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        make_include_dir(workdir)
        for index, pair in enumerate(pairs):
            feed = pair.get("stdin", "")
            problem = check(pair["code"], pair["improved_code"], workdir, args.timeout, feed)
            label = pair.get("name") or str(index)
            if problem:
                rejected.append({"source": pair["source"], "index": index,
                                 "name": pair.get("name"), "reason": problem})
                print(f"  [{index:>3}] {pair['source']:<14} REJECT  {label}: {problem}")
            else:
                row = {"task": "optimize", "language": "cpp",
                       "code": pair["code"], "improved_code": pair["improved_code"]}
                if feed:
                    row["stdin"] = feed
                for extra in ("name", "kind", "difficulty"):
                    if pair.get(extra):
                        row[extra] = pair[extra]
                kept.append(row)

    out = args.directory / "pairs.jsonl"
    out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in kept), encoding="utf-8"
    )
    (args.directory / "rejected.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rejected), encoding="utf-8"
    )

    print(f"\n{'=' * 72}")
    print(f"verified {len(kept)}/{len(pairs)} pairs -> {out}")
    print(f"rejected {len(rejected)} -> {args.directory / 'rejected.jsonl'}")
    if kept:
        print("\nEach kept row compiles, runs, and prints what the recursive version printed.")


if __name__ == "__main__":
    main()
