# Roman Urdu translator

Self-contained. Nothing here touches the C++ review model, the training
pipeline, or the API — it produces one small seq2seq model that turns English
explanations into Roman Urdu, and the backend calls it behind the interface it
already has.

Three steps, in order. **Stop after step 3 if the drafts are bad** — that is
what step 3 is for.

```
prepare_data.py   local, seconds     clean ERUPD into splits
kaggle_train.py   Kaggle GPU, ~1 hr  fine-tune t5-small
make_drafts.py    local CPU, minutes draft our own text and judge it
```

---

## Why this shape

The system needs Roman Urdu that sounds like a developer, and no dataset
contains that. What exists splits cleanly in two:

- **ERUPD** — 75,146 English → Roman Urdu pairs, conversational and narrative.
  Teaches *the language*.
- **Nothing** — teaches *the register*. Measured against our own corpus, ERUPD
  contains the word "integer" **0** times against 8,353 in ours; "iterate" 0
  against 2,295; "vector" once against 11,504.

So the language is borrowed and the register is built:

```
stage 1   ERUPD, 67k pairs        ->  general English -> Roman Urdu
stage 2   our corpus, 2-5k pairs  ->  the developer register
```

Only stage 1 is here. Stage 2 needs a corpus that does not exist yet, and step
3 exists to find out whether generating it is realistic before a fortnight goes
into it.

---

## Step 1 — prepare the data

```bash
uv run python roman_urdu/prepare_data.py
```

Reads `urdu/ERUPD_NMT.csv`, writes `roman_urdu/data/{train,validation,test}.jsonl`.

| | |
| --- | ---: |
| rows in | 75,146 |
| after dropping duplicates and untranslated rows | **66,956** |
| placeholder examples added | ~3,600 |
| train / validation / test | 67,723 / 1,410 / 1,410 |

**The placeholder examples matter.** Serving masks identifiers to `⟦0⟧` before
translation, and the model has to learn those are opaque tokens to carry
across. Rather than inventing synthetic rows, real ones are made from ERUPD: a
proper noun appearing verbatim on both sides ("named Aisha" / "naam Aisha tha")
is genuine evidence of a token translation leaves alone, so masking both
occurrences yields a true parallel pair with correct word order around it.

## Step 2 — train on Kaggle

Upload `roman_urdu/data/` as a Kaggle dataset, then run `kaggle_train.py` in a
GPU notebook. About an hour on a free T4.

**One detail that would otherwise waste the run.** `⟦` and `⟧` are U+27E6/U+27E7
and are *not* in T5's vocabulary, so the tokenizer would turn every placeholder
into an unknown token and the model would learn nothing about them — exactly
what destroyed 43 of 43 placeholders when `opus-mt-en-ur` was tried. T5 already
ships tokens for this job: `<extra_id_0>` and its 99 siblings, the sentinels
used during pretraining. Placeholders are converted to sentinels for training
and back afterwards; serving never sees the difference. The script asserts the
round trip before training rather than trusting it.

Reported each epoch:

- **chrF**, not BLEU — Roman Urdu has no standardised spelling, and word-level
  BLEU would punish a correct answer for writing `hai` where the reference
  wrote `hay`.
- **placeholders kept** — the property the serving path depends on.

## Step 3 — draft our own text, and judge it

```bash
uv run python roman_urdu/make_drafts.py --model t5-roman-urdu --limit 50
```

Samples real explanation lines, **weighted half towards `Algorithm:`** because
that is the section the rule layer cannot reach and therefore the only one a
trained model exists to serve. Masks code exactly as serving does. Writes
`drafts.md`.

Then read it and answer one question:

> **Would correcting this be faster than writing it from scratch?**

- **Yes** → the domain corpus is worth building, and those drafts are its first
  rows. Correct 2,000–5,000, then fine-tune again on them.
- **No** → stop. That was the answer `opus-mt-en-ur` gave, and it saved a
  fortnight.

There is no automatic score for this on purpose. The non-English generation
literature reports that both automatic metrics and LLM-as-judge are unreliable
outside English; a fluent reader decides it in seconds.

---

## What has already been ruled out

| Tried | Result |
| --- | --- |
| Asking the C++ model for Roman Urdu | Ignored the instruction; 3 phrasings, 3 identical English replies |
| Asking it to translate one sentence | Produced **Persian**, then looped. Urdu is not in Qwen2.5's language list |
| `opus-mt-en-ur` as a draft generator | **0/43** placeholders survived; 9/50 drafts contained `%s`/`%d` from its localisation training data; "merge two sorted arrays" came back as "divide into two pieces" |
| A Roman Urdu dictionary as a lexicon | Covers **5.4%** of ERUPD tokens and misses every function word — it is a literary glossary, not a usage lexicon |
| Word-by-word substitution | Cannot work: Urdu is verb-final, English is not, so a bigger dictionary makes it worse |

Full reasoning in `docs/LANGUAGE_RESEARCH.md` and `docs/LANGUAGE_TRAINING.md`.

## What ships today without any of this

The backend already translates using sentence frames and guarantees code
survives: 100% placeholder integrity across 3,000 explanations, carrying 29.9%
of `Purpose:` lines. The remaining ~50% is multi-clause prose that no frame
reaches — which is the measured argument for this model, and the reason to
build it only if step 3 says the corpus is reachable.
