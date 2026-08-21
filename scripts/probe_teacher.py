"""Ask whether a large model can do the transformation ours cannot.

Two runs of `build_optimize_dataset.py` produced 2 verified rows from 130
functions and then 0 from 320 attempts. The generator was the bottleneck, not
the gate: the compile-run-compare check works, it simply had nothing correct to
approve.

So the question is whether a stronger model produces rewrites worth gating. If
it does, distillation is a real route - teacher proposes, our harness verifies,
the small model trains on survivors. If it does not, the task is hard on real
submissions rather than hard for a 1.5B, and the whole line of work ends here
for a defensible reason.

Twenty functions, because that is enough to tell 15/20 from 2/20 and costs an
hour rather than a day. Same corpus, same wording, same verifier as the runs it
is being compared against - only the generator changes.

    uv run python scripts/probe_teacher.py --limit 20
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_optimize_dataset import (
    build_prompt,
    drivable_recursive,
    extract_candidate,
    recursive_call_count,
)

from qwen_cpp_review.verification import verify


def load_provider(path: Path, name: str) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["providers"][name]


def ask_teacher(provider: dict, model: str, prompt: str, budget: int) -> str:
    """One rewrite. The prompt is the product's, so only the model differs."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": budget,
        "reasoning_effort": "medium",
    }).encode()
    request = urllib.request.Request(
        provider["baseUrl"].rstrip("/") + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "api-key": provider["apiKey"]},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)["choices"][0]["message"].get("content") or ""


#: Already carries a table, so there is nothing for memoisation to add.
ALREADY_OPTIMISED = re.compile(r"\b(memo|dp|cache|visited|seen)\b", re.I)


def unchanged(original: str, candidate: str) -> bool:
    """Whitespace-insensitive equality, since a reformat is not a rewrite."""
    squeeze = lambda t: re.sub(r"\s+", " ", t).strip()  # noqa: E731
    return squeeze(original) == squeeze(candidate)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=Path, default=Path(".env"))
    parser.add_argument("--provider", default="azure-saffi")
    parser.add_argument("--model", default="gpt-oss-120b")
    parser.add_argument(
        "--corpus", type=Path,
        default=Path("my_data_annotation/recursion_optimization/inputs.jsonl"))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--max-lines", type=int, default=40)
    parser.add_argument("--budget", type=int, default=6000)
    parser.add_argument("--out", type=Path, default=Path("test_results/teacher_probe.json"))
    args = parser.parse_args()

    provider = load_provider(args.env, args.provider)

    functions = [
        f for f in drivable_recursive(args.corpus, args.max_lines)
        if recursive_call_count(f) >= 2 and not ALREADY_OPTIMISED.search(f)
    ][: args.limit]
    print(f"{len(functions)} un-optimised functions with overlapping subproblems\n")

    records, kept = [], 0
    for position, code in enumerate(functions, start=1):
        try:
            reply = ask_teacher(provider, args.model, build_prompt(code), args.budget)
        except Exception as exc:  # noqa: BLE001 - one bad call must not end the run
            print(f"  [{position:>3}/{len(functions)}] api error: {type(exc).__name__}")
            records.append({"code": code, "verdict": f"api error: {exc}"})
            continue

        candidate = extract_candidate(reply)
        if not candidate:
            verdict = "no code in reply"
        elif unchanged(code, candidate):
            verdict = "returned unchanged"
        else:
            # Deliberately no "still recursive" rejection here. Top-down
            # memoisation *is* recursive - the recursion is kept and a table
            # added - so the check inherited from the `iterate` task rejects
            # precisely the correct answer. Only the verifier decides.
            report = verify(code, candidate)
            verdict = "KEPT" if report.equivalent else (report.error or "output differs")
            kept += report.equivalent

        print(f"  [{position:>3}/{len(functions)}] kept {kept:>3}  {verdict[:58]}")
        records.append({"code": code, "improved_code": candidate, "verdict": verdict})

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"\n{'=' * 66}")
    print(f"verified: {kept}/{len(functions)}   (our 1.5B: 0/20)")
    print("15+ -> distillation is real. ~5 -> marginal. 0-2 -> the task is the problem.")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
