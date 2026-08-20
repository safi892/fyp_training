"""Take the cases the probe failed and attack them with harder wordings.

`probe_optimization.py` answers "does a clear instruction find the capability".
Where it says no, there are still two possibilities, and they lead to opposite
decisions:

    the wording was still not explicit enough  ->  keep writing prompts, free
    the capability is not there                ->  build a dataset, a fortnight

So before any dataset is built for a failing case, that case gets one more
round: the same code, asked five more ways, including a worked example. Only a
case that survives all of them has earned training data.

    uv run python scripts/probe_wordings.py --probe test_results/optimization_probe_v3.json

Reads which cases failed from a probe run rather than re-deriving them, so the
two scripts cannot disagree about what "failed" means.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from probe_optimization import (
    SAMPLES,
    SYSTEM,
    classify,
    complete,
    wait_for_server,
)

#: Each wording is a different theory about why the plain request failed.
#: `baseline` repeats what the probe already asked, so any gain is measured
#: against the same model on the same day rather than against a remembered number.
WORDINGS = {
    "baseline": (
        "rewrite this function so it uses a loop instead of calling itself. Keep the same "
        "signature and the same results"
    ),
    # Theory: it knows the parts but not the order to apply them in.
    "numbered_recipe": (
        "rewrite this function iteratively by following these steps exactly:\n"
        "1. create a container to hold the work the recursion would have held\n"
        "2. put the first piece of work into it\n"
        "3. loop while the container is not empty: take one item out, do the work for it, "
        "and put any further work back in\n"
        "4. return the same value the recursive version returned\n"
        "The rewritten function must not call itself"
    ),
    # Theory: it does not connect "remove recursion" to "you need a data structure".
    "name_the_structure": (
        "the call stack is what makes this function work. Replace it with an explicit "
        "std::stack (or std::queue where order allows), declared inside the function. Push the "
        "starting item, then loop while it is not empty, popping one item and pushing the items "
        "the recursive calls would have been made on. Keep the signature and the results identical"
    ),
    # Theory: it needs to be shown the shape once, not told about it.
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
    # Theory: it needs a condition it can check its own answer against.
    "forbid_self_call": (
        "rewrite this function so that the body of the rewritten function contains no call to "
        "the function's own name anywhere. Every other behaviour - the signature, the return "
        "value, the order things are printed - must be unchanged. If you write the function's "
        "own name inside its body, the answer is wrong"
    ),
}


def build_prompt(code: str, wording: str) -> str:
    instruction = (
        "Analyze the following C++ code.\n\nLanguage: cpp\n\n"
        f"Generate:\n- Improved code ({wording})\n\n"
        "Return a single JSON object using the requested field names."
    )
    return (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\n\n### Code\n\n```cpp\n{code}\n```<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def failing_samples(probe: Path) -> list[dict]:
    """Samples whose best wording lost on original names, read from a probe run."""
    records = json.loads(probe.read_text(encoding="utf-8"))
    by_name = {sample["name"]: sample for sample in SAMPLES}
    failed = set()
    for record in records:
        if record.get("strategy") != "original":
            continue
        sample = by_name.get(record["sample"])
        if sample and not record["verdict"].startswith(sample["wants"]):
            failed.add(record["sample"])
    # A sample counts as failed only if no phrasing in the probe ever won on it;
    # one losing phrasing beside a winning one is a wording result, not a wall.
    won = {
        record["sample"]
        for record in records
        if record.get("strategy") == "original"
        and by_name.get(record["sample"])
        and record["verdict"].startswith(by_name[record["sample"]]["wants"])
    }
    return [by_name[name] for name in sorted(failed - won)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--probe", type=Path, default=Path("test_results/optimization_probe_v3.json"))
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8098)
    parser.add_argument("--n-predict", type=int, default=600)
    parser.add_argument("--output", default="test_results/wording_search.json")
    args = parser.parse_args()

    targets = failing_samples(args.probe)
    if not targets:
        raise SystemExit(f"no failing samples in {args.probe} - nothing to attack")
    print(f"{len(targets)} samples that no wording in the probe could fix:")
    for sample in targets:
        print(f"  {sample['name']} ({sample['kind']}, {sample['difficulty']})")

    process = subprocess.Popen(
        ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096",
         "-t", "8", "--no-warmup"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    records = []
    try:
        wait_for_server(args.port)
        for sample in targets:
            print(f"\n=== {sample['name']}  ({sample['kind']}) ===")
            for label, wording in WORDINGS.items():
                text = complete(args.port, build_prompt(sample["code"], wording), args.n_predict)
                try:
                    improved = (json.loads(text) or {}).get("improved_code") or ""
                    parsed = True
                except json.JSONDecodeError:
                    improved, parsed = text, False
                verdict, signals = classify(sample["code"], improved)
                won = verdict.startswith(sample["wants"])
                print(f"  {label:<20} {'PASS' if won else 'fail'}  {verdict:<22} "
                      f"[{', '.join(signals) or 'nothing detected'}]")
                records.append({
                    "sample": sample["name"], "kind": sample["kind"],
                    "difficulty": sample["difficulty"], "wording": label,
                    "verdict": verdict, "won": won, "signals": signals,
                    "json_ok": parsed, "improved_code": improved,
                })
    finally:
        process.terminate()
        process.wait(timeout=30)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"\n{'=' * 72}")
    print("wording                 fixed")
    for label in WORDINGS:
        hits = [r for r in records if r["wording"] == label and r["won"]]
        print(f"  {label:<20}  {len(hits)}/{len(targets)}")

    unfixed = sorted({
        sample["name"] for sample in targets
        if not any(r["won"] for r in records if r["sample"] == sample["name"])
    })
    print(f"\n{len(unfixed)} of {len(targets)} survived every wording: {', '.join(unfixed) or 'none'}")
    print("Those, and only those, are the cases a dataset would have to teach.")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
