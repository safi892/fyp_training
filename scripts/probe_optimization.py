"""Ask whether the model can already turn recursion into dynamic programming.

Before building a dataset for a capability, it is worth finding out whether the
model has it already and was only being asked badly. The trained `improve`
target was LLM-written and never executed, so it taught tidying rather than
algorithmic change - but the base model underneath has seen a great deal of
real C++, and the instruction may simply have been too vague.

Each recursive sample is sent with several phrasings, from the vague wording
the model was trained on to an explicit request for memoisation. The output is
classified by what it actually contains, not by whether it looks improved.

    uv run python scripts/probe_optimization.py --gguf models/gguf/qwen-cpp-review-q4_k_m.gguf

Runs against llama-server, so this takes minutes rather than hours.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

#: Recursive functions with overlapping subproblems - the case where turning
#: recursion into a table changes the complexity class. Grid traversal and
#: backtracking are deliberately excluded: recursion is the right answer there,
#: and an explicit stack is worse code, not better.
SAMPLES = [
    {
        "name": "fibonacci",
        "code": "int fib(int n)\n{\n  if (n <= 1)\n    return n;\n  return fib(n - 1) + fib(n - 2);\n}",
        "naive": "O(2^n)",
    },
    {
        "name": "grid_paths",
        "code": (
            "int paths(int rows, int cols)\n"
            "{\n"
            "  if (rows == 1 || cols == 1)\n"
            "    return 1;\n"
            "  return paths(rows - 1, cols) + paths(rows, cols - 1);\n"
            "}"
        ),
        "naive": "O(2^(n+m))",
    },
    {
        "name": "coin_change",
        "code": (
            "int ways(int coins[], int count, int amount)\n"
            "{\n"
            "  if (amount == 0)\n"
            "    return 1;\n"
            "  if (amount < 0 || count == 0)\n"
            "    return 0;\n"
            "  return ways(coins, count - 1, amount) + ways(coins, count, amount - coins[count - 1]);\n"
            "}"
        ),
        "naive": "O(2^n)",
    },
]

PHRASINGS = {
    "trained_wording": "Generate:\n- Improved code",
    "explicit_faster": "Generate:\n- Improved code (make it asymptotically faster; do not merely reformat)",
    "explicit_memo": (
        "Generate:\n- Improved code (this function recomputes the same subproblems many times. "
        "Rewrite it to store results so each subproblem is solved once, using memoisation or a "
        "dynamic-programming table. Keep the same signature and behaviour.)"
    ),
}

SYSTEM = (
    "You are a senior C++ code review assistant. Produce accurate, structured, "
    "actionable review output for the given source code."
)


def build_prompt(code: str, generate_block: str) -> str:
    instruction = (
        "Analyze the following C++ code.\n\nLanguage: cpp\n\n"
        f"{generate_block}\n\nReturn a single JSON object using the requested field names."
    )
    return (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\n\n### Code\n\n```cpp\n{code}\n```<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def classify(original: str, improved: str) -> tuple[str, list[str]]:
    """Say what the rewrite actually did, in terms that can be checked."""
    signals = []
    name_match = re.search(r"\b\w+\s+(\w+)\s*\(", original)
    name = name_match.group(1) if name_match else None

    still_recursive = bool(name) and len(re.findall(rf"\b{re.escape(name)}\s*\(", improved)) > 1
    has_table = bool(re.search(r"\b(memo|dp|cache|table|vector\s*<|map\s*<|unordered_map)", improved, re.I))
    has_loop = bool(re.search(r"\b(for|while)\s*\(", improved))
    has_static = bool(re.search(r"\bstatic\b", improved))

    if has_table:
        signals.append("stores results")
    if has_loop:
        signals.append("has a loop")
    if still_recursive:
        signals.append("still recursive")
    if has_static:
        signals.append("static storage")

    if has_table and still_recursive:
        return "MEMOISED (top-down)", signals
    if has_table and has_loop and not still_recursive:
        return "TABULATED (bottom-up)", signals
    if has_loop and not still_recursive:
        return "ITERATIVE (no table)", signals
    if still_recursive:
        return "unchanged algorithm", signals
    return "unclear", signals


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


def complete(port: int, prompt: str, n_predict: int) -> str:
    payload = json.dumps(
        {"prompt": prompt, "n_predict": n_predict, "temperature": 0, "cache_prompt": False}
    ).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)["content"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8097)
    parser.add_argument("--n-predict", type=int, default=450)
    parser.add_argument("--output", default="test_results/optimization_probe.json")
    args = parser.parse_args()

    process = subprocess.Popen(
        ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096", "-t", "8", "--no-warmup"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    records = []
    try:
        wait_for_server(args.port)
        for sample in SAMPLES:
            print(f"\n=== {sample['name']}  (naive {sample['naive']}) ===")
            for label, block in PHRASINGS.items():
                text = complete(args.port, build_prompt(sample["code"], block), args.n_predict)
                try:
                    improved = (json.loads(text) or {}).get("improved_code") or ""
                    parsed = True
                except json.JSONDecodeError:
                    improved, parsed = text, False
                verdict, signals = classify(sample["code"], improved)
                print(f"  {label:<18} -> {verdict:<22} [{', '.join(signals) or 'nothing detected'}]")
                records.append(
                    {"sample": sample["name"], "phrasing": label, "verdict": verdict,
                     "signals": signals, "json_ok": parsed, "improved_code": improved}
                )
    finally:
        process.terminate()
        process.wait(timeout=30)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(records, indent=2), encoding="utf-8")

    wins = [r for r in records if r["verdict"].startswith(("MEMOISED", "TABULATED"))]
    print(f"\n{'=' * 72}")
    print(f"rewrites that actually changed the algorithm: {len(wins)}/{len(records)}")
    for phrasing in PHRASINGS:
        hits = [r for r in wins if r["phrasing"] == phrasing]
        print(f"  {phrasing:<18} {len(hits)}/{len(SAMPLES)}")
    print("\nIf the explicit phrasing wins, the capability is there and the")
    print("instruction was the problem. If nothing wins, it needs training data.")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
