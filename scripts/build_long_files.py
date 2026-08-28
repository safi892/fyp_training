"""Synthesise multi-function files, because the corpus has almost none.

The model is reliable in-distribution and unreliable out of it: 1 of 46
explanations carries a false statement on ordinary competitive-programming code,
against **9 of 20** on 45-58 line tree and graph programs. Measured over the
training mixture, the length distribution says why:

    p10 6 · p50 13 · p90 30 · p99 52
    >= 45 lines : 2.2% of rows

The failures happen where there is almost no training signal. The corpus cannot
supply longer files - its rows are single functions, p50 15 lines - so they are
built by concatenating rows that already carry verified anchors.

Concatenation is safe here for a reason worth stating: of the 13,087 anchored
rows, exactly **one** contains `int main()` and 3% contain an `#include`. They
are function bodies, so joining three or four of them produces a plausible
translation-unit rather than two programs stapled together.

**The anchor guarantee is preserved mechanically, not assumed.** Each row's
line numbers are shifted by its offset in the bundle, and every anchor is then
re-checked against the file that was actually written; a bundle with a single
mismatch is discarded rather than emitted. That is the same contract
`build_line_anchored.py` established, and this script would be worthless without
it - a long file whose anchors are wrong teaches the model to invent quotes.

    uv run python scripts/build_long_files.py --min-lines 45 --max-lines 90
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qwen_cpp_review.claim_checks import strip_comments  # noqa: E402

#: A definition, not a call: a name followed by a parameter list and a brace.
#: Used only to refuse bundles that would define the same name twice, so a
#: false positive costs a bundle and a false negative costs a duplicate symbol.
_DEFINITION = re.compile(r"\b(\w+)\s*\([^;{}]*\)\s*(?:const\s*)?\{")

#: Words that open a block without defining anything.
_NOT_DEFINITIONS = frozenset(
    {"if", "for", "while", "switch", "catch", "return", "sizeof", "else", "do"}
)


def defined_names(code: str) -> set[str]:
    return {
        match.group(1)
        for match in _DEFINITION.finditer(strip_comments(code))
        if match.group(1) not in _NOT_DEFINITIONS
    }


def anchors_hold(code: str, anchors: list[dict[str, Any]]) -> bool:
    """Every anchor quotes the line it claims, in the file as written."""
    lines = code.split("\n")
    for anchor in anchors:
        number = anchor.get("line")
        quoted = (anchor.get("code") or "").strip()
        if not isinstance(number, int) or not quoted:
            return False
        if not 1 <= number <= len(lines):
            return False
        if lines[number - 1].strip() != quoted:
            return False
    return True


def bundle(rows: list[dict[str, Any]], separator: str = "\n\n") -> dict[str, Any] | None:
    """One synthesised file, or None if its anchors do not survive the join."""
    parts: list[str] = []
    anchors: list[dict[str, Any]] = []
    offset = 0
    for row in rows:
        code = (row.get("code") or "").rstrip("\n")
        for anchor in row.get("line_comments") or []:
            anchors.append({
                "line": anchor["line"] + offset,
                "code": anchor["code"],
                "comment": anchor["comment"],
            })
        parts.append(code)
        # `count("\n") - 1`, not `count("\n")`: the separator's first newline
        # terminates this part's last line rather than adding one, so "a\nb"
        # joined by "\n\n" to "c" splits as ["a", "b", "", "c"] and c is line 4,
        # not line 5. Getting this wrong shifts every anchor by one per part and
        # the check below discards the whole run, which is how it was found.
        offset += len(code.split("\n")) + separator.count("\n") - 1
    code = separator.join(parts)
    if not anchors_hold(code, anchors):
        return None
    anchors.sort(key=lambda a: a["line"])
    # The row carries exactly the keys the rest of the mixture carries and no
    # others. `datasets.load_dataset` casts a JSONL to one schema and refuses
    # the file outright when a later row introduces a column - "1 new columns
    # ({'synthesised_from'})" - so a provenance field here costs the whole run.
    # The count is reported in the summary instead, where it was the only use.
    return {
        "task": "line_comments",
        "language": "cpp",
        "code": code,
        "line_comments": anchors,
    }


def candidates(path: Path, max_lines: int) -> list[dict[str, Any]]:
    kept = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        anchors = row.get("line_comments") or []
        code = row.get("code") or ""
        if not anchors or not code.strip():
            continue
        if len(code.splitlines()) > max_lines:
            continue
        # The one row with a main, and any with includes, would put a
        # preprocessor line or a second entry point in the middle of a file.
        if re.search(r"\bint\s+main\s*\(|#include", code):
            continue
        kept.append(row)
    return kept


def bundles(
    rows: list[dict[str, Any]], *, min_lines: int, max_lines: int, rng: random.Random
) -> Iterator[tuple[dict[str, Any], int]]:
    """Greedily fill files to `min_lines`, refusing duplicate definitions."""
    pool = rows[:]
    rng.shuffle(pool)
    current: list[dict[str, Any]] = []
    names: set[str] = set()
    lines = 0
    for row in pool:
        code = row.get("code") or ""
        mine = defined_names(code)
        if mine & names:                     # would define the same symbol twice
            continue
        current.append(row)
        names |= mine
        lines += len(code.splitlines()) + 1
        if lines >= min_lines:
            if lines <= max_lines and len(current) > 1:
                built = bundle(current)
                if built is not None:
                    yield built, len(current)
            current, names, lines = [], set(), 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--input", type=Path, default=Path("cleaned/line_anchored.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("cleaned/long_files.jsonl"))
    parser.add_argument("--min-lines", type=int, default=45,
                        help="the length the model starts failing at")
    parser.add_argument("--max-lines", type=int, default=90)
    parser.add_argument("--source-max-lines", type=int, default=25,
                        help="longest single row eligible to be bundled")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rows = candidates(args.input, args.source_max_lines)
    print(f"eligible source rows: {len(rows)} of the anchored corpus")

    pairs = list(bundles(
        rows, min_lines=args.min_lines, max_lines=args.max_lines,
        rng=random.Random(args.seed),
    ))
    built = [row for row, _ in pairs]
    parts = [count for _, count in pairs]
    if not built:
        raise SystemExit("no bundle survived the anchor check")

    # Re-checked here as well as at construction: this is the guarantee the
    # whole file exists to keep, and it costs nothing to assert it twice.
    bad = [b for b in built if not anchors_hold(b["code"], b["line_comments"])]
    if bad:
        raise SystemExit(f"{len(bad)} bundles failed the second anchor check")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in built:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    lengths = sorted(len(b["code"].splitlines()) for b in built)
    anchors = sum(len(b["line_comments"]) for b in built)
    print(f"files written        : {len(built)}")
    print(f"  lines  p50 {lengths[len(lengths) // 2]} · min {lengths[0]} · max {lengths[-1]}")
    print(f"  anchors            : {anchors} (mean {anchors / len(built):.1f}/file)")
    print(f"  functions per file : mean {sum(parts) / len(parts):.1f}")
    print("\nevery anchor quotes the line it claims, in the file as written")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
