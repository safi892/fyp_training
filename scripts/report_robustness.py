"""Turn a robustness run into a readable markdown report.

Reads the JSONL written by ``scripts/eval_robustness.py`` and lays out, for
every sample and every renaming, the exact code the model was given and
everything it said back. Generation is the expensive part, so this is a
separate script: the report can be regenerated or restyled without paying for
inference again.

    uv run python scripts/report_robustness.py \
        --input test_results/robustness.jsonl \
        --output test_results/robustness.md
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from qwen_cpp_review.line_anchoring import repair_anchors
from qwen_cpp_review.robustness_samples import SAMPLES

VARIANT_NOTES = {
    "original": "as written, meaningful names",
    "clear": "renamed, still descriptive",
    "terse": "single letters: a, b, x, n",
    "noise": "visually confusing: lllIII, O0OoO0",
    "misleading": "names that suggest the wrong operation",
    "mixed": "half descriptive, half noise",
}


def missed_concepts(text: str, concepts: list[list[str]]) -> list[str]:
    lowered = text.lower()
    return [group[0] for group in concepts if not any(word.lower() in lowered for word in group)]


def anchors_for(record: dict[str, Any]) -> list[Any]:
    """Re-derive the repaired anchors from the raw generation."""
    try:
        parsed = json.loads(record.get("line_comments_raw") or "{}")
    except json.JSONDecodeError:
        return []
    return repair_anchors(record["code"], parsed.get("line_comments") or []).anchors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", default="test_results/robustness.jsonl")
    parser.add_argument("--output", default="test_results/robustness.md")
    parser.add_argument("--title", default="Identifier robustness — model output review")
    args = parser.parse_args()

    records = [json.loads(line) for line in Path(args.input).read_text().splitlines() if line.strip()]
    if not records:
        raise SystemExit(f"no records in {args.input}")

    by_sample: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_sample[record["sample"]].append(record)
    concepts_by_sample = {sample["name"]: sample for sample in SAMPLES}
    variants = list(dict.fromkeys(record["variant"] for record in records))

    out: list[str] = [f"# {args.title}", ""]
    out.append(
        "Every section below is the **same algorithm** with the variables renamed. "
        "If the model understands the code, the comments should say the same thing "
        "in each one."
    )
    out.append("")

    # --- summary ---------------------------------------------------------- #
    out += ["## Summary", "", "| variant | what changed | JSON | anchors kept | concepts | agreement |",
            "| --- | --- | ---: | ---: | ---: | ---: |"]
    baseline = None
    for variant in variants:
        rows = [r for r in records if r["variant"] == variant]
        json_ok = sum(r["line_comments_json_ok"] + r["explanation_json_ok"] for r in rows) / (2 * len(rows))
        kept = sum(r["anchors_kept"] for r in rows)
        total = sum(r["anchors_total"] for r in rows)
        concepts = sum(r["concepts_hit"] for r in rows) / max(1, sum(r["concepts_total"] for r in rows))
        agreement = sum(r["agreement"] for r in rows) / len(rows)
        if variant == "original":
            baseline = concepts
        delta = "" if baseline is None or variant == "original" else f" ({concepts - baseline:+.0%})"
        out.append(
            f"| `{variant}` | {VARIANT_NOTES.get(variant, '')} | {json_ok:.0%} | "
            f"{kept}/{total} | {concepts:.0%}{delta} | {agreement:.2f} |"
        )
    out += ["",
            "**concepts** is the headline: the share of ideas the model named, scored against "
            "words that never appear as identifiers, so a point cannot be earned by echoing a "
            "variable name. **agreement** is word overlap with the same sample's `original` output.",
            ""]

    # --- per sample ------------------------------------------------------- #
    for name, rows in by_sample.items():
        sample = concepts_by_sample.get(name, {})
        out += [f"## {name}", ""]
        if sample:
            wanted = ", ".join(group[0] for group in sample["concepts"])
            out.append(f"*difficulty: {sample.get('difficulty', '?')} — a correct answer should mention: {wanted}*")
            out.append("")

        for record in sorted(rows, key=lambda r: variants.index(r["variant"])):
            variant = record["variant"]
            out += [f"### `{variant}` — {VARIANT_NOTES.get(variant, '')}", ""]
            out += ["**Input**", "", "```cpp"]
            out += [f"{index:>3}  {line}" for index, line in enumerate(record["code"].split("\n"), start=1)]
            out += ["```", ""]

            anchors = anchors_for(record)
            if anchors:
                out += ["**Line-by-line comments**", "", "| line | code | comment |", "| ---: | --- | --- |"]
                for anchor in anchors:
                    code_cell = anchor.code.replace("|", "\\|")
                    comment_cell = anchor.comment.replace("|", "\\|")
                    out.append(f"| {anchor.line} | `{code_cell}` | {comment_cell} |")
                out.append("")
            else:
                out += ["**Line-by-line comments** — none produced "
                        f"(JSON parsed: {record['line_comments_json_ok']})", ""]

            explanation = (record.get("explanation") or "").strip()
            out += ["**Explanation**", ""]
            out += [f"> {line}" for line in (explanation or "_none_").split("\n")]
            out.append("")

            if sample:
                combined = explanation + " " + " ".join(record.get("anchor_comments") or [])
                missed = missed_concepts(combined, sample["concepts"])
                # Recomputed rather than read from the record, so the count and
                # the list of misses can never contradict each other.
                hit = len(sample["concepts"]) - len(missed)
                verdict = f"{hit}/{len(sample['concepts'])} concepts"
                if missed:
                    verdict += f" — missed: {', '.join(missed)}"
                out += [f"*{verdict} · anchors {record['anchors_kept']}/{record['anchors_total']} kept "
                        f"({record['anchors_exact']} exact) · agreement {record['agreement']:.2f}*", ""]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {output_path}  ({len(records)} generations, {len(by_sample)} samples, "
          f"{len(variants)} variants)")


if __name__ == "__main__":
    main()
