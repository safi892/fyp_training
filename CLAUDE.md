# Project context

Read this first. It is the handover between sessions: what exists, what was
measured, and what is half-done. Everything here is a measured number or a
decision with a reason — keep it that way, and correct it when it goes stale.

## Three separate projects, kept separate on purpose

| | Path | Job |
| --- | --- | --- |
| **training** | `/Volumes/Data/fyp8th_clean` (here) | dataset, QLoRA, evaluation, GGUF |
| **backend** | `/Volumes/Data/saffi/fyp_backend` | FastAPI serving the mobile app |
| **language** | `roman_urdu/` here + `app/model_processing/` there | English → Roman Urdu |

A session holding two of these ends up proposing training changes to fix
serving bugs. Work in one at a time.

## Where things stand

Both repos are on branch `language`, nothing merged.

- training `c657951` · **169 tests**
- backend `9086453` · **106 tests**

Run before believing anything: `python3 -m pytest -q` and `ruff check`.
One known pre-existing lint error, `tests/test_analyze_endpoint.py:58` E501.

## The C++ model — finished, measured, not being changed

Qwen2.5-Coder-1.5B + QLoRA, merged, Q4_K_M GGUF (940 MB, 17.7 tok/s CPU),
served by llama.cpp on **port 8081** (the API owns 8080).

The headline result, all from **one run**:

| | |
| --- | ---: |
| valid JSON | 100% |
| anchors attached to real lines | 100% |
| problems noticed on 20 broken programs | **13%** |
| confidently false descriptions | **50%** |

That is the finding, not a defect to fix: reliability and understanding are
separable, and the usual metrics measure the first while being read as the
second. Published evaluation chapter:
https://claude.ai/code/artifact/c234f2cd-4fda-461b-bd11-ec4fe8d6ac89

Other measured results worth not re-deriving:

- **Renaming every variable to something misleading costs 0 points** (94% → 94%).
  Single letters cost 12. Published comparison: GPT-4o drops ~29.
- **Base model ablation**: untuned Qwen produced 0/20 usable JSON and 68% anchor
  validity against the fine-tune's 20/20 and 100%. Fine-tuning bought *format*,
  not comprehension (9/55 vs 7/55 problems named — and the base had 3.3× more
  text scored, so that gap favours the base by construction).
- **Optimisation** is latent in the base model: trained wording 0/3, explicit
  "use memoization" 3/3. No dataset was needed.
- **Defect blindness is capability, not prompting**: three phrasings moved one
  sample of eight. A verified buggy-code corpus is the only route, ~2 weeks,
  deliberately out of scope.
- **A verified recursion→iteration corpus was attempted and abandoned.**
  5.8 GPU-hours, 130 of 582 functions attempted, **2 verified — a 1.5% yield**.
  Dominant rejection was "still recursive", 57 of 130. Worse, both survivors
  were mechanical `std::stack` simulations with no complexity gain, and one
  carried a `return -1; // Placeholder` path that the generated inputs never
  reached. Do not restart this: the probe already showed explicit wording gets
  the real transformation for free. Evidence in `kaggle_output/verified_labels/`.
- **Retried with the better wording, and it was worse.** The stack wording was
  the obvious suspect, so the run was repeated with the memoisation wording the
  probe scored 3/3, on only the 335 functions with overlapping subproblems:
  **0 verified from 20 functions × 16 samples**, 16 of 20 rejected as "still
  recursive", 4 originals not even compiling. The probe's 3/3 was on three
  hand-written textbook functions; these are real submissions with their
  authors' identifiers. Same lesson as the 3/60 recursion result — a capability
  number measured on code you wrote yourself is not a serving number.
  Evidence in `kaggle_output/results(9)/`.
- **Recursion into a loop, on 60 real submissions** with their authors' own
  identifiers: shipped wording **3/60** (all three the same `gcd`), naming the
  container **10/60**, a worked example 6/60. Hand-written samples said 47-100%
  for the same model — a capability number measured on code you wrote yourself
  is not a serving number.
- **Comments and explanations, read back against the code**: format holds
  (JSON 89/90, anchors 636/644 on 92 in-distribution programs) while nine of
  twenty explanations on tree and graph code carry a false statement. That 45%
  is a worst case: those programs are 45-58 lines against a corpus p50 of 14,
  using shapes that are 1.6-1.9% of the training data. In-distribution the same
  check gives 99% anchors and 1/46 loops wrongly called recursive.

## The anchoring design, which explains most of the code

Comments are `{line, code, comment}` records, never a rewritten file. The
quoted line is checked against the submission, so an invented comment is
*detectable*. Line numbers are wrong ~75% of the time and quotes are right
~100%, so anchors are relocated by their quote.

`needs_review` keeps its name and type because an Android client reads it.
The response contract is additive only.

**The same move now covers the other two fields.** `checked_response.check_response`
composes three checks that each already existed alone: `repair_anchors` for the
quoted line, `verification.verify` for `improved_code` (compile both, run both,
compare), and `claim_checks.check_claims` for prose the source refutes.
`verification.py` had 23 passing tests and **no callers** before this — the
report already lists it as contribution 3.

Over 112 saved responses it drops 20 anchors, 1 comment ("BFS queue for
flood-filling" on a `stack<>` line) and flags 2 false recursion claims, all
hand-checked. Precision was **1 in 3** until it ran on real output: `prints the
phrase "I love Recursion"` is correct prose about a loop, and "stack overflow"
is the runtime stack, not a `std::stack`. Both excluded, both tested. A filter
that drops correct output is worse than no filter.

It catches **1 of the 9** wrong explanations, and `docs/DETECTABILITY.md` says
so in a heading rather than a footnote. Behaviour is decidable and a quote is a
string; free prose is checkable only where it happens to make a claim the source
answers.

**Not wired into the backend yet** — separate repo, separate session.

## Language work — in progress, this is where you are

Roman Urdu. `roman_urdu/README.md` has the full three-step pipeline.

**Ruled out, do not retry:**

| Tried | Result |
| --- | --- |
| Asking the C++ model for Roman Urdu | Ignored it — 3 phrasings, 3 identical English replies |
| Asking it to translate one sentence | Produced **Persian**, then looped. Urdu is not in Qwen2.5's languages |
| `opus-mt-en-ur` as draft generator | 0/43 placeholders survived; `%s`/`%d` from its localisation training data; "merge two arrays" → "divide into two pieces" |
| A Roman Urdu dictionary as lexicon | Covers 5.4% of tokens, missing every function word — literary glossary, not usage |
| Word-by-word substitution | Cannot work. Urdu is verb-final; a bigger dictionary makes it worse |

**Works:**

- `urdu/ERUPD_NMT.csv` — 75,146 English→Roman Urdu pairs, 66,956 clean. Teaches
  the *language*. Contains "integer" **0** times against 8,353 in our corpus, so
  it teaches none of the *register* — that gap is stage 2.
- Stage 1 t5-small on Kaggle: **chrF 51.7, placeholders kept 98.3%**.
  Model at `kaggle_output/urdu_output/results(7)/t5-roman-urdu`.
- Drafts are correctable (21/43 placeholders, meanings survive, technical nouns
  stay English) — the premise `opus-mt` failed.

**Placeholders**: serving writes `⟦0⟧`; T5's vocabulary has no `⟦`, so training
converts to `<extra_id_0>` and back. Asserted before training, because getting
this wrong wastes an hour of GPU silently.

**Where the user is right now**: hand-correcting drafts in
`my_data_annotation/roman_urdu/`. 250 blocks done, 248 usable. Target 500, then
train and measure, then decide whether 2,000 is worth it.

Two known fixes waiting there: `batch_001` block 1 (wrote "lists" instead of
keeping `⟦0⟧`) and `batch_002` block 156 (RU is a translation of a different
sentence — delete it).

```bash
python3 roman_urdu/make_corpus.py collect --outdir my_data_annotation/roman_urdu --pairs my_data_annotation/roman_urdu/pairs.jsonl
python3 roman_urdu/make_corpus.py split   --pairs my_data_annotation/roman_urdu/pairs.jsonl --outdir my_data_annotation/roman_urdu/data
```

`roman_urdu/corpus/batch_003.txt` holds 2,000 more unique drafts, unstarted.

The backend already ships a rule layer: sentence frames carrying 29.9% of
`Purpose:` lines with **100% code integrity** across 3,000 explanations. The
other ~50% is multi-clause prose no frame reaches — the measured argument for
the trained model.

## How this project works, and why

Every capability was **probed before it was built**. Twice the probe said "the
model can already do this, ask better" and twice it said "no, and here is the
evidence". Both answers saved weeks. Do not start building a dataset without
running the probe first.

Scoring has now been wrong **seven** times, always flattering the model. The
four found in one session: a keyword matched inside a comment ("// cache next
node" scored an unchanged function as memoised), a closed list of verbs that
missed "recursively sorting", a code pattern matched against prose so the check
could only ever return zero, and a report naming pairs before filtering so it
printed one program's source beside another's comments. Assume the next one
exists and is in the same direction.

The original three: scoring has been wrong three times, always flattering the model — a single word
counted as understanding ("compute midpoint **to avoid overflow**" scored as
finding an overflow bug). Every awarded point now ships with the phrase that
earned it, and `tests/test_hard_scoring.py` guards it. Distrust any metric you
cannot see the evidence for.

Two bugs were found by running over real data while every test passed,
including one where the integrity *checker itself* was wrong and refused 836
valid rows. Tests passing is not the same as the thing working — run it on the
corpus.

## What is left

The report. `docs/WRITEUP_GUIDE.md` maps every chapter to the file that already
holds its material, and `docs/DETECTABILITY.md` is a written chapter waiting to
be placed. All development phases in `PLAN.md` are finished or were measured
into irrelevance. Do not start new capability work without asking.

Two loose ends, both small and both outside the report:

1. **Roman Urdu is still at 250 of 500 blocks** — that is where the work was
   before the recursion detour, and the two known fixes in `batch_001` block 1
   and `batch_002` block 156 are still unfixed.
2. **The backend does not call `check_response`.** Until it does, contribution 3
   is true of the repository and not of the product.
