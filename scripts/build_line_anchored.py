"""Rebuild the review dataset with verified line-anchored comments.

Reads the merged JSONL, realigns each row's ``comments`` field onto the original
source lines, and writes rows that pass validation to ``--output``. Rows whose
annotated copy drifted too far from the input go to ``--rejected`` instead of
being lost, so the rejection threshold can be retuned without re-running the
alignment.

The input file is never modified.

    uv run python scripts/build_line_anchored.py \
        --input cleaned/merged_cleaned.jsonl \
        --output cleaned/line_anchored.jsonl \
        --rejected cleaned/line_anchored_rejected.jsonl
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from qwen_cpp_review.line_anchoring import anchor_comments

#: Complexity labels claimed by the annotator far more often than a dataset of
#: short competitive-programming snippets can support. Rows carrying these are
#: flagged, not dropped: the label may be right, but it should not be trusted
#: without review.
SUSPECT_COMPLEXITY = {"O(n³)", "O(n^3)", "O(n² log n)", "O(n²log n)"}


def quality_flags(row: dict[str, Any], min_confidence: float) -> list[str]:
    """Report complexity labels that should not be trained on unchecked."""
    flags: list[str] = []
    analysis = row.get("complexity_analysis")
    if not isinstance(analysis, dict):
        flags.append("missing_complexity")
        return flags

    confidence = analysis.get("confidence")
    if isinstance(confidence, (int, float)) and confidence < min_confidence:
        flags.append("low_complexity_confidence")
    if analysis.get("time") in SUSPECT_COMPLEXITY:
        flags.append("suspect_time_complexity")
    if not analysis.get("time") or not analysis.get("space"):
        flags.append("incomplete_complexity")
    return flags


def build_row(row: dict[str, Any], min_confidence: float) -> tuple[dict[str, Any], bool, str]:
    """Return ``(row_with_anchors, passed, reason)`` for one dataset row."""
    result = anchor_comments(row.get("code") or "", row.get("comments") or "")

    enriched = dict(row)
    enriched["line_comments"] = [anchor.to_dict() for anchor in result.anchors]
    enriched["line_comment_quality"] = {
        "match_ratio": round(result.match_ratio, 4),
        "coverage": round(result.coverage, 4),
        "anchored": result.anchored,
        "dropped": result.dropped,
    }
    enriched["quality_flags"] = quality_flags(row, min_confidence)
    return enriched, True, ""


def classify(
    enriched: dict[str, Any],
    *,
    min_match_ratio: float,
    min_anchors: int,
    min_coverage: float,
) -> str:
    """Return an empty string when the row passes, otherwise the reason."""
    quality = enriched["line_comment_quality"]
    if quality["anchored"] == 0:
        return "no_anchors"
    if quality["anchored"] < min_anchors:
        return "too_few_anchors"
    if quality["match_ratio"] < min_match_ratio:
        return "annotated_code_drifted"
    if quality["coverage"] < min_coverage:
        return "low_coverage"
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", default="cleaned/merged_cleaned.jsonl")
    parser.add_argument("--output", default="cleaned/line_anchored.jsonl")
    parser.add_argument("--rejected", default=None, help="Optional path for rows that fail validation.")
    parser.add_argument(
        "--min-match-ratio",
        type=float,
        default=0.6,
        help="Minimum share of annotated code lines that must exist in the input.",
    )
    parser.add_argument("--min-anchors", type=int, default=2, help="Minimum anchored comments per row.")
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=0.0,
        help="Minimum share of original code lines carrying a comment.",
    )
    parser.add_argument(
        "--min-complexity-confidence",
        type=float,
        default=0.7,
        help="Complexity confidence below this is flagged, not dropped.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path = Path(args.rejected) if args.rejected else None

    reasons: Counter[str] = Counter()
    flags: Counter[str] = Counter()
    kept = 0
    total = 0
    anchors_kept = 0
    dropped_comments = 0
    match_ratios: list[float] = []
    coverages: list[float] = []

    rejected_file = rejected_path.open("w", encoding="utf-8") if rejected_path else None
    try:
        with input_path.open(encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as target:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {input_path}:{line_number}") from exc

                total += 1
                enriched, _, _ = build_row(row, args.min_complexity_confidence)
                for flag in enriched["quality_flags"]:
                    flags[flag] += 1

                reason = classify(
                    enriched,
                    min_match_ratio=args.min_match_ratio,
                    min_anchors=args.min_anchors,
                    min_coverage=args.min_coverage,
                )
                if reason:
                    reasons[reason] += 1
                    if rejected_file:
                        enriched["rejection_reason"] = reason
                        rejected_file.write(json.dumps(enriched, ensure_ascii=False) + "\n")
                    continue

                quality = enriched["line_comment_quality"]
                kept += 1
                anchors_kept += quality["anchored"]
                dropped_comments += quality["dropped"]
                match_ratios.append(quality["match_ratio"])
                coverages.append(quality["coverage"])
                target.write(json.dumps(enriched, ensure_ascii=False) + "\n")
    finally:
        if rejected_file:
            rejected_file.close()

    def mean(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    print(f"read              {total}")
    print(f"kept              {kept} ({kept / total:.1%})" if total else "kept 0")
    print(f"rejected          {total - kept}")
    for reason, count in reasons.most_common():
        print(f"  {reason:<24} {count}")
    print(f"anchors kept      {anchors_kept} (mean {anchors_kept / kept:.1f}/row)" if kept else "anchors kept 0")
    print(f"comments dropped  {dropped_comments} (sat on lines absent from the input)")
    print(f"mean match_ratio  {mean(match_ratios):.3f}")
    print(f"mean coverage     {mean(coverages):.3f}")
    if flags:
        print("quality flags (kept + rejected):")
        for flag, count in flags.most_common():
            print(f"  {flag:<28} {count}")
    print(f"\nwrote {output_path}")
    if rejected_path:
        print(f"wrote {rejected_path}")


if __name__ == "__main__":
    main()
