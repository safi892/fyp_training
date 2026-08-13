"""Clean ERUPD into training splits, and teach placeholders while we are here.

Step 1 of 3. Runs locally; produces the files that get uploaded to Kaggle.

Two jobs.

**Cleaning.** ERUPD ships 75,146 rows of which about 8,000 are duplicates or
untranslated - rows where the Roman Urdu column repeats the English. Training
on those teaches the model to copy its input, which is exactly the failure
mode that would be hardest to notice afterwards, because copied English looks
like a confident answer.

**Placeholder augmentation.** The serving path masks identifiers to ``⟦0⟧``
before translation, so the model has to learn that such tokens are opaque and
must come out exactly as they went in. Nothing in ERUPD contains them.

Rather than inventing synthetic examples, real ones are made from the corpus:
a proper noun appearing verbatim on both sides ("named Aisha" / "naam Aisha
tha") is genuine evidence of a token that survives translation unchanged.
Replacing both occurrences with a placeholder produces a true parallel pair
that teaches the copy behaviour, with correct word order around it, for free.

    uv run python roman_urdu/prepare_data.py
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
from pathlib import Path

#: Tokens that look like names rather than ordinary words: capitalised inside
#: the sentence, and long enough not to be "I" or "A".
_CANDIDATE = re.compile(r"\b[A-Z][a-z]{2,}\b")

#: Words that are capitalised for grammar rather than because they name
#: something, and would make useless placeholders.
_NOT_A_NAME = {
    "The", "This", "That", "There", "These", "Those", "Then", "They", "Their",
    "She", "Her", "His", "Him", "Its", "But", "And", "For", "With", "When",
    "What", "Why", "How", "One", "Two", "All", "Some", "Any", "You", "Your",
    "Was", "Were", "Have", "Has", "Had", "Not", "Now", "New", "After", "Before",
}


def usable(english: str, roman: str) -> bool:
    """Whether a row is worth training on."""
    if len(english.split()) < 3 or len(roman.split()) < 3:
        return False
    if english.strip().lower() == roman.strip().lower():
        return False  # untranslated; teaches the model to echo
    # Roman Urdu is Latin script by definition. Anything in the Arabic block
    # means the row is really Urdu and belongs to a different task.
    return not any(0x0600 <= ord(character) <= 0x06FF for character in roman)


def add_placeholder(english: str, roman: str) -> tuple[str, str] | None:
    """Mask one word that appears verbatim on both sides, if there is one.

    The shared word is real evidence of a token translation leaves alone, which
    is precisely what a masked identifier is. Only one is masked per row: the
    lesson is "carry this across", and repeating it in a single sentence does
    not teach it harder.
    """
    for candidate in _CANDIDATE.findall(english):
        if candidate in _NOT_A_NAME:
            continue
        if not re.search(rf"\b{re.escape(candidate)}\b", roman):
            continue
        pattern = rf"\b{re.escape(candidate)}\b"
        return (
            re.sub(pattern, "⟦0⟧", english, count=1),
            re.sub(pattern, "⟦0⟧", roman, count=1),
        )
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="urdu/ERUPD_NMT.csv")
    parser.add_argument("--outdir", default="roman_urdu/data")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument(
        "--placeholder-share", type=float, default=0.15,
        help="Fraction of eligible rows to also emit in masked form.",
    )
    args = parser.parse_args()

    rows = list(csv.DictReader(Path(args.input).open(encoding="utf-8")))
    print(f"read {len(rows):,} rows")

    seen: set[tuple[str, str]] = set()
    pairs: list[tuple[str, str]] = []
    for row in rows:
        english = (row.get("English") or "").strip()
        roman = (row.get("Roman Urdu") or "").strip()
        if not usable(english, roman):
            continue
        key = (english.lower(), roman.lower())
        if key in seen:
            continue
        seen.add(key)
        pairs.append((english, roman))
    print(f"clean, deduplicated      : {len(pairs):,}")

    rng = random.Random(args.seed)
    augmented: list[tuple[str, str]] = []
    eligible = 0
    for english, roman in pairs:
        masked = add_placeholder(english, roman)
        if masked is None:
            continue
        eligible += 1
        if rng.random() < args.placeholder_share:
            augmented.append(masked)
    print(f"rows with a shared name  : {eligible:,}")
    print(f"placeholder examples added: {len(augmented):,}")

    everything = pairs + augmented
    rng.shuffle(everything)
    cut_test = len(everything) // 50          # 2%
    cut_val = cut_test * 2                    # a further 2%
    splits = {
        "test": everything[:cut_test],
        "validation": everything[cut_test:cut_val],
        "train": everything[cut_val:],
    }

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for name, split in splits.items():
        path = outdir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for english, roman in split:
                handle.write(
                    json.dumps({"en": english, "ru": roman}, ensure_ascii=False) + "\n"
                )
        print(f"  {name:<11} {len(split):>7,}  -> {path}")

    print(f"\nupload {outdir}/ to Kaggle as a dataset, then run kaggle_train.py")


if __name__ == "__main__":
    main()
