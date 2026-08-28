"""Compare Roman Urdu checkpoints on the held-out test set, and on the register.

Stage 1 speaks Roman Urdu and does not know the developer vocabulary: measured
on three sentences it rendered "iterates over" as *tayyar karta hai* (prepares)
and "is empty" as *saaf karta hai* (cleans), while keeping every placeholder.
Stage 2 exists to fix the verbs without losing the placeholders, so both have to
be measured or the trade is invisible.

Three numbers, and the third is the one chrF cannot give:

    chrF                character overlap with the reference
    placeholders_kept   share of the reference's placeholders that survived
    register            hand-checked verbs on fixed probe sentences

`--split test` is the default on purpose. `load_best_model_at_end` selected the
checkpoint on validation chrF, so validation is optimistic for every model that
was trained here and honest only for stage 1, which never saw either.

    uv run python roman_urdu/compare_models.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kaggle_train import PREFIX, to_sentinel, to_serving  # noqa: E402

_PLACEHOLDER = re.compile(r"⟦(\d+)⟧")

#: Sentences whose correct Roman Urdu verb is known, so the register can be read
#: rather than inferred from a similarity score. A wrong verb shares most of its
#: characters with the right one, which is exactly why chrF cannot see this.
PROBES: list[dict[str, Any]] = [
    {
        "en": "Iterates over the vector ⟦0⟧ and returns the sum.",
        "wrong": ["tayyar"],          # "prepares" - what stage 1 said
        "right": ["iterate", "chalta", "guzarta", "loop"],
    },
    {
        "en": "Returns true if the list ⟦0⟧ is empty.",
        "wrong": ["saaf"],            # "cleans" - what stage 1 said
        "right": ["empty", "khaali", "khali"],
    },
    {
        "en": "⟦0⟧ – a mutable 2-D integer matrix.",
        "wrong": [],
        "right": ["matrix", "integer"],
    },
    {
        "en": "Recursively computes the factorial of ⟦0⟧.",
        "wrong": [],
        "right": ["recursi", "factorial"],
    },
    {
        "en": "Swaps the values at indices ⟦0⟧ and ⟦1⟧ using a temporary variable.",
        "wrong": [],
        "right": ["swap", "badal", "temporary"],
    },
]


def load(path: Path):
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(path))
    model.eval()
    return tokenizer, model


def translate(tokenizer, model, english: str, max_new_tokens: int = 160) -> str:
    import torch

    encoded = tokenizer(PREFIX + to_sentinel(english), return_tensors="pt", truncation=True)
    with torch.no_grad():
        out = model.generate(**encoded, max_new_tokens=max_new_tokens, num_beams=4)
    raw = tokenizer.decode(out[0], skip_special_tokens=False)
    for token in ("<pad>", "</s>"):
        raw = raw.replace(token, "")
    return to_serving(raw.strip())


def score(tokenizer, model, rows: list[dict[str, str]]) -> dict[str, Any]:
    import sacrebleu

    hypotheses, references = [], []
    kept = wanted = 0
    for row in rows:
        hypothesis = translate(tokenizer, model, row["en"])
        hypotheses.append(hypothesis)
        references.append(row["ru"])
        expected = _PLACEHOLDER.findall(row["ru"])
        wanted += len(expected)
        kept += sum(1 for index in expected if f"⟦{index}⟧" in hypothesis)
    return {
        "chrf": sacrebleu.corpus_chrf(hypotheses, [references]).score,
        "placeholders_kept": (kept / wanted) if wanted else 1.0,
        "placeholders": wanted,
        "hypotheses": hypotheses,
    }


def register(tokenizer, model) -> dict[str, Any]:
    """Read the verbs, since a similarity score cannot."""
    results = []
    for probe in PROBES:
        got = translate(tokenizer, model, probe["en"])
        lowered = got.lower()
        results.append({
            "en": probe["en"],
            "ru": got,
            "kept_placeholders": set(_PLACEHOLDER.findall(probe["en"]))
            <= set(_PLACEHOLDER.findall(got)),
            "says_wrong": [w for w in probe["wrong"] if w in lowered],
            "says_right": [r for r in probe["right"] if r in lowered],
        })
    return {
        "probes": results,
        "wrong_verbs": sum(1 for r in results if r["says_wrong"]),
        "right_words": sum(1 for r in results if r["says_right"]),
        "placeholders_held": sum(1 for r in results if r["kept_placeholders"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", required=True, help="checkpoint directories")
    parser.add_argument("--labels", nargs="+", default=None)
    parser.add_argument("--data", type=Path,
                        default=Path("my_data_annotation/roman_urdu/data"))
    parser.add_argument("--split", default="test", choices=("test", "validation"))
    parser.add_argument("--limit", type=int, default=0, help="0 for the whole split")
    parser.add_argument("--output", type=Path,
                        default=Path("urdu_output/comparison.json"))
    args = parser.parse_args()

    labels = args.labels or [Path(m).name for m in args.models]
    if len(labels) != len(args.models):
        raise SystemExit("--labels must match --models")

    rows = [
        json.loads(line)
        for line in (args.data / f"{args.split}.jsonl").read_text().splitlines()
        if line.strip()
    ]
    if args.limit:
        rows = rows[: args.limit]
    print(f"{args.split} split: {len(rows)} pairs, "
          f"{sum(len(_PLACEHOLDER.findall(r['ru'])) for r in rows)} placeholders\n")

    records = []
    for label, path in zip(labels, args.models):
        print(f"--- {label} ---", flush=True)
        tokenizer, model = load(Path(path))
        measured = score(tokenizer, model, rows)
        reg = register(tokenizer, model)
        print(f"  chrF {measured['chrf']:.2f}   placeholders "
              f"{measured['placeholders_kept']:.1%}   "
              f"wrong verbs {reg['wrong_verbs']}/{len(PROBES)}   "
              f"right words {reg['right_words']}/{len(PROBES)}", flush=True)
        records.append({
            "label": label, "path": str(path),
            "chrf": measured["chrf"],
            "placeholders_kept": measured["placeholders_kept"],
            "placeholders": measured["placeholders"],
            **{k: v for k, v in reg.items() if k != "probes"},
            "probes": reg["probes"],
        })
        # Written per model: loading four seq2seq models and decoding 62 pairs
        # each is minutes, and a kill should not cost the ones already done.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")

    print(f"\n{'=' * 74}")
    print(f"{'model':22} {'chrF':>7} {'placeholders':>13} {'wrong verbs':>12} {'right':>7}")
    print("-" * 74)
    for record in records:
        print(f"{record['label']:22} {record['chrf']:>7.2f} "
              f"{record['placeholders_kept']:>12.1%} "
              f"{record['wrong_verbs']:>8}/{len(PROBES)} "
              f"{record['right_words']:>5}/{len(PROBES)}")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
