from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from qwen_cpp_review.identifier_augmentation import augment_row


def main() -> None:
    parser = argparse.ArgumentParser(description="Create variable-renaming augmentation for C++ JSONL.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--mode",
        choices=["all", "bad", "descriptive"],
        default="all",
        help="Use all variants or only one augmented naming style.",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    read_rows = 0
    written_rows = 0

    with input_path.open(encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as target:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {input_path}:{line_number}") from exc

            variants = augment_row(row, rng)
            if args.mode == "bad":
                variants = variants[:1] + [
                    item for item in variants[1:] if item.get("augmentation") == "bad_variable_names"
                ]
            elif args.mode == "descriptive":
                variants = variants[:1] + [
                    item for item in variants[1:] if item.get("augmentation") == "descriptive_variable_names"
                ]

            read_rows += 1
            for variant in variants:
                target.write(json.dumps(variant, ensure_ascii=False) + "\n")
                written_rows += 1

    print(f"Read {read_rows} rows, wrote {written_rows} rows to {output_path}")


if __name__ == "__main__":
    main()
