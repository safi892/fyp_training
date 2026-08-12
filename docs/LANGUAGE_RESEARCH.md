# Roman Urdu output: research and recommendation

**Question asked:** should the multilingual capability be a separate model, or
part of the existing one?

**Short answer:** separate — but not the separate thing it first looks like.
Not a second *code* model. A translation *stage* that runs after the code model
and never touches the code.

The reasoning is below, in the order it was arrived at: what the model can
actually do, what the literature reports, and what the existing architecture
already makes easy.

---

## 1. What the model can actually do (measured)

Before designing anything, the model was asked. `scripts/probe_language.py`,
results in `test_results/language_probe.json`.

| Probe | What was asked | Result |
| --- | --- | --- |
| `roman_urdu_plain` | the product's own prompt + "write the explanation in Roman Urdu" | **English** |
| `roman_urdu_with_example` | same, with a worked example of the target style | **English** |
| `urdu_script` | "write the explanation in Urdu" | **English** |
| `translate_plain` | no code at all — just translate one English sentence | **Persian, then a repetition loop** |
| `translate_few_shot` | same, with an English→Roman Urdu example given | **Persian** |

**0 of 5 replies were Roman Urdu.**

Two separate failures, and the second is the important one:

- On the **code task**, the language instruction is ignored completely. All
  three replies are byte-identical English in the trained
  `Purpose / Input / Output / Algorithm` shape. The fine-tuning locked the
  output format hard — which the base-model ablation showed is the main thing
  the training bought, working against us here.
- On **translation alone**, with the code task removed, it produces *Persian*
  and then loops. Persian and Urdu share a Perso-Arabic script, so this is the
  model reaching for the nearest thing it knows. It does not know Urdu.

That second result settles the architecture question. If the model cannot
translate a sentence it wrote itself, no amount of prompt work on the code task
will get there.

**Consistent with the documentation:** Qwen2.5 advertises support for 29+
languages — Chinese, English, French, Spanish, Portuguese, German, Italian,
Russian, Japanese, Korean, Vietnamese, Thai, Arabic and others. **Urdu is not
among them.**

---

## 2. What the literature says

**Non-English comment generation degrades badly, even in supported languages.**
A 2026 study evaluated five code LLMs (CodeGemma, CodeLlama, CodeQwen1.5,
GraniteCode, StarCoder2) generating comments in Dutch, Greek, Polish, Chinese
and English. Linguistic errors rose sharply outside English — **15.1× for
Greek** — and Chinese performed worst *despite being in the training data*.
Hallucination was the most common semantic error category. [1]

The same study found that **automatic metrics could not reliably assess
non-English output**, and LLM-as-a-judge was unstable across languages. Human
annotation remained necessary. That is a real cost to plan for: the
English-side evaluation harness in this project does not transfer.

**Roman Urdu is harder than Urdu.** It is Urdu written in Latin script with
**no standardised spelling**, so the same word appears many ways. There is no
single correct target, which complicates both training data and marking. [2][3]

**But transliteration is close to solved.** Urdu ↔ Roman-Urdu transliteration
with a fine-tuned m2m100 reaches **Char-BLEU 96.4 (Urdu→Roman) and 97.4
(Roman→Urdu)**, beating both RNN baselines and GPT-4o Mini. [3]

That last finding is the useful one: it says **do not treat Roman Urdu as a
translation target.** Treat it as a transliteration of Urdu, which is a
well-supported language, and the hard part becomes a solved sub-problem.

---

## 3. Why the existing architecture makes this easier than expected

A comment in this system is not a sentence. It is a record:

```json
{ "line": 6, "code": "total /= 10;", "comment": "Remove the least-significant digit." }
```

Only **one** of those three fields is prose. `line` is a number and `code` is a
verbatim quote of the user's own C++, which is what the whole anchoring
guarantee rests on.

So a translation stage:

- touches **only** `comment` and `explanation`
- **cannot** break anchoring, because it never sees `code` or `line`
- runs **after** anchors have already been validated in English

This is worth stating plainly because it is the strongest argument against
putting the language inside the code model. If the model generated Roman Urdu
directly, it would be generating the `code` field in the same breath — and a
model that is translating is a model that might tidy a quoted line. The
ablation already measured what that costs: the base model, which reformats
quotes, keeps only **68%** of its anchors against **100%** for the tuned one.

Anchor validity is this project's central claim. It should not be put at risk
to add a language.

---

## 4. The options

| Option | What it means | Cost | Risk |
| --- | --- | ---: | --- |
| **A — Train the code model to answer in Roman Urdu** | new task tag, bilingual corpus, retrain | weeks | **High.** No corpus exists; Urdu is not in the base model; [1] says quality drops sharply even for supported languages; anchoring is exposed |
| **B — Second code model for Urdu** | train and serve a separate adapter | weeks | **High.** Same data problem as A, plus 2× serving memory and 2× everything to maintain |
| **C — Translation stage after generation** | translate `comment` / `explanation` only | days | **Low.** Code model untouched; anchoring untouched; failure is contained to one field |
| **D — Expand the phrase dictionary already in the backend** | extend `translation_service.py` | hours | **Very low**, but only covers a fixed vocabulary |

**A and B are the same bet** — that a 1.5B model can be taught a language it
does not have, from a corpus that does not exist, without damaging the one
property the project is built on. The measurements say do not take it.

---

## 5. Recommendation

**Option C, with D as the first increment.**

```
C++  →  [ code model, English ]  →  anchors + explanation  →  validated
                                                                  ↓
                                             [ translation stage ]  →  Roman Urdu
                                              comment / explanation only
```

**The seam already exists.** `app/services/translation_service.py` in the
backend was written with exactly this in mind, and says so:

> "The current implementation is a dictionary/phrase fallback; a trained
> translation model can later replace `to_roman_urdu` without changing
> callers."

Nothing calling it has to change.

**Start with D, because the output has a fixed shape.** The tuned model always
emits `Purpose: … Input: … Output: … Algorithm: …`. That scaffolding can be
translated once, exactly, and only the variable content needs real translation.
Free-form MT is the hard version of a problem that is partly templated here.

**Then C, as two hops rather than one**, following [3]:

```
English  →  Urdu (well-supported MT)  →  Roman Urdu (transliteration, ~96 Char-BLEU)
```

Candidate models, both CPU-runnable:

| Model | Covers | Size | Note |
| --- | --- | ---: | --- |
| `Helsinki-NLP/opus-mt-en-ur` | English→Urdu only | small (6-layer transformer) | purpose-built for one direction; the lightest option |
| `facebook/nllb-200-distilled-600M` | 200 languages incl. `urd_Arab` | ~2.5 GB | heavier than the code model itself — check before committing |

Size matters here: the whole point of the Q4 build was a 940 MB model at 17.7
tok/s on CPU. A 2.5 GB translator next to it changes the deployment story, so
`opus-mt` is the better default and NLLB the fallback if quality demands it.

**Adding a third language later** costs one more MT model on this design, and a
retrain on option A or B. That asymmetry is the argument on its own.

---

## 6. Training a translator for this domain

The obvious objection to option C is that a general MT model is a blunt
instrument for the job. That objection is correct, and the numbers say so.

### The domain is roughly ten times narrower than ordinary English

Measured over the 18,942 explanations in `cleaned/merged_cleaned.jsonl`:

| Vocabulary | Share of all text |
| ---: | ---: |
| top 500 words | **81.4%** |
| top 1,000 words | 89.5% |
| top 2,000 words | **95.2%** |

General English needs 10,000–20,000 word types to reach 95%. This needs 2,000.
The text is also templated rather than free — `"Purpose: Compute the …"` opens
**2,966** of them, `"Algorithm: The function …"` another 2,264.

A narrow, repetitive, templated domain is the case where a small purpose-built
model beats a large general one, and where a few thousand training pairs are
enough rather than a few million.

### Register, not grammar, is the real problem

`opus-mt-en-ur` and NLLB were trained on news and parliamentary text. Given
*"this function returns a pointer to the array element"*, they will faithfully
render **function**, **pointer**, **array** and **element** as formal literary
Urdu — words no working developer in Pakistan says out loud.

Actual Roman Urdu developer speech is code-switched, keeping the technical
nouns in English:

> Ye function array ko sort karta hai aur pointer return karta hai.

**17 of the 60 most frequent words in the corpus are exactly those terms** —
`input, output, algorithm, int, string, vector, value, integer, node, returns,
array, element, index, function, pointer, list, return`. A general model gets
them grammatically right and pragmatically wrong, which reads worse than
leaving them in English would have.

This is the argument for training something of our own. It is not that
off-the-shelf Urdu is poor; it is that off-the-shelf Urdu is the wrong
register, and no amount of decoding parameters fixes that.

### Use the two-hop to build data, not to serve requests

```
BUILD TIME, once
    18,942 English explanations
        -> Urdu (MT)  -> Roman Urdu (transliteration, ~96 Char-BLEU [3])
        -> corrected by hand on a sample
        = a parallel corpus that does not currently exist

RUN TIME, every request
    English -> [ small domain model ] -> Roman Urdu       one hop
```

The two-hop earns its place once, offline, where its errors are cheap because
the output is being edited anyway. At serving time it would double the latency
and compound two models' mistakes into one answer.

For a domain this templated, 2,000–5,000 corrected pairs is a reasonable
target, not the whole corpus. Candidate starting points: fine-tune
`opus-mt-en-ur` on the domain data, or a small mT5. Domain-adapting a model
that already knows Urdu grammar is far cheaper than teaching grammar from
scratch.

### The checkable property: placeholder integrity

Everything in this project rests on a property that can be checked
mechanically. For comments that property is anchor validity. Translation has
an exact analogue, and it should be built before any model is trained.

Identifiers and code fragments are masked out before translation and restored
afterwards:

```
before   Divide `total` by 10 to drop the last digit of arr[j]
masked   Divide ⟦0⟧ by 10 to drop the last digit of ⟦1⟧
                          -> translate ->
after    ⟦0⟧ ko 10 se divide karein taake ⟦1⟧ ka aakhri digit hat jaye
restore  `total` ko 10 se divide karein taake arr[j] ka aakhri digit hat jaye
```

Every placeholder must return **present, exactly once, unchanged**. That is
decidable without a fluent reader, and it catches the failure that would
actually hurt: a translator quietly rewriting `arr[j]`, renaming `total`, or
dropping a symbol because it looked like noise. A translation that fails the
check is discarded and the English is returned, the same way an unverifiable
optimisation returns the user's own code.

It has a second benefit. Masking removes exactly the tokens a general MT model
handles worst, so it improves off-the-shelf output as well as protecting it —
which means the check is worth building even if no model is ever trained.

### Two tiers

| | Work | What it gets |
| --- | --- | --- |
| **Tier 1** | placeholder masking, exact translation of the fixed scaffolding (`Purpose:` → `Maqsad:`), and the ~500 words covering 81% | A working feature, deterministic and offline, replacing a 20-phrase dictionary. Days. |
| **Tier 2** | build the parallel corpus, fine-tune a small seq2seq on it | A Roman Urdu parallel set for code explanations, which does not exist. One to two weeks. |

Tier 1 ships and is testable. Tier 2 is the part with novelty in it, and is
honestly a second project rather than a finishing touch — the corpus is the
contribution, and building a corpus is where the time goes.

---

## 7. Where the work lives

The three parts of this project stay separate, and this does not change that:

| Piece | Repository | Why |
| --- | --- | --- |
| Code model, training, evaluation | `fyp8th_clean` | unchanged — no retrain, no new task |
| Translation stage | `fyp_backend` | it is a serving concern, and the interface is already there |
| Mobile app | unchanged | `output_language` is already in the request schema |

The API contract already carries `output_language: english | roman_urdu`, so
the client needs no change either.

---

## 8. What to measure, if this is built

The English harness does not transfer — [1] is explicit that automatic metrics
fail on non-English output. Plan for human judgement:

- **Placeholder integrity** — every masked identifier returns present, once,
  unchanged. Decidable without a human, so it can gate every response.
- **Anchor validity after translation** must still be 100%. It should be, by
  construction, since `code` is never touched — but assert it, because "by
  construction" is how the earlier bugs got in.
- **Meaning preserved**, rated by a fluent reader on a sample. There is no
  automatic substitute.
- **Round-trip check** as a cheap screen: Roman Urdu → Urdu → English, then
  compare to the original English. It catches gross failures without a human,
  and catches nothing subtle.
- **Spelling variance is not an error.** Roman Urdu has no standard
  orthography [2][3]; marking against one fixed spelling would measure
  conformity to an arbitrary choice.

---

## References

1. [Evaluating Non-English Developer Support in Machine Learning for Software Engineering](https://arxiv.org/html/2605.05902v1) — five code LLMs, five languages; 15.1× linguistic error increase for Greek; automatic metrics unreliable outside English
2. [Roman Urdu as a Low-Resource Language](https://aclanthology.org/2025.lowresnlp-1.9.pdf) — non-standardised orthography and its consequences
3. [Low-Resource Transliteration for Roman-Urdu and Urdu Using Transformer-Based Models](https://arxiv.org/abs/2503.21530) — Char-BLEU 96.37 / 97.44, outperforming GPT-4o Mini
4. [Qwen2.5 multilingual support](https://qwenlm.github.io/blog/qwen2.5/) — the 29+ supported languages; Urdu is not listed
5. [facebook/nllb-200-distilled-600M](https://huggingface.co/facebook/nllb-200-distilled-600M) — 200 languages including `urd_Arab`
6. [Open-source translation models for embedded use](https://picovoice.ai/blog/open-source-translation/) — size comparison; NLLB-600M at ~2.5 GB is too large for mobile
