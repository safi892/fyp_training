"""Build the task-tagged training mixture from the line-anchored dataset.

One source row can serve several tasks, so it is emitted once per task it can
supply, each copy tagged with a ``task`` key that `prompt.py` resolves into an
output-field list. Splitting the corpus this way recovers the ~5.9k rows the
anchoring pass rejected: they lack usable line comments but almost all still
carry a usable explanation.

    uv run python scripts/build_task_mixture.py

Reads ``cleaned/line_anchored.jsonl`` and ``cleaned/line_anchored_rejected.jsonl``
(both produced by ``scripts/build_line_anchored.py``) and writes
``cleaned/task_mixture.jsonl``.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

from qwen_cpp_review.prompt import TASKS, build_messages

#: Fields copied onto every emitted row regardless of task.
CARRIED = ("code", "language")

#: Complexity targets carrying any of these flags are not trained on. The label
#: may still be correct, but it has not been checked, and a wrong complexity is
#: worse than no complexity.
COMPLEXITY_BLOCKING_FLAGS = {
    "low_complexity_confidence",
    "suspect_time_complexity",
    "incomplete_complexity",
    "missing_complexity",
}


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path}:{line_number}") from exc


def emit_tasks(row: dict[str, Any], *, min_anchors: int) -> Iterator[dict[str, Any]]:
    """Yield one tagged copy of ``row`` per task it can supply a target for."""
    base = {key: row[key] for key in CARRIED if key in row}
    flags = set(row.get("quality_flags") or ())

    anchors = row.get("line_comments") or []
    if len(anchors) >= min_anchors:
        yield {**base, "task": "line_comments", "line_comments": anchors}

    explanation = (row.get("explanation") or "").strip()
    if explanation:
        yield {**base, "task": "explanation", "explanation": explanation}

    analysis = row.get("complexity_analysis")
    if isinstance(analysis, dict) and not (flags & COMPLEXITY_BLOCKING_FLAGS):
        # `confidence` is annotator metadata, not part of the answer.
        target = {key: analysis[key] for key in ("time", "space") if key in analysis}
        yield {**base, "task": "complexity", "complexity_analysis": target}

    improved = (row.get("improved_code") or "").strip()
    if improved and improved != (row.get("code") or "").strip():
        yield {**base, "task": "improve", "improved_code": improved}


def load_length_filter(tokenizer_name: str, max_tokens: int):
    """Return ``row -> bool`` keeping rows that fit, or ``None`` if unavailable.

    A target longer than ``max_seq_length`` is truncated by the trainer, which
    teaches the model to emit JSON that never closes. Dropping those rows is
    cheaper than the bad habit. If the tokenizer cannot be loaded (no network,
    no cache) the filter is skipped rather than failing the build.
    """
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    except Exception as exc:  # noqa: BLE001 - any failure means "filter unavailable"
        print(f"warning: length filter disabled, could not load {tokenizer_name} ({type(exc).__name__}: {exc})")
        return None

    def fits(row: dict[str, Any]) -> bool:
        text = "\n".join(message["content"] for message in build_messages(row, []))
        return len(tokenizer(text, add_special_tokens=False).input_ids) <= max_tokens

    return fits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--inputs",
        nargs="+",
        default=["cleaned/line_anchored.jsonl", "cleaned/line_anchored_rejected.jsonl"],
    )
    parser.add_argument("--output", default="cleaned/task_mixture.jsonl")
    parser.add_argument(
        "--min-anchors",
        type=int,
        default=2,
        help="Rows with fewer anchored comments do not get a line_comments target.",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=None,
        help=f"Restrict the mixture to these tasks. Known: {sorted(TASKS)}",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Drop rows whose rendered prompt exceeds this. Match data.max_seq_length. 0 disables.",
    )
    parser.add_argument("--tokenizer", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument(
        "--fraction",
        type=float,
        default=1.0,
        help=(
            "Keep this share of each task, sampled deterministically. Task proportions are "
            "preserved, so 0.5 is half of every task rather than half the file."
        ),
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for --fraction sampling.")
    args = parser.parse_args()

    if not 0 < args.fraction <= 1:
        raise SystemExit(f"--fraction must be in (0, 1]; got {args.fraction}")

    wanted = set(args.tasks) if args.tasks else None
    if wanted and not wanted <= set(TASKS):
        raise SystemExit(f"Unknown tasks: {sorted(wanted - set(TASKS))}. Known: {sorted(TASKS)}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fits = load_length_filter(args.tokenizer, args.max_tokens) if args.max_tokens else None

    # Sample per task rather than per file: the tasks are not evenly distributed
    # across the inputs, so truncating the file would drop whole task/annotation
    # styles. A seeded counter keeps this reproducible without holding the
    # mixture in memory.
    rng = random.Random(args.seed)
    # One accumulator per task, started at a random phase so the tasks do not
    # all keep the same positions. Adding `fraction` and taking whole units out
    # keeps exactly that share, evenly spread through the file.
    budget = {task: rng.random() for task in TASKS}

    def keep(task: str) -> bool:
        if args.fraction >= 1.0:
            return True
        budget[task] += args.fraction
        if budget[task] >= 1.0:
            budget[task] -= 1.0
            return True
        return False

    counts: Counter[str] = Counter()
    sampled_out: Counter[str] = Counter()
    too_long: Counter[str] = Counter()
    source_rows = 0
    written = 0

    with output_path.open("w", encoding="utf-8") as target:
        for input_path in args.inputs:
            for row in read_jsonl(Path(input_path)):
                source_rows += 1
                for tagged in emit_tasks(row, min_anchors=args.min_anchors):
                    if wanted and tagged["task"] not in wanted:
                        continue
                    if not keep(tagged["task"]):
                        sampled_out[tagged["task"]] += 1
                        continue
                    if fits and not fits(tagged):
                        too_long[tagged["task"]] += 1
                        continue
                    counts[tagged["task"]] += 1
                    written += 1
                    target.write(json.dumps(tagged, ensure_ascii=False) + "\n")

    print(f"source rows   {source_rows}")
    print(f"training rows {written} ({written / source_rows:.2f} per source row)")
    for task, count in counts.most_common():
        notes = []
        if sampled_out[task]:
            notes.append(f"{sampled_out[task]} not sampled")
        if too_long[task]:
            notes.append(f"{too_long[task]} over {args.max_tokens} tokens")
        suffix = f"   (dropped: {', '.join(notes)})" if notes else ""
        print(f"  {task:<16} {count}{suffix}")
    if args.fraction < 1.0:
        print(f"\nfraction {args.fraction}: kept {written} of {written + sum(sampled_out.values())} rows")
    print(f"\nwrote {output_path}")


if __name__ == "__main__":
    main()
