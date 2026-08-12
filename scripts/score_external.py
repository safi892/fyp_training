"""Score generations produced somewhere else with the harness used here.

The base-model comparison was run on Kaggle, because the untuned weights were
never converted to GGUF and downloading them proved slower than borrowing a
GPU. That leaves a file of raw text that has to be judged by exactly the same
rules as the fine-tuned checkpoint, or the comparison measures the marking
rather than the models.

Two parses are reported, and the gap between them is the interesting part:

- **strict**  — what the product's own parser accepts: ``json.loads`` of the
  reply, then the ``line_comments`` key. Anything else reaches a user as
  nothing at all.
- **lenient** — after stripping markdown fences and accepting a bare array in
  place of the requested object. This is the charitable reading, and it
  separates "cannot produce structure" from "produces structure in the wrong
  wrapper", which are very different problems with very different fixes.

Content is then scored on the lenient parse, so a format failure is never
allowed to masquerade as a comprehension failure. A model that understood the
code perfectly and returned it in a fence should lose format marks only.

    uv run python scripts/score_external.py \
        --input test_results/basemodel/base_model_outputs.json \
        --output test_results/hard_examples_base
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from eval_hard import SAMPLES, score, write_report  # noqa: E402

from qwen_cpp_review.line_anchoring import repair_anchors  # noqa: E402

#: ```json … ``` and friends. Models reach for a fence when asked for JSON
#: because that is how JSON appears in nearly all their training text.
_FENCE = re.compile(r"^\s*```[a-zA-Z]*\s*\n(.*?)\n\s*```\s*$", re.S)


def strip_fence(text: str) -> str:
    match = _FENCE.match(text.strip())
    return match.group(1) if match else text.strip()


def parse_strict(text: str) -> list[dict[str, Any]] | None:
    """What the serving code accepts. Anything else shows the user nothing."""
    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None
    anchors = payload.get("line_comments")
    return anchors if isinstance(anchors, list) else None


def parse_lenient(text: str) -> list[dict[str, Any]] | None:
    """The charitable reading: unwrap a fence, and take a bare array as the field.

    Being generous here is deliberate. If the only thing wrong is the wrapper,
    that is a few lines of parsing rather than a missing capability, and the
    report should say which of the two it found.
    """
    body = strip_fence(text)
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return None
    if isinstance(payload, dict):
        payload = payload.get("line_comments")
    if not isinstance(payload, list):
        return None
    return [item for item in payload if isinstance(item, dict)]


def read_explanation(text: str) -> tuple[str, bool]:
    """Return the prose and whether it arrived as the requested JSON field."""
    body = strip_fence(text)
    try:
        payload = json.loads(body)
        if isinstance(payload, dict) and payload.get("explanation"):
            return str(payload["explanation"]), True
    except (json.JSONDecodeError, TypeError):
        pass
    # Not JSON. Score the prose anyway: refusing to would let a model dodge the
    # content question by failing the format one.
    return text, False


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--input", required=True, help='{"sample": {"task": "text"}}')
    parser.add_argument("--output", default="test_results/hard_examples_base")
    args = parser.parse_args()

    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    by_name = {s["name"]: s for s in SAMPLES}

    records: list[dict[str, Any]] = []
    strict_ok = lenient_ok = explanation_json = 0

    for name, sample in by_name.items():
        reply = raw.get(name)
        if reply is None:
            print(f"  {name:<34} MISSING from the input file")
            continue

        comments_raw = reply.get("line_comments", "")
        explanation_raw = reply.get("explanation", "")

        strict = parse_strict(comments_raw)
        lenient = parse_lenient(comments_raw) or []
        explanation, explanation_was_json = read_explanation(explanation_raw)

        strict_ok += strict is not None
        lenient_ok += bool(lenient)
        explanation_json += explanation_was_json

        report = repair_anchors(sample["code"], lenient)
        text = "\n".join(
            [*(str(a.get("comment") or "") for a in lenient), explanation]
        )
        result = score(text, sample)

        records.append({
            **sample,
            **result,
            "text": text,
            # `json_ok` keeps the meaning it has everywhere else in this project:
            # the reply the serving code could actually use.
            "json_ok": strict is not None and explanation_was_json,
            "strict_json": strict is not None,
            "lenient_json": bool(lenient),
            "explanation_json": explanation_was_json,
            "anchors_proposed": len(lenient),
            "anchors_kept": len(report.anchors),
            "raw": reply,
        })

        print(
            f"  {name:<34} strict={'ok ' if strict is not None else 'no '}"
            f"lenient={'ok ' if lenient else 'no '}"
            f"anchors={len(report.anchors)}/{len(lenient):<3} "
            f"found={result['found']}/{result['of']}"
            f"{'  FALSE' if result['false_claim'] else ''}"
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    write_report(records, out.with_suffix(".md"))

    n = len(records)
    proposed = sum(r["anchors_proposed"] for r in records)
    kept = sum(r["anchors_kept"] for r in records)
    print(f"\n{'=' * 72}")
    print(f"usable by the serving parser  : {strict_ok}/{n}")
    print(f"parseable if fences stripped  : {lenient_ok}/{n}")
    print(f"explanation as requested JSON : {explanation_json}/{n}")
    print(f"anchors surviving the check   : {kept}/{proposed}"
          f"{'' if not proposed else f' ({kept / proposed:.0%})'}")
    print(f"problems named                : {sum(r['found'] for r in records)}"
          f"/{sum(r['of'] for r in records)}")
    print(f"confidently false             : {sum(r['false_claim'] for r in records)}/{n}")
    print(f"\nwrote {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
