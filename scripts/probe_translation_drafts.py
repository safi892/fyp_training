"""Find out whether machine drafts are worth correcting, before correcting 5,000.

The plan for a Roman Urdu corpus is to generate drafts and fix them rather than
translate from scratch, because correcting is several times faster than
composing. That saving is the whole reason the corpus is a fortnight instead of
a term — and it only exists if the drafts come out close enough to correct. If
they need rewriting, the generator is costing time rather than saving it, and
that is worth knowing on day one rather than in week two.

Only the first hop is measured here. Urdu to Roman Urdu is transliteration and
is close to solved: a fine-tuned m2m100 reaches Char-BLEU 96.4, beating
GPT-4o Mini (arXiv 2503.21530). English to Urdu on *technical* text is the
unknown, because every published Urdu MT system was trained on news and
conversation, and none of it discusses pointers.

So this translates real explanations from the corpus into Urdu and prints them
side by side. There is no automatic score here on purpose: whether a draft is
correctable is a judgement a fluent reader makes in a few seconds and no metric
makes reliably.

    uv run python scripts/probe_translation_drafts.py --limit 50
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

#: Lines are sampled by section rather than uniformly. `Algorithm` is the half
#: the rule layer cannot reach and therefore the half a trained model exists to
#: serve, so it is the half whose drafts actually matter.
SECTION_WEIGHTS = {"algorithm": 0.5, "purpose": 0.25, "output": 0.15, "input": 0.10}

_LABEL = re.compile(r"^\s*(Purpose|Input|Output|Algorithm)\s*:\s*(.+)$", re.I | re.S)

#: Code fragments are masked before translation, exactly as the serving path
#: does it, so this measures the drafts the pipeline would really produce.
_PROTECTED = re.compile(
    r"`[^`\n]+`"
    r"|\b[A-Za-z_]\w*\s*\([^()\n]*\)"
    r"|\b[A-Za-z_]\w*\s*\[[^\[\]\n]*\]"
    r"|\b[A-Za-z_]\w*(?:::|->|\.)\w+"
    r"|\b[a-z]+[A-Z]\w*"
    r"|\b\w+_\w+\b"
    r"|\bO\([^()\n]*\)"
)


def mask(text: str) -> tuple[str, list[str]]:
    spans: list[str] = []
    index: dict[str, int] = {}

    def swap(match: re.Match[str]) -> str:
        span = match.group(0)
        if span not in index:
            index[span] = len(spans)
            spans.append(span)
        return f"⟦{index[span]}⟧"

    return _PROTECTED.sub(swap, text), spans


def sample_lines(path: Path, limit: int, seed: int) -> list[tuple[str, str]]:
    """Pull labelled explanation lines, weighted towards the hard sections."""
    buckets: dict[str, list[str]] = {key: [] for key in SECTION_WEIGHTS}
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            explanation = json.loads(raw).get("explanation") or ""
            for line in explanation.split("\n"):
                match = _LABEL.match(line.strip())
                if not match:
                    continue
                section = match.group(1).lower()
                if section in buckets and len(buckets[section]) < limit * 20:
                    buckets[section].append(match.group(2).strip())

    rng = random.Random(seed)
    chosen: list[tuple[str, str]] = []
    for section, weight in SECTION_WEIGHTS.items():
        wanted = max(1, round(limit * weight))
        pool = buckets[section]
        chosen += [(section, line) for line in rng.sample(pool, min(wanted, len(pool)))]
    rng.shuffle(chosen)
    return chosen[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--model", default="models/mt/opus-en-ur")
    parser.add_argument("--data", default="cleaned/merged_cleaned.jsonl")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", default="test_results/translation_drafts.md")
    args = parser.parse_args()

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    print(f"loading {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    model.eval()

    lines = sample_lines(Path(args.data), args.limit, args.seed)
    print(f"sampled {len(lines)} lines\n")

    records: list[dict[str, Any]] = []
    for position, (section, english) in enumerate(lines, start=1):
        masked, spans = mask(english)
        batch = tokenizer([masked], return_tensors="pt", truncation=True, max_length=256)
        output = model.generate(**batch, max_new_tokens=200, num_beams=4)
        urdu = tokenizer.decode(output[0], skip_special_tokens=True)

        kept = sum(1 for index in range(len(spans)) if f"⟦{index}⟧" in urdu)
        records.append({
            "section": section, "english": english, "masked": masked,
            "urdu": urdu, "spans": len(spans), "spans_kept": kept,
        })
        print(f"[{position:>3}/{len(lines)}] {section:<10} placeholders {kept}/{len(spans)}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    body = [
        "# English → Urdu drafts, for judging",
        "",
        "First hop only. Read these and answer one question: **would correcting this",
        "be faster than writing it from scratch?** If yes, the corpus is a fortnight.",
        "If no, the generator is not earning its place and the plan should change now.",
        "",
        "Placeholders (`⟦0⟧`) stand for code fragments, which are masked before",
        "translation. A draft that loses them would lose the identifiers too.",
        "",
    ]
    total = sum(r["spans"] for r in records)
    kept = sum(r["spans_kept"] for r in records)
    body += [
        f"**{len(records)} lines · placeholders surviving the hop: {kept}/{total}"
        f"{'' if not total else f' ({kept / total:.0%})'}**",
        "",
        "---",
        "",
    ]
    for index, record in enumerate(records, start=1):
        body += [
            f"### {index}. `{record['section']}`",
            "",
            f"**EN** {record['english']}",
            "",
            f"**UR** {record['urdu']}",
            "",
        ]
    out.write_text("\n".join(body), encoding="utf-8")

    print(f"\n{'=' * 72}")
    print(f"placeholders surviving: {kept}/{total}")
    print(f"wrote {out} - read it and judge whether these are correctable")


if __name__ == "__main__":
    main()
