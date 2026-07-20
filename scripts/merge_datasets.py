from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def stable_key(row: dict[str, Any]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge JSONL dataset shards into one JSONL file.")
    parser.add_argument(
        "--inputs",
        nargs="+",
        default=[
            "cleaned/results_0_cleaned.jsonl",
            "cleaned/results_1_cleaned.jsonl",
            "cleaned/llm_annotated_cleaned.jsonl",
            "cleaned/llm_annotated_part2_cleaned.jsonl",
        ],
    )
    parser.add_argument("--output", default="cleaned/merged_cleaned.jsonl")
    parser.add_argument("--keep-duplicates", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    total = 0
    written = 0

    with output.open("w", encoding="utf-8") as target:
        for input_path in args.inputs:
            with Path(input_path).open(encoding="utf-8") as source:
                for line_number, line in enumerate(source, start=1):
                    if not line.strip():
                        continue
                    total += 1
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"Invalid JSON in {input_path}:{line_number}") from exc
                    key = stable_key(row)
                    if not args.keep_duplicates and key in seen:
                        continue
                    seen.add(key)
                    target.write(json.dumps(row, ensure_ascii=False) + "\n")
                    written += 1

    print(f"Read {total} rows, wrote {written} rows to {output}")


if __name__ == "__main__":
    main()
