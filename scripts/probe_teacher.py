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
import time
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


class RateLimiter:
    """Space calls out, because the free tiers here allow ten a minute.

    Sleeping between requests is cheaper than being throttled: a 429 costs the
    call *and* the wait, and a long unattended run that trips it repeatedly
    finishes with a fraction of the rows it should have.
    """

    def __init__(self, per_minute: int):
        self.gap = 60.0 / max(1, per_minute)
        self.last = 0.0

    def wait(self) -> None:
        pause = self.gap - (time.monotonic() - self.last)
        if pause > 0:
            time.sleep(pause)
        self.last = time.monotonic()


def ask_teacher(provider: dict, model: str, prompt: str, budget: int,
                limiter: RateLimiter, retries: int = 6) -> str:
    """One rewrite. The prompt is the product's, so only the model differs.

    Azure authenticates with an ``api-key`` header and NVIDIA with a bearer
    token, so the provider config decides. Retries exist because a run of three
    hundred functions will meet a transient 429 or 503, and losing the row for
    it wastes the whole call.
    """
    headers = {"Content-Type": "application/json"}
    if "azure" in provider["baseUrl"]:
        headers["api-key"] = provider["apiKey"]
    else:
        headers["Authorization"] = f"Bearer {provider['apiKey']}"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "top_p": 0.95,
    }
    # Azure reasoning models want max_completion_tokens; the rest want max_tokens.
    payload["max_completion_tokens" if "azure" in provider["baseUrl"] else "max_tokens"] = budget

    last = ""
    for attempt in range(retries):
        limiter.wait()
        try:
            request = urllib.request.Request(
                provider["baseUrl"].rstrip("/") + "/chat/completions",
                data=json.dumps(payload).encode(), headers=headers,
            )
            with urllib.request.urlopen(request, timeout=600) as response:
                message = json.load(response)["choices"][0]["message"]
            # Some models put the answer in `content` and their working in
            # `reasoning_content`; others run them together. Prefer the clean one.
            return message.get("content") or message.get("reasoning_content") or ""
        except Exception as exc:  # noqa: BLE001 - retried, then reported
            last = f"{type(exc).__name__}: {exc}"
            # Up to ~64s on the last attempt, which rides out a brief drop
            # rather than discarding a function the run has already paid for.
            time.sleep(min(64, 2 ** attempt))
    raise RuntimeError(last)


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
    parser.add_argument("--task", choices=("optimize", "iterate"), default="optimize")
    parser.add_argument(
        "--min-calls", type=int, default=2,
        help="2 for memoisation, which needs overlapping subproblems. 1 to reach "
             "the linear recursion that can only become a loop.",
    )
    parser.add_argument("--max-calls", type=int, default=99)
    parser.add_argument("--max-lines", type=int, default=40)
    parser.add_argument("--budget", type=int, default=6000)
    parser.add_argument("--out", type=Path, default=Path("test_results/teacher_probe.json"))
    parser.add_argument("--rate", type=int, default=10, help="requests per minute")
    parser.add_argument("--verified", type=Path, default=None,
                        help="Append kept pairs here as JSONL, for training on.")
    args = parser.parse_args()

    provider = load_provider(args.env, args.provider)
    limiter = RateLimiter(args.rate)

    # Resume: a run of three hundred takes hours and will be interrupted.
    done = set()
    if args.verified and args.verified.exists():
        done = {json.loads(line)["code"] for line in args.verified.open(encoding="utf-8")}
        print(f"{len(done)} already verified, skipping those")

    functions = [
        f for f in drivable_recursive(args.corpus, args.max_lines)
        if args.min_calls <= recursive_call_count(f) <= args.max_calls
        and not ALREADY_OPTIMISED.search(f)
    ]
    functions = [f for f in functions if f not in done][: args.limit]
    print(f"{len(functions)} functions, {args.min_calls}-{args.max_calls} "
          f"recursive calls, task={args.task}\n")

    records, kept = [], 0
    for position, code in enumerate(functions, start=1):
        try:
            reply = ask_teacher(
                provider, args.model, build_prompt(code, args.task), args.budget, limiter)
        except Exception as exc:  # noqa: BLE001 - one bad call must not end the run
            print(f"  [{position:>3}/{len(functions)}] api error: {type(exc).__name__}", flush=True)
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
            if report.equivalent and args.verified:
                args.verified.parent.mkdir(parents=True, exist_ok=True)
                with args.verified.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({
                        "task": args.task, "language": "cpp",
                        "code": code, "improved_code": candidate,
                        "verified": "compiled and ran with identical output",
                        "teacher": args.model,
                    }, ensure_ascii=False) + "\n")

        print(f"  [{position:>3}/{len(functions)}] kept {kept:>3}  {verdict[:58]}", flush=True)
        records.append({"code": code, "improved_code": candidate, "verdict": verdict})
        # Rewritten every time: a long unattended run that dies at hour two
        # should still have everything it learned in hour one.
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(records, indent=2), encoding="utf-8")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"\n{'=' * 66}")
    print(f"verified: {kept}/{len(functions)}   (our 1.5B: 0/20)")
    print("15+ -> distillation is real. ~5 -> marginal. 0-2 -> the task is the problem.")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
