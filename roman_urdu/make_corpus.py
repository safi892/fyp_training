"""Draft a batch, correct it by hand, collect it into training pairs.

Step 4. The corpus is the contribution and the hand-correction is nearly all
the work, so the format is chosen to make that hour pleasant rather than to be
tidy: a plain text file, one sentence per block, edited in place.

    uv run python roman_urdu/make_corpus.py draft --limit 50     # writes a batch
    #  ... edit the RU lines in roman_urdu/corpus/batch_001.txt ...
    uv run python roman_urdu/make_corpus.py collect              # -> pairs.jsonl

Corrections are checked, not trusted. Every placeholder in the English has to
appear in the Roman Urdu, because a corrected row with a dropped identifier
teaches the model to drop identifiers - and hand-written data is exactly where
that kind of mistake hides, since nobody reviews the reviewer.

Blocks left exactly as the model wrote them are reported separately rather than
counted as corrections. A draft that happened to be perfect is real data, but
it should be an explicit decision to keep it, not an accident of not having got
to it yet.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_drafts import PREFIX, load_tokenizer, mask, sample_lines, to_sentinel, to_serving

_PLACEHOLDER = re.compile(r"⟦(\d+)⟧")
_BLOCK = re.compile(
    r"^#\s*(\d+)\s+(\w+)(.*)$\n^EN\s+(.*)$\n^RU\s+(.*)$", re.M
)

HEADER = """\
# Roman Urdu corpus - batch {batch}
#
# Edit the RU lines. Leave EN alone.
#
# Rules that are checked when this is collected:
#   * every ⟦n⟧ in the EN line must appear in your RU line
#   * keep technical words in English - function, array, pointer, index
#   * write how you would say it out loud, not how a textbook would
#
# The ⟦n⟧ = ... note on each header line says what the placeholder stands for.
# Delete a block entirely to drop that sentence.

"""


def write_batch(records: list[dict], path: Path, batch: int) -> None:
    blocks = [HEADER.format(batch=batch)]
    for index, record in enumerate(records, start=1):
        legend = "  ".join(
            f"⟦{n}⟧={span}" for n, span in enumerate(record["spans"])
        )
        blocks.append(
            f"# {index}  {record['section']}"
            f"{'   ' + legend if legend else ''}\n"
            f"EN  {record['masked']}\n"
            f"RU  {record['draft']}\n"
        )
    path.write_text("\n".join(blocks), encoding="utf-8")


def parse_batch(text: str) -> list[dict[str, str]]:
    return [
        {"index": m.group(1), "section": m.group(2),
         "en": m.group(4).strip(), "ru": m.group(5).strip()}
        for m in _BLOCK.finditer(text)
    ]


def check(row: dict[str, str]) -> str | None:
    """Return why a row cannot be used, or None if it is fine."""
    if not row["ru"]:
        return "RU line is empty"
    wanted = sorted(_PLACEHOLDER.findall(row["en"]))
    got = sorted(_PLACEHOLDER.findall(row["ru"]))
    if wanted != got:
        missing = set(wanted) - set(got)
        extra = set(got) - set(wanted)
        if missing:
            return f"RU is missing ⟦{sorted(missing)[0]}⟧"
        if extra:
            return f"RU has ⟦{sorted(extra)[0]}⟧, which is not in the English"
        return "placeholder counts differ between EN and RU"
    return None


def do_draft(args: argparse.Namespace) -> None:
    from transformers import AutoModelForSeq2SeqLM

    tokenizer = load_tokenizer(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    model.eval()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    batch = 1 + len(list(outdir.glob("batch_*.txt")))

    # Everything already sent out, so batches do not repeat each other.
    already = {
        row["en"]
        for path in outdir.glob("batch_*.txt")
        for row in parse_batch(path.read_text(encoding="utf-8"))
    }
    lines = sample_lines(Path(args.data), args.limit, args.seed + batch, exclude=already)
    if already:
        print(f"skipping {len(already):,} sentences already drafted")
    print(f"batch {batch}: drafting {len(lines)} lines\n")

    import torch

    # Generated in groups rather than one at a time: on CPU the per-call
    # overhead dominates, and 2,000 sentences singly is hours where batched it
    # is well under one.
    records = []
    for start in range(0, len(lines), args.chunk):
        group = lines[start : start + args.chunk]
        masked = [mask(english) for _, english in group]
        inputs = tokenizer(
            [PREFIX + to_sentinel(text) for text, _ in masked],
            return_tensors="pt", truncation=True, max_length=256, padding=True,
        )
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=200, num_beams=4)

        for (section, _), (text, spans), output in zip(group, masked, outputs, strict=True):
            draft = to_serving(tokenizer.decode(output, skip_special_tokens=False))
            draft = re.sub(r"</s>|<pad>", "", draft).strip()
            records.append(
                {"section": section, "masked": text, "draft": draft, "spans": spans}
            )
        print(f"[{len(records):>5}/{len(lines)}]")

    path = outdir / f"batch_{batch:03d}.txt"
    write_batch(records, path, batch)
    # Kept so `collect` can tell a block that was judged correct from one that
    # was never looked at.
    path.with_suffix(".drafts.json").write_text(
        json.dumps({str(i): r["draft"] for i, r in enumerate(records, start=1)},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\nwrote {path}")
    print("edit the RU lines, then: python roman_urdu/make_corpus.py collect")


def do_collect(args: argparse.Namespace) -> None:
    outdir = Path(args.outdir)
    batches = sorted(outdir.glob("batch_*.txt"))
    if not batches:
        raise SystemExit(f"no batch files in {outdir}. Run `draft` first.")

    pairs: list[dict[str, str]] = []
    rejected: list[tuple[str, str, str]] = []
    untouched = 0

    for path in batches:
        rows = parse_batch(path.read_text(encoding="utf-8"))
        # The drafts as generated, so a block nobody has touched can be told
        # from one that was read and judged already correct. Both are usable
        # data; only the second is a decision.
        sidecar = path.with_suffix(".drafts.json")
        original = json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else {}

        print(f"{path.name}: {len(rows)} blocks")
        for row in rows:
            problem = check(row)
            if problem:
                rejected.append((path.name, row["index"], problem))
                continue
            if original.get(row["index"]) == row["ru"]:
                untouched += 1
            pairs.append({"en": row["en"], "ru": row["ru"]})

    out = Path(args.pairs)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for pair in pairs:
            handle.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print(f"\n{'=' * 66}")
    print(f"usable pairs : {len(pairs):,}  -> {out}")
    if untouched:
        print(f"untouched    : {untouched}")
    if rejected:
        print(f"rejected     : {len(rejected)}")
        for name, index, problem in rejected[:10]:
            print(f"   {name} block {index}: {problem}")
        if len(rejected) > 10:
            print(f"   ... and {len(rejected) - 10} more")
    print()
    print(f"target for stage 2 is 2,000-5,000. At {len(pairs):,} you are "
          f"{len(pairs) / 2000:.0%} of the way to the lower bound.")


def do_split(args: argparse.Namespace) -> None:
    """Turn collected pairs into the train/validation/test files training wants.

    Held-out sets are small because the corpus is: at a few hundred pairs a 10%
    validation split costs more in training signal than it buys in confidence,
    and the measurement that actually decides anything is reading the output.
    """
    import random

    pairs = [json.loads(line) for line in Path(args.pairs).open(encoding="utf-8")]
    random.Random(args.seed).shuffle(pairs)

    held = max(10, len(pairs) // 20)
    splits = {
        "test": pairs[:held],
        "validation": pairs[held : held * 2],
        "train": pairs[held * 2 :],
    }

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for name, rows in splits.items():
        path = outdir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"  {name:<11} {len(rows):>6,}  -> {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    draft = sub.add_parser("draft", help="generate a batch to correct")
    draft.add_argument("--model", default="kaggle_output/urdu_output/results(7)/t5-roman-urdu")
    draft.add_argument("--data", default="cleaned/merged_cleaned.jsonl")
    draft.add_argument("--outdir", default="roman_urdu/corpus")
    draft.add_argument("--limit", type=int, default=50)
    draft.add_argument("--seed", type=int, default=100)
    draft.add_argument("--chunk", type=int, default=16, help="Sentences per generate call.")
    draft.set_defaults(func=do_draft)

    collect = sub.add_parser("collect", help="turn corrected batches into pairs")
    collect.add_argument("--outdir", default="roman_urdu/corpus")
    collect.add_argument("--pairs", default="roman_urdu/corpus/pairs.jsonl")
    collect.set_defaults(func=do_collect)

    split = sub.add_parser("split", help="pairs.jsonl -> train/validation/test")
    split.add_argument("--pairs", default="roman_urdu/corpus/pairs.jsonl")
    split.add_argument("--outdir", default="roman_urdu/data_domain")
    split.add_argument("--seed", type=int, default=13)
    split.set_defaults(func=do_split)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
