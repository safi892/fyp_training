"""Put the fine-tuned checkpoint next to the model it was trained from.

Every evaluation in this project measured the trained adapter. None measured
what the base model does on the same inputs, which leaves the central claim -
that fine-tuning bought something - asserted rather than shown. It is the first
question an examiner asks and the harness to answer it already existed; only
the run was missing.

The comparison is clean because the prompt is identical. Both models share a
tokenizer and a chat template, and ``eval_hard.py`` renders the prompt from the
package rather than retyping it, so the only variable is the weights.

Two columns matter and they are not the same column:

- **format**  - valid JSON, anchors that survive checking. This is what
  fine-tuning on a rigid output schema should buy, and where the base model is
  expected to struggle.
- **content** - problems named, false claims made. This is comprehension, which
  comes from pretraining, and where the fine-tune may well have bought nothing.

Reporting them separately is the point. A single averaged score would hide
exactly the distinction this project exists to make.

    uv run python scripts/report_ablation.py \
        --base test_results/hard_examples_base.json \
        --tuned test_results/hard_examples.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from qwen_cpp_review.line_anchoring import repair_anchors  # noqa: E402


def load(path: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    # `eval_hard` writes a bare list; `probe_defects` wraps it. Accept both so a
    # mistyped path fails loudly rather than reporting zeros.
    if isinstance(payload, dict):
        payload = payload.get("rows", [])
    if not isinstance(payload, list) or not payload:
        raise SystemExit(f"{path} holds no results")
    return payload


def anchor_counts(record: dict[str, Any]) -> tuple[int, int]:
    """How many anchors the model offered, and how many survive checking.

    Recomputed from the saved generation rather than read from the record:
    ``eval_hard`` stores the raw text and scores the prose, so the anchor tally
    is not in the file. Deriving it here keeps that harness unchanged and means
    the number comes from the same repair the product runs, not a second
    implementation of it that could disagree with it.
    """
    if "anchors_proposed" in record:
        return record["anchors_proposed"], record.get("anchors_kept", 0)

    raw = (record.get("raw") or {}).get("line_comments", "")
    try:
        proposed = (json.loads(raw) or {}).get("line_comments") or []
    except (json.JSONDecodeError, AttributeError):
        return 0, 0
    proposed = [a for a in proposed if isinstance(a, dict)]
    if not proposed:
        return 0, 0
    return len(proposed), len(repair_anchors(record["code"], proposed).anchors)


def totals(records: list[dict[str, Any]]) -> dict[str, Any]:
    counted = [anchor_counts(r) for r in records]
    return {
        "samples": len(records),
        "json_ok": sum(1 for r in records if r.get("json_ok")),
        "anchors_proposed": sum(p for p, _ in counted),
        "anchors_kept": sum(k for _, k in counted),
        "found": sum(r.get("found", 0) for r in records),
        "of": sum(r.get("of", 0) for r in records),
        "false_claims": sum(1 for r in records if r.get("false_claim")),
    }


def pct(part: int, whole: int) -> str:
    return "—" if not whole else f"{part / whole:.0%}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base", required=True, help="results from the untuned model")
    parser.add_argument("--tuned", required=True, help="results from the trained checkpoint")
    parser.add_argument("--output", default="test_results/ablation.md")
    args = parser.parse_args()

    base = totals(load(args.base))
    tuned = totals(load(args.tuned))
    n = tuned["samples"]

    rows = [
        ("Valid JSON", f"{base['json_ok']}/{base['samples']}", f"{tuned['json_ok']}/{n}", "format"),
        (
            "Anchors proposed",
            str(base["anchors_proposed"]),
            str(tuned["anchors_proposed"]),
            "format",
        ),
        (
            "Anchors surviving the check",
            f"{base['anchors_kept']}/{base['anchors_proposed']} "
            f"({pct(base['anchors_kept'], base['anchors_proposed'])})",
            f"{tuned['anchors_kept']}/{tuned['anchors_proposed']} "
            f"({pct(tuned['anchors_kept'], tuned['anchors_proposed'])})",
            "format",
        ),
        (
            "Problems named",
            f"{base['found']}/{base['of']} ({pct(base['found'], base['of'])})",
            f"{tuned['found']}/{tuned['of']} ({pct(tuned['found'], tuned['of'])})",
            "content",
        ),
        (
            "Confidently false descriptions",
            f"{base['false_claims']}/{base['samples']}",
            f"{tuned['false_claims']}/{n}",
            "content",
        ),
    ]

    lines = [
        "# Base model vs fine-tuned checkpoint",
        "",
        "Same twenty programs, same prompt, same decoding settings. The prompt is",
        "rendered by the package rather than retyped, and both models share a chat",
        "template, so the only variable is the weights.",
        "",
        "| Measure | Base | Fine-tuned | Kind |",
        "| --- | ---: | ---: | :---: |",
    ]
    lines += [f"| {name} | {b} | {t} | `{kind}` |" for name, b, t, kind in rows]

    format_gain = (tuned["json_ok"] / max(1, n)) - (base["json_ok"] / max(1, base["samples"]))
    content_gain = (tuned["found"] / max(1, tuned["of"])) - (base["found"] / max(1, base["of"]))
    claim_gain = (base["false_claims"] / max(1, base["samples"])) - (
        tuned["false_claims"] / max(1, n)
    )

    lines += [
        "",
        "## What the training bought",
        "",
        f"- **Format compliance: {format_gain:+.0%}** valid JSON",
        f"- **Problems named: {content_gain:+.1%}** of concepts",
        f"- **Fewer false descriptions: {claim_gain:+.0%}** of samples",
        "",
        "Read the two kinds separately. A model that emits perfect JSON about code it",
        "has misread has been improved on one axis and not the other, and averaging",
        "them into a single score hides the distinction this project exists to make.",
        "",
    ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    width = max(len(name) for name, *_ in rows)
    print(f"{'measure'.ljust(width)}   {'base':>18}   {'tuned':>18}")
    for name, b, t, _ in rows:
        print(f"{name.ljust(width)}   {b:>18}   {t:>18}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
