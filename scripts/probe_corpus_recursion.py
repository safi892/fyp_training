"""Run the recursion-to-loop question on real submissions instead of written samples.

`probe_optimization.py` asks the question on seventeen functions written for the
purpose, with identifiers this project renamed on purpose. That answers "can the
model do this", and it cannot answer "will it do this for a user", because both
the code and the names are ours.

This asks the same question of code nobody here wrote: the self-calling functions
already in `cleaned/merged_cleaned.jsonl`, kept exactly as their authors typed
them. 2,516 of the 19,033 rows contain one. Their names are whatever a real
submission happened to use, which is the condition serving actually runs in, and
the only condition a claim about serving can be based on.

    uv run python scripts/probe_corpus_recursion.py --limit 60

Shape is decided by counting how many times a function calls itself, because that
is the split the written-sample probe found and it is the part that can be
counted rather than judged:

    one self-call     linear      - a running variable can replace the stack
    two or more       branching   - the stack holds work, and needs a container

Branching is not split further into "needs a table" and "needs a container" here.
Telling those apart means deciding whether subproblems overlap, which is not
something a regular expression can do, and guessing it would put an unverifiable
label on every number below.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
from pathlib import Path

from probe_optimization import SYSTEM, classify, complete, wait_for_server
from verify_optimization_pairs import _FUNCTION, _NOT_CALLS, _body, recursive_functions

#: The two wordings that won the wording search on written samples, plus the
#: instruction the model was trained on as the control. Anything that did not win
#: there is not worth spending real-corpus calls on.
WORDINGS = {
    "trained_wording": "",
    "name_the_structure": (
        "the call stack is what makes this function work. Replace it with an explicit "
        "std::stack (or std::queue where order allows), declared inside the function. Push the "
        "starting item, then loop while it is not empty, popping one item and pushing the items "
        "the recursive calls would have been made on. Keep the signature and the results identical"
    ),
    "worked_example": (
        "here is the transformation, applied to a different function:\n\n"
        "BEFORE:\n"
        "void walk(Node* n) { if (!n) return; use(n); walk(n->left); walk(n->right); }\n\n"
        "AFTER:\n"
        "void walk(Node* n) {\n"
        "  if (!n) return;\n"
        "  std::stack<Node*> pending; pending.push(n);\n"
        "  while (!pending.empty()) {\n"
        "    Node* c = pending.top(); pending.pop();\n"
        "    use(c);\n"
        "    if (c->right) pending.push(c->right);\n"
        "    if (c->left) pending.push(c->left);\n"
        "  }\n"
        "}\n\n"
        "Apply the same transformation to the function below. Keep its signature and results"
    ),
}


def self_call_count(code: str) -> int:
    """The most times any one function in `code` calls itself."""
    best = 0
    for match in _FUNCTION.finditer(code):
        name = match.group(1)
        if name in _NOT_CALLS:
            continue
        body = _body(code, match.end() - 1)
        best = max(best, len(re.findall(rf"\b{re.escape(name)}\s*\(", body)))
    return best


def shape(code: str) -> str:
    return "linear" if self_call_count(code) == 1 else "branching"


def build_prompt(code: str, wording: str) -> str:
    asked = f"Generate:\n- Improved code{f' ({wording})' if wording else ''}"
    instruction = (
        "Analyze the following C++ code.\n\nLanguage: cpp\n\n"
        f"{asked}\n\nReturn a single JSON object using the requested field names."
    )
    return (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\n\n### Code\n\n```cpp\n{code}\n```<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def load_samples(corpus: Path, limit: int, seed: int, max_lines: int) -> list[dict]:
    """Real recursive submissions, balanced across the two shapes."""
    buckets: dict[str, list[dict]] = {"linear": [], "branching": []}
    for line in corpus.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        code = row.get("code") or ""
        if len(code.splitlines()) > max_lines or not recursive_functions(code):
            continue
        buckets[shape(code)].append(code)

    rng = random.Random(seed)
    picked = []
    for name, codes in buckets.items():
        rng.shuffle(codes)
        for code in codes[: limit // 2]:
            picked.append({"shape": name, "code": code})
    return picked


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--corpus", type=Path, default=Path("cleaned/merged_cleaned.jsonl"))
    parser.add_argument("--limit", type=int, default=60, help="samples, split evenly by shape")
    parser.add_argument("--max-lines", type=int, default=40)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8100)
    parser.add_argument("--n-predict", type=int, default=600)
    parser.add_argument("--output", default="test_results/corpus_recursion.json")
    args = parser.parse_args()

    samples = load_samples(args.corpus, args.limit, args.seed, args.max_lines)
    counts = {s: sum(1 for x in samples if x["shape"] == s) for s in ("linear", "branching")}
    print(f"{len(samples)} real recursive submissions: "
          f"{counts['linear']} linear, {counts['branching']} branching")
    print("Identifiers are whatever the author wrote - nothing here is renamed.\n")

    process = subprocess.Popen(
        ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096",
         "-t", "8", "--no-warmup"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    records = []
    try:
        wait_for_server(args.port)
        for index, sample in enumerate(samples):
            marks = []
            for label, wording in WORDINGS.items():
                text = complete(args.port, build_prompt(sample["code"], wording), args.n_predict)
                try:
                    improved = (json.loads(text) or {}).get("improved_code") or ""
                    parsed = True
                except json.JSONDecodeError:
                    improved, parsed = text, False
                verdict, signals = classify(sample["code"], improved)
                # Any rewrite that stopped recursing counts, whichever route it took.
                won = verdict.startswith(("ITERATIVE", "TABULATED"))
                marks.append(f"{label[:4]}:{'Y' if won else '.'}")
                records.append({
                    "index": index, "shape": sample["shape"], "wording": label,
                    "verdict": verdict, "won": won, "signals": signals,
                    "json_ok": parsed, "code": sample["code"], "improved_code": improved,
                })
            print(f"  [{index:>3}] {sample['shape']:<10} {'  '.join(marks)}")
    finally:
        process.terminate()
        process.wait(timeout=30)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"\n{'=' * 72}")
    print(f"  {'wording':<20}{'overall':<12}{'linear':<12}{'branching':<12}")
    for label in WORDINGS:
        rows = [r for r in records if r["wording"] == label]
        cells = ""
        for group in ("linear", "branching"):
            part = [r for r in rows if r["shape"] == group]
            cells += f"{sum(r['won'] for r in part)}/{len(part):<10}"
        print(f"  {label:<20}{sum(r['won'] for r in rows)}/{len(rows):<10}{cells}")
    print("\nThese are real submissions with their authors' own identifiers, so this")
    print("is the number that describes serving. The written-sample probe cannot.")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
