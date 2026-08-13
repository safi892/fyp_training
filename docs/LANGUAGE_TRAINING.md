# Training an English → Roman Urdu model for this domain

What exists, what does not, and the cheapest route from one to the other.

The short version: **most of the data already exists, and none of it is in our
domain.** That combination is good news — it means the expensive general
ability can be borrowed and only the register has to be built, which is a few
thousand pairs rather than a hundred thousand.

---

## 1. What is already available

### Direct English → Roman Urdu

| Dataset | Pairs | Domain | Notes |
| --- | ---: | --- | --- |
| **ERUPD** [1] | **75,146** | synthetic prompts + personal messaging groups | CC BY 4.0. The closest thing to what we need. Human-checked for code-switching and phonetic consistency, which is exactly the hard part |
| `Alisaeed001/englist-to-roman-urdu-finetune` [5] | 513 | mixed | too small to train on, useful as a sanity set |
| `Redgerd/roman-urdu-alpaca-qa-mix` [6] | 1,022 | instruction/QA | Alpaca-style, half Roman Urdu |

### Urdu ↔ Roman Urdu (transliteration, for the two-hop route)

| Dataset | Pairs | Notes |
| --- | ---: | --- |
| **Roman-Urdu-Parl** [2] | **6.37 million** | The large one. 42,927 Roman-Urdu vocabulary, crowd-annotated |
| **Dakshina** (Google) [3] | ~10,000 | Smaller but domain-diverse, which is why [3] pairs the two |

### English → Urdu (the first hop)

`Helsinki-NLP/opus-mt-en-ur` (small, purpose-built), several mBART and T5
fine-tunes on the Hub [7][8].

### The gap

**None of it is technical.** ERUPD is conversational and messaging text; the
transliteration corpora are general. A model trained on any of them will speak
fluent casual Roman Urdu and will not sound like a developer explaining code —
which is the register problem measured in `LANGUAGE_RESEARCH.md`, unsolved by
any dataset on this page.

That gap is ours to fill, and it is small.

---

## 2. The recipe: borrow the language, build the register

Two-stage fine-tuning. The first stage is the expensive one and someone else
has already paid for it.

```
Stage 1   ERUPD, 75,146 pairs          -> general English -> Roman Urdu
Stage 2   our corpus, 2,000-5,000      -> the developer register
```

Stage 2 is the whole contribution. It is also the only part that has to be
created by hand, and 2–5k pairs is a fortnight of evenings rather than a
research programme.

### Building stage 2 without writing 5,000 sentences

Use the two-hop as a **generator**, then correct rather than compose:

```
our English explanations
    -> Urdu            (opus-mt-en-ur)
    -> Roman Urdu      (transliteration, Char-BLEU ~96 [3])
    -> read and fix    <- the only manual step
```

Correcting a draft is several times faster than translating from scratch, and
it is where the register gets fixed: the machine draft will say the formal
Urdu word for "pointer", and the correction is to put `pointer` back.

Sample deliberately rather than taking the first 5,000. From the corpus
measurements: `Purpose:` and `Output:` lines are short and templated,
`Algorithm:` lines are the multi-clause prose that rules cannot reach. Weight
the sample **towards `Algorithm:`** — it is 50.2% of what currently falls
through and the frames already cover the easy half.

### Train on masked text

Mask code fragments *before* training, not just at inference:

```
source   Divide ⟦0⟧ by 10 to drop the last digit of ⟦1⟧
target   ⟦0⟧ ko 10 se divide karein taake ⟦1⟧ ka aakhri digit hat jaye
```

The model then never sees an identifier and learns the placeholders are opaque
tokens to carry across. Placeholder integrity becomes high *by construction*
rather than only being checked afterwards — and the check stays, because "by
construction" is how the last two bugs got in.

---

## 3. Model choice

| Candidate | Size | For | Against |
| --- | ---: | --- | --- |
| **`t5-small`** | 60M | What ERUPD's own authors used [1]. Latin-script output matches Roman Urdu natively. Trains on a free T4 in an hour | English-centric vocabulary |
| `google/mt5-small` | 300M | Genuinely multilingual, better subword coverage | 5× the size; heavier next to a 940 MB code model |
| `Helsinki-NLP/opus-mt-en-ur` | small | Already knows English→Urdu | Its decoder vocabulary is **Urdu script**. Asking for Latin output fights the tokenizer |

**Start with `t5-small`.** It is the precedent, it is small enough to serve
next to the existing model, and Roman Urdu is Latin script so the tokenizer is
not being asked to do anything strange.

Format as a prefixed seq2seq task, the way T5 expects:

```
input   translate English to Roman Urdu: Counts the number of digits in ⟦0⟧
target  ⟦0⟧ mein kitne digits hain ye ginta hai
```

---

## 4. Evaluation

Standard MT metrics are the wrong instrument here and the literature says so —
automatic scores could not reliably judge non-English generation, and
LLM-as-judge was unstable across languages [4].

| Measure | How | Why |
| --- | --- | --- |
| **Placeholder integrity** | already built (`masking.py`) | Decidable, gates every response, catches the failure that matters |
| **chrF** or **Char-BLEU** | `sacrebleu` | Character-level survives Roman Urdu's non-standard spelling; word-level BLEU would punish a correct answer for spelling `karta` differently |
| **Round-trip** | Roman Urdu → Urdu → English, compare to source | Cheap screen for gross failures, blind to subtle ones |
| **Human rating** | a fluent reader, sample of 100 | The only real measure of whether it reads like a developer wrote it |

**Do not score against one fixed spelling.** Roman Urdu has no standard
orthography [2][3]; marking `hai` against `hay` measures conformity to an
arbitrary choice, not quality.

Report coverage separately from quality, as the rule layer already does: how
many lines were translated at all, then how good those were.

---

## 5. Effort, honestly

| Step | Time |
| --- | --- |
| Get ERUPD, verify licence and format | half a day |
| Two-hop generation over sampled explanations | a day |
| **Hand-correct 2,000–5,000 pairs** | **the bulk of it — one to two weeks** |
| Stage 1 + stage 2 fine-tune on a free T4 | a day |
| Evaluation harness and the human sample | two days |

Roughly **two to three weeks**, and the corpus is where nearly all of it goes.

The corpus is also the part worth publishing. A Roman Urdu parallel set for
code explanations does not exist; a fine-tuned `t5-small` is a Tuesday.

---

## 6. Before starting, check two things

**Is ERUPD actually downloadable?** The paper states CC BY 4.0 but the abstract
does not name a repository. If it cannot be obtained, stage 1 has to come from
the smaller Hub datasets [5][6] plus the transliteration route, and the
estimate grows.

**Does the two-hop draft come out usable?** Run fifty explanations through
`opus-mt-en-ur` → transliteration and read them. If the drafts need rewriting
rather than correcting, the generator is not saving any time and the plan
should change before two weeks go into it, not after.

That check is half a day and it is the one that decides whether this is a
fortnight or a term.

---

## References

1. [ERUPD — English to Roman Urdu Parallel Dataset](https://arxiv.org/abs/2412.17562) — 75,146 pairs, CC BY 4.0, synthetic plus messaging data, human-checked for code-switching
2. [Roman-Urdu-Parl](https://dl.acm.org/doi/10.1145/3464424) — 6.37M Roman-Urdu ↔ Urdu pairs
3. [Low-Resource Transliteration for Roman-Urdu and Urdu](https://arxiv.org/abs/2503.21530) — Char-BLEU 96.37 / 97.44, uses Roman-Urdu-Parl with Dakshina
4. [Evaluating Non-English Developer Support in ML for SE](https://arxiv.org/html/2605.05902v1) — automatic metrics unreliable outside English
5. [`Alisaeed001/englist-to-roman-urdu-finetune`](https://huggingface.co/datasets/Alisaeed001/englist-to-roman-urdu-finetune)
6. [`Redgerd/roman-urdu-alpaca-qa-mix`](https://huggingface.co/datasets/Redgerd/roman-urdu-alpaca-qa-mix)
7. [`abdulwaheed1/english-to-urdu-translation-mbart`](https://huggingface.co/abdulwaheed1/english-to-urdu-translation-mbart)
8. [`HaiderSultanArc/t5-small-english-to-urdu`](https://huggingface.co/HaiderSultanArc/t5-small-english-to-urdu)
