"""Fine-tune t5-small on ERUPD. Paste into a Kaggle cell, or run as a script.

Step 2 of 3. Needs a GPU; about an hour on a free T4.

Why t5-small: ERUPD's own authors used it, Roman Urdu is Latin script so the
tokenizer is not being asked to do anything unusual, and 60M parameters serves
next to a 940 MB code model without changing the deployment story.

**The placeholder detail, which is the one that would waste a run.** Serving
masks identifiers as ``⟦0⟧``. Those brackets are U+27E6/U+27E7, which are not
in T5's SentencePiece vocabulary, so the tokenizer turns them into unknown
tokens and the model never learns to carry them across - the exact failure that
destroyed 43 of 43 placeholders when opus-mt was tried.

T5 already ships tokens designed for this: ``<extra_id_0>`` and its 99
siblings, the sentinels used for span corruption during pretraining. They are
real vocabulary entries, so they survive tokenisation and the model is already
used to emitting them. Placeholders are translated to sentinels for training
and back at the boundary; serving never sees the difference.

The assumption is checked at startup rather than trusted, because this is
precisely the kind of thing that silently produces a useless model.

    python roman_urdu/kaggle_train.py --data roman_urdu/data --out t5-roman-urdu
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PREFIX = "translate English to Roman Urdu: "

#: Where the splits live, most specific first. Kaggle mounts an attached
#: dataset read-only under /kaggle/input, and the exact path depends on how it
#: was attached, so the likely spellings are tried rather than one being
#: assumed - a wrong path here costs an hour of GPU before it is noticed.
DATA_LOCATIONS = (
    "/kaggle/input/datasets/saffiullah892/language/data",
    "/kaggle/input/language/data",
    "/kaggle/input/language",
    "roman_urdu/data",
    "data",
)

#: Only /kaggle/working survives the session. Writing the model anywhere else
#: on Kaggle trains it successfully and then throws it away.
DEFAULT_OUT = "/kaggle/working/t5-roman-urdu" if Path("/kaggle/working").exists() else "t5-roman-urdu"


def find_data(given: str | None) -> Path:
    """Locate the splits, and say what is actually there when they are missing."""
    candidates = ([given] if given else []) + list(DATA_LOCATIONS)
    for candidate in candidates:
        path = Path(candidate)
        if (path / "train.jsonl").exists():
            print(f"data: {path}")
            return path

    tried = "\n  ".join(candidates)
    available = ""
    root = Path("/kaggle/input")
    if root.exists():
        found = sorted(str(p.parent) for p in root.rglob("train.jsonl"))
        available = (
            "\n\ntrain.jsonl was found in:\n  " + "\n  ".join(found)
            if found
            else "\n\nNothing named train.jsonl exists under /kaggle/input. "
            "Is the dataset attached to this notebook?"
        )
    raise SystemExit(f"could not find train.jsonl. Tried:\n  {tried}{available}")

#: Serving writes ⟦0⟧; T5 understands <extra_id_0>. Same idea, different alphabet.
_SERVING = re.compile(r"⟦(\d+)⟧")
_SENTINEL = re.compile(r"<extra_id_(\d+)>")


def to_sentinel(text: str) -> str:
    return _SERVING.sub(lambda m: f"<extra_id_{int(m.group(1))}>", text)


def to_serving(text: str) -> str:
    return _SENTINEL.sub(lambda m: f"⟦{int(m.group(1))}⟧", text)


def check_tokenizer(tokenizer) -> None:
    """Refuse to train if placeholders do not survive a round trip.

    A model trained on placeholders the tokenizer has already destroyed looks
    like it is training normally and produces something useless an hour later.
    """
    probe = "Divide <extra_id_0> by 10 to drop the last digit of <extra_id_1>"
    restored = tokenizer.decode(
        tokenizer(probe, add_special_tokens=False)["input_ids"],
        skip_special_tokens=False,
    )
    for sentinel in ("<extra_id_0>", "<extra_id_1>"):
        if sentinel not in restored:
            raise SystemExit(
                f"{sentinel} does not survive this tokenizer: {restored!r}\n"
                "Training would silently learn nothing about placeholders."
            )
    print(f"placeholder round trip ok: {restored}")


def load(path: Path) -> list[dict[str, str]]:
    rows = [json.loads(line) for line in path.open(encoding="utf-8")]
    return [{"en": to_sentinel(r["en"]), "ru": to_sentinel(r["ru"])} for r in rows]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", default=None,
        help=f"Splits directory. Autodetected from {DATA_LOCATIONS[0]} and friends.",
    )
    parser.add_argument("--model", default="t5-small")
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--max-source", type=int, default=128)
    parser.add_argument("--max-target", type=int, default=160)
    args = parser.parse_args()

    import numpy as np
    from datasets import Dataset
    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        DataCollatorForSeq2Seq,
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    check_tokenizer(tokenizer)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)

    data = find_data(args.data)
    splits = {name: Dataset.from_list(load(data / f"{name}.jsonl"))
              for name in ("train", "validation", "test")}
    for name, split in splits.items():
        print(f"{name:<11} {len(split):>7,}")

    def encode(batch: dict[str, list[str]]) -> dict:
        model_inputs = tokenizer(
            [PREFIX + text for text in batch["en"]],
            max_length=args.max_source, truncation=True,
        )
        model_inputs["labels"] = tokenizer(
            text_target=batch["ru"], max_length=args.max_target, truncation=True
        )["input_ids"]
        return model_inputs

    encoded = {
        name: split.map(encode, batched=True, remove_columns=split.column_names)
        for name, split in splits.items()
    }

    def metrics(prediction) -> dict[str, float]:
        """chrF, and how many placeholders came back.

        chrF rather than BLEU because Roman Urdu has no standardised spelling:
        word-level BLEU would punish a correct answer for writing `hai` where
        the reference wrote `hay`. Character-level survives that.
        """
        import sacrebleu

        predicted, labels = prediction
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        predicted = np.where(predicted != -100, predicted, tokenizer.pad_token_id)
        hypotheses = tokenizer.batch_decode(predicted, skip_special_tokens=False)
        references = tokenizer.batch_decode(labels, skip_special_tokens=False)

        clean = lambda rows: [  # noqa: E731
            re.sub(r"</s>|<pad>", "", row).strip() for row in rows
        ]
        hypotheses, references = clean(hypotheses), clean(references)

        kept = wanted = 0
        for hypothesis, reference in zip(hypotheses, references, strict=True):
            expected = _SENTINEL.findall(reference)
            wanted += len(expected)
            kept += sum(1 for s in expected if f"<extra_id_{s}>" in hypothesis)

        return {
            "chrf": sacrebleu.corpus_chrf(hypotheses, [references]).score,
            "placeholders_kept": (kept / wanted) if wanted else 1.0,
        }

    trainer = Seq2SeqTrainer(
        model=model,
        args=Seq2SeqTrainingArguments(
            output_dir=args.out,
            learning_rate=args.lr,
            per_device_train_batch_size=args.batch,
            per_device_eval_batch_size=args.batch,
            num_train_epochs=args.epochs,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="chrf",
            greater_is_better=True,
            predict_with_generate=True,
            generation_max_length=args.max_target,
            fp16=True,
            logging_steps=100,
            save_total_limit=2,
            report_to=[],
        ),
        train_dataset=encoded["train"],
        eval_dataset=encoded["validation"],
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
        compute_metrics=metrics,
    )

    trainer.train()

    print("\n=== held-out test set ===")
    for key, value in trainer.evaluate(encoded["test"], metric_key_prefix="test").items():
        if isinstance(value, float):
            print(f"  {key:<28} {value:.4f}")

    trainer.save_model(args.out)
    tokenizer.save_pretrained(args.out)
    print(f"\nsaved to {args.out}/ - download it and run make_drafts.py")


if __name__ == "__main__":
    main()
