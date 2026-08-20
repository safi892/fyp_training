"""Build a verified recursion-to-iteration dataset by generating and throwing most of it away.

The corpus cannot supply this. Of the 736 recursive functions whose signature the
driver can drive, **614 - 83% - carry an `improved_code` that still recurses**.
The targets were written without being executed, so they tidied the code and left
the algorithm alone, and a model trained on them does the same. Filtering the
corpus yields about 55 usable rows, which is not a dataset.

So the rows are generated instead, and the gate decides which ones exist:

    1. take a recursive function from the corpus, with its author's identifiers
    2. ask the model for an iterative version, several times, sampled not greedy
    3. keep an attempt only if it compiles, runs, and prints exactly what the
       original printed on the same generated inputs
    4. everything else is discarded without being looked at

A single attempt succeeds about 17% of the time. That is a poor generator and a
perfectly good *proposer*, because correctness is not being trusted - it is being
tested. Every kept row is executable evidence rather than an opinion, which is
the property the original 19,033 rows never had.

    uv run python scripts/build_optimize_dataset.py --limit 300 --samples 6

Resumable: finished functions are skipped on the next run, so this can be
stopped and restarted without losing work or repeating calls.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from qwen_cpp_review.claim_checks import recursive_functions
from qwen_cpp_review.prompt import TASK_FIELD_HINTS
from qwen_cpp_review.verification import parse_signature, verify

SYSTEM = (
    "You are a senior C++ code review assistant. Produce accurate, structured, "
    "actionable review output for the given source code."
)

#: The wording that measured 10/60 against the shipped 3/60. Read from the
#: registry rather than copied, so the dataset is built with the instruction that
#: will be used to serve it.
WORDING = TASK_FIELD_HINTS["iterate"]["improved_code"]


def build_prompt(code: str) -> str:
    instruction = (
        "Analyze the following C++ code.\n\nLanguage: cpp\n\n"
        f"Generate:\n- Improved code ({WORDING})\n\n"
        "Return a single JSON object using the requested field names."
    )
    return (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\n\n### Code\n\n```cpp\n{code}\n```<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def wait_for_server(port: int, timeout: float = 300.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as response:
                if json.load(response).get("status") == "ok":
                    return
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            pass
        time.sleep(2)
    raise RuntimeError("llama-server did not become ready")


def complete(port: int, prompt: str, n_predict: int, temperature: float, seed: int) -> str:
    """One sample. Temperature is above zero on purpose.

    Greedy decoding gives the same wrong answer every time, so a second attempt
    at the same function would cost a call and add nothing. Sampling is what
    makes several attempts worth making.
    """
    payload = json.dumps({
        "prompt": prompt, "n_predict": n_predict, "temperature": temperature,
        "top_p": 0.95, "seed": seed, "cache_prompt": False,
    }).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)["content"]


def drivable_recursive(corpus: Path, max_lines: int) -> list[str]:
    """Corpus functions that recurse and whose signature the driver can supply."""
    found = []
    for line in corpus.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        code = json.loads(line).get("code") or ""
        if not code.strip() or len(code.splitlines()) > max_lines:
            continue
        if not recursive_functions(code):
            continue
        signature = parse_signature(code)
        if signature is not None and signature.supported:
            found.append(code)
    # De-duplicated: the corpus repeats popular problems, and the same function
    # generated twice is one row of information counted twice.
    return list(dict.fromkeys(found))


def judge(original: str, candidate: str, timeout: float) -> str | None:
    """Why this attempt cannot be kept, or None if it is verified."""
    if not candidate.strip():
        return "empty"
    if recursive_functions(candidate):
        return "still recursive"
    report = verify(original, candidate, timeout=timeout)
    if report.error:
        return f"unchecked: {report.error[:60]}"
    if not report.compiled_optimized:
        return "does not compile"
    if not report.equivalent:
        return "different output"
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--corpus", type=Path, default=Path("cleaned/merged_cleaned.jsonl"))
    parser.add_argument("--out", type=Path,
                        default=Path("my_data_annotation/recursion_optimization/verified.jsonl"))
    parser.add_argument("--limit", type=int, default=300, help="functions to attempt")
    parser.add_argument("--samples", type=int, default=6, help="attempts per function")
    parser.add_argument("--max-lines", type=int, default=40)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8101)
    parser.add_argument("--n-predict", type=int, default=700)
    args = parser.parse_args()

    functions = drivable_recursive(args.corpus, args.max_lines)[: args.limit]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    done: set[str] = set()
    if args.out.exists():
        for line in args.out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                done.add(json.loads(line)["code"])
    attempted = args.out.with_suffix(".attempted.json")
    tried: set[str] = set(json.loads(attempted.read_text())) if attempted.exists() else set()

    todo = [code for code in functions if code not in done and code not in tried]
    print(f"{len(functions)} drivable recursive functions, {len(done)} already verified, "
          f"{len(tried) - len(done)} already failed -> {len(todo)} to attempt")
    if not todo:
        return

    process = subprocess.Popen(
        ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096",
         "-t", "8", "--no-warmup"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    kept = 0
    try:
        wait_for_server(args.port)
        for index, code in enumerate(todo):
            reasons = []
            for sample in range(args.samples):
                text = complete(args.port, build_prompt(code), args.n_predict,
                                args.temperature, seed=sample)
                try:
                    candidate = (json.loads(text) or {}).get("improved_code") or ""
                except json.JSONDecodeError:
                    reasons.append("bad json")
                    continue
                problem = judge(code, candidate, args.timeout)
                if problem is None:
                    with args.out.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps({
                            "task": "iterate", "language": "cpp",
                            "code": code, "improved_code": candidate,
                            "verified": "compiled and ran with identical output",
                            "attempt": sample,
                        }, ensure_ascii=False) + "\n")
                    kept += 1
                    reasons.append("KEPT")
                    break                      # one verified rewrite per function is enough
                reasons.append(problem)
            tried.add(code)
            # Written every function, so a kill does not lose the record of what
            # was already paid for.
            attempted.write_text(json.dumps(sorted(tried)), encoding="utf-8")
            mark = "KEPT" if reasons and reasons[-1] == "KEPT" else reasons[-1] if reasons else "-"
            print(f"  [{index + 1:>4}/{len(todo)}] kept {kept:>4}  {mark}")
    finally:
        process.terminate()
        process.wait(timeout=30)

    print(f"\n{'=' * 72}")
    print(f"verified rows written: {kept}  (total in {args.out}: {len(done) + kept})")
    print("Every row compiled, ran, and printed what the recursive version printed.")


if __name__ == "__main__":
    main()
