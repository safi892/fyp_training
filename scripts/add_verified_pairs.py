"""Fold execution-verified optimisation pairs into the training mixture.

The `improve` task has 18,935 rows whose targets were written by a model and
never run. That is how it came to teach tidying: 99.6% of them claim an
improvement, and nothing checked whether the rewrite still computed the same
answer. Training on them taught the shape of an optimisation rather than one.

These 58 are different. Each was proposed by a 30B teacher, compiled next to
its original, run on generated inputs, and kept only where the outputs matched.
They go in under the `optimize` task rather than joining `improve`, so the two
stay separable at evaluation time - mixing verified rows into an unverified
pile makes the pile look better without making it better.

They are also upsampled, because 58 rows against 66,103 is not a signal. That
is a real risk of memorisation rather than learning, and it is the reason to
re-probe afterwards instead of trusting the loss curve.

    uv run python scripts/add_verified_pairs.py --repeat 5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verified", type=Path, default=Path("test_results/distilled.jsonl"))
    parser.add_argument("--mixture", type=Path, default=Path("cleaned/task_mixture.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("cleaned/task_mixture_verified.jsonl"))
    parser.add_argument(
        "--repeat", type=int, default=5,
        help="Copies of each verified pair. Enough to be seen, few enough that "
             "the model has to generalise rather than recite.",
    )
    args = parser.parse_args()

    pairs = [json.loads(line) for line in args.verified.open(encoding="utf-8")]
    # The teacher can propose the same rewrite for two near-identical
    # submissions; keeping both would upsample it twice over.
    unique = {(p["code"], p["improved_code"]): p for p in pairs}
    print(f"verified pairs: {len(pairs)}  unique: {len(unique)}")

    rows = 0
    with args.out.open("w", encoding="utf-8") as handle:
        for line in args.mixture.open(encoding="utf-8"):
            handle.write(line)
            rows += 1
        for pair in unique.values():
            row = json.dumps({
                "code": pair["code"],
                "language": "cpp",
                "task": "optimize",
                "improved_code": pair["improved_code"],
            }, ensure_ascii=False)
            for _ in range(args.repeat):
                handle.write(row + "\n")
                rows += 1

    added = len(unique) * args.repeat
    print(f"wrote {args.out}: {rows:,} rows ({added} added as task=optimize)")
    print(f"optimize is {added / rows:.2%} of the mixture - re-probe after "
          f"training rather than believing the loss")


if __name__ == "__main__":
    main()
