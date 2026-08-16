"""Draft our own explanations with the trained model, and judge them.

Step 3 of 3. Runs locally on CPU once the Kaggle model is downloaded.

This is the check that failed with ``opus-mt-en-ur``: 0 of 43 placeholders
survived and 9 of 50 drafts came back full of ``%s`` and ``%d``, because that
model was trained on software localisation catalogues. The question is
unchanged - **would correcting these be faster than writing them from
scratch?** - and the answer decides whether a domain corpus is a fortnight or
not worth starting.

A model fine-tuned on ERUPD should do better for three reasons: it emits Roman
Urdu directly rather than going through Urdu and a transliterator, it was
trained on conversational text rather than gettext strings, and it has seen
placeholders and been measured on keeping them.

It will still not know the technical register - ERUPD contains the word
"integer" zero times against 8,353 in our corpus. That gap is what the
corrections create, and it is the whole point of the exercise.

    uv run python roman_urdu/make_drafts.py --model t5-roman-urdu --limit 50
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kaggle_train import PREFIX, to_sentinel, to_serving  # noqa: E402

#: Weighted towards Algorithm: it is the half the rule layer cannot reach, so
#: it is the half a trained model exists to serve. Drafting the easy sections
#: would flatter the result.
SECTION_WEIGHTS = {"algorithm": 0.5, "purpose": 0.25, "output": 0.15, "input": 0.10}

_LABEL = re.compile(r"^\s*(Purpose|Input|Output|Algorithm)\s*:\s*(.+)$", re.I | re.S)

#: Kept in step with the serving masker in the backend. Duplicated rather than
#: imported for the reason the anchoring code is: the two projects pin
#: different transformers versions and must deploy independently.
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


def load_tokenizer(path: str):
    """Load the saved tokenizer, tolerating the version it was saved by.

    Kaggle's transformers writes ``extra_special_tokens`` as a list; older
    releases read it as a mapping and fail with ``'list' object has no
    attribute 'keys'``. The key is redundant either way — the 100 sentinels are
    already registered through ``extra_ids`` — so it is overridden rather than
    the downloaded model being edited, which would make the fix invisible to
    the next person who copies it off Kaggle.
    """
    from transformers import AutoTokenizer

    try:
        return AutoTokenizer.from_pretrained(path)
    except AttributeError:
        return AutoTokenizer.from_pretrained(path, extra_special_tokens={})


def sample_lines(
    path: Path, limit: int, seed: int, exclude: set[str] | None = None
) -> list[tuple[str, str]]:
    """Sample labelled lines, skipping any already drafted.

    ``exclude`` matters once batches are being produced in series: the pool was
    previously capped at the first ``limit * 20`` lines of the file, so batch 40
    drew from the same few hundred sentences as batch 1 and mostly repeated
    them. The whole corpus is read now, and lines already sent out are dropped.
    """
    exclude = set(exclude or set())
    buckets: dict[str, list[str]] = {key: [] for key in SECTION_WEIGHTS}
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            for line in (json.loads(raw).get("explanation") or "").split("\n"):
                match = _LABEL.match(line.strip())
                if not match:
                    continue
                section = match.group(1).lower()
                body = match.group(2).strip()
                # Compared in masked form, because that is what a batch file
                # records and therefore all a later run can read back. Adding
                # to `exclude` as we go also drops the repeats inside the
                # corpus itself - the same one-line Purpose appears under many
                # functions, and correcting it twice is wasted effort.
                masked = mask(body)[0]
                if section in buckets and masked not in exclude:
                    exclude.add(masked)
                    buckets[section].append(body)

    rng = random.Random(seed)
    chosen: list[tuple[str, str]] = []
    for section, weight in SECTION_WEIGHTS.items():
        pool = buckets[section]
        wanted = max(1, round(limit * weight))
        chosen += [(section, line) for line in rng.sample(pool, min(wanted, len(pool)))]
    rng.shuffle(chosen)
    return chosen[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="t5-roman-urdu")
    parser.add_argument("--data", default="cleaned/merged_cleaned.jsonl")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", default="roman_urdu/drafts.md")
    args = parser.parse_args()

    from transformers import AutoModelForSeq2SeqLM

    tokenizer = load_tokenizer(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    model.eval()

    lines = sample_lines(Path(args.data), args.limit, args.seed)
    print(f"drafting {len(lines)} lines\n")

    records = []
    for position, (section, english) in enumerate(lines, start=1):
        masked, spans = mask(english)
        batch = tokenizer(
            PREFIX + to_sentinel(masked), return_tensors="pt",
            truncation=True, max_length=256,
        )
        output = model.generate(**batch, max_new_tokens=200, num_beams=4)
        draft = to_serving(tokenizer.decode(output[0], skip_special_tokens=False))
        draft = re.sub(r"</s>|<pad>", "", draft).strip()

        kept = sum(1 for index in range(len(spans)) if f"⟦{index}⟧" in draft)
        records.append({
            "section": section, "english": english, "masked": masked,
            "draft": draft, "spans": len(spans), "kept": kept,
        })
        print(f"[{position:>3}/{len(lines)}] {section:<10} placeholders {kept}/{len(spans)}")

    total = sum(r["spans"] for r in records)
    kept = sum(r["kept"] for r in records)

    body = [
        "# Roman Urdu drafts from the fine-tuned model",
        "",
        "Read these and answer one question: **would correcting this be faster than",
        "writing it from scratch?**",
        "",
        "If yes, the domain corpus is worth building and these are its first rows.",
        "If no, stop - the same answer opus-mt gave, and the same conclusion.",
        "",
        f"**{len(records)} lines · placeholders kept {kept}/{total}"
        f"{'' if not total else f' ({kept / total:.0%})'}** "
        "(opus-mt managed 0/43)",
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
            f"**RU** {record['draft']}",
            "",
        ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(body), encoding="utf-8")

    print(f"\n{'=' * 72}")
    print(f"placeholders kept: {kept}/{total}   (opus-mt: 0/43)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
