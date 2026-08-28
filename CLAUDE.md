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

## Where the work happens

**Data on the laptop, training on Kaggle.** They are different jobs and both are
needed: an API cannot train the model and a GPU cannot invent data.

The Linux checkout is **CPU-only** — `nvidia-smi` fails, and the GTX 970M behind
it is compute capability 5.2, so it has no bf16, no tensor cores, and less VRAM
than the T4 run peaks at. Do not propose `accelerate launch`, QLoRA loading, or
any bitsandbytes path there. What runs locally: tests, dataset builders, the
scoring and report scripts, prompt rendering, and llama.cpp inference over the
GGUFs. Install CPU torch as `torch==2.13.0+cpu` from
`https://download.pytorch.org/whl/cpu`, never the PyPI default, which drags in
~3 GB of unusable CUDA packages.

`uv sync` uninstalls anything not in the lockfile — use `uv pip install` and
`.venv/bin/python` directly, or the CPU stack disappears.

## Where things stand

Both repos are on branch `language`, nothing merged.

- training `d1663bd` · **206 tests**
- backend `9086453` · **106 tests**

Run before believing anything: `python3 -m pytest -q` and `ruff check`.
One known pre-existing lint error, `tests/test_analyze_endpoint.py:58` E501.

`tests/test_loss_masking_setup.py` needs `trl`, which is not installed in a
CPU-only checkout; `--ignore` it there. The other 206 run without a GPU.

**Read `.claude/skills/measuring-changes/SKILL.md` before running any
evaluation or writing any number into the report.** Every wrong conclusion this
project has reached came from the measurement, not the training.

## The C++ model — three runs, and what separates them

Qwen2.5-Coder-1.5B + QLoRA, merged, Q4_K_M GGUF (940 MB), served by llama.cpp on
**port 8081** (the API owns 8080). 17.7 tok/s was measured on the Mac; the Linux
box gets ~12.

Three checkpoints exist. **Compare them only on one machine in one session** —
the same weights score 7/55 on the Mac and 9/55 on Linux at `temperature: 0`.

| | phase 1 | phase 2 | v3 (`models/27aug01`) |
| --- | ---: | ---: | ---: |
| mixture rows | 66,103 | 66,898 | 56,668 |
| verified pairs | 0 | 159 | 253 |
| algorithmic rewriting | 10/60 (17%) | **25/60 (42%)** | **25/60 (42%)** |
| problems named | — | 16/55 | 11/55 |
| training time | — | 10.4 h | 6.8 h |

Two findings sit in that table:

1. **Introducing execution-verified data moved rewriting 17% → 42%**
   (p = 5.2e-04), from 159 pairs that were **1.9% of the mixture**. The 18,935
   asserted `improve` rows holding 37% of the loss budget did not.
2. **Scaling those pairs to 253 did nothing** (p = 1.0000). The gain came from
   *introducing* verification, not from scaling it.

The headline result about comprehension is unchanged and is still the finding
rather than a defect to fix — reliability and understanding are separable, and
the usual metrics measure the first while being read as the second. Valid JSON
100%, anchors 100%, problems noticed on 20 broken programs 13-20%, confidently
false descriptions 30-50%. Published evaluation chapter:
https://claude.ai/code/artifact/c234f2cd-4fda-461b-bd11-ec4fe8d6ac89

**A prompt change doubles defect finding for free.** Appending four sentences —
"This code may contain defects. Do not assume it is correct…" — takes problems
named from 8/55 to 16/55 and *reduces* defects invented in correct code from 1
to 0. It is `DEFECT_AWARE_SUFFIX` in `prompt.py`, applied at **inference only**
and only to `line_comments`/`explanation`/`review`; the training render is
deliberately untouched, because the measurement is of this wording given to a
model trained without it. Cost: false claims 7 → 8.

**The remaining gap is one transformation, not four data shapes.** Grouped by
what the rewrite must do: `table` (memoisation) 12/20, `accumulator` (tail
recursion → loop) 14/28, **`stack` (rebuild the call stack by hand) 3/20**.
`quicksort` is an array and `flood_fill` a grid; they fail beside the tree and
linked-list ones. Generating tree/list pairs will not fix it — and the corpus
has 20 tree functions and 0 linked-list ones among 582 drivable anyway.

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
- Stage 1 t5-small on Kaggle: **chrF 51.7 on ERUPD's own test split**. Re-measured
  on our register test split it is **51.34 chrF, 87.5% placeholders** - the same
  weights, a harder set, and the baseline stage 2 is compared against.
  Model at `kaggle_output/urdu_output/results(7)/t5-roman-urdu`.
- Drafts are correctable (21/43 placeholders, meanings survive, technical nouns
  stay English) — the premise `opus-mt` failed.

**Placeholders**: serving writes `⟦0⟧`; T5's vocabulary has no `⟦`, so training
converts to `<extra_id_0>` and back. Asserted before training, because getting
this wrong wastes an hour of GPU silently.

## Stage 2 is done, and it worked

**1,249 hand-annotated pairs**, 0 rejected, every placeholder set matching
between EN and RU. Both fixes the previous note listed are closed. Split
1,125 / 62 / 62 in `my_data_annotation/roman_urdu/data/`.

Three configs were trained from the stage-1 checkpoint — 20 epochs each, about
three minutes a run — and compared on the **held-out test split** with
`roman_urdu/compare_models.py`:

| | chrF | placeholders kept | register probes |
| --- | ---: | ---: | ---: |
| stage 1 | 51.34 | 87.5% | 4/5 |
| stage2-a (b16, 1e-4) | 73.66 | 92.9% | 5/5 |
| stage2-b (b8, 1e-4) | 74.60 | 96.4% | 5/5 |
| **stage2-c (b16, 3e-4)** | **76.14** | **100.0%** | **5/5** |

**Use `urdu_output/roman-model/t5-stage2-c`.** chrF +24.8 and placeholder
retention 87.5% → 100% — the register improved without trading away the
identifiers the product depends on, which was the failure mode to watch.

The harness measures stage 1 at 51.34 against the 51.7 recorded independently,
so the gain is not a measurement artefact. Test, not validation:
`load_best_model_at_end` selected on validation chrF, so only test is honest.

The sentence stage 1 actually failed, and what stage 2 does with it:

    stage1    ⟦0⟧ ko khud kar rahi hai.                        (lost "empty" and "true")
    stage2-c  Agar list⟦0⟧ empty ho to true return karta hai.

**A caveat and a correction.** 62 test pairs hold 56 placeholders, so the 100%
vs 96.4% gap between c and b is two placeholders — c wins on chrF, and the
placeholder difference should not be over-read. And 3e-4 beat the gentler 1e-4
that was recommended to avoid overwriting stage 1: at 1,125 rows over 20 epochs
there is not enough training for that forgetting to happen.

Earlier notes here said stage 1 renders "iterates" as *tayyar karta hai*
(prepares) and "is empty" as *saaf karta hai* (cleans). **Those were greedy
decoding artefacts.** With `num_beams=4` stage 1 says "iterates karta hai" - it
keeps the English verb rather than inventing a wrong Urdu one, and only the
"is empty" sentence genuinely failed.

```bash
python3 roman_urdu/make_corpus.py collect --outdir my_data_annotation/roman_urdu --pairs my_data_annotation/roman_urdu/pairs.jsonl
python3 roman_urdu/make_corpus.py split   --pairs my_data_annotation/roman_urdu/pairs.jsonl --outdir my_data_annotation/roman_urdu/data
uv run python roman_urdu/compare_models.py --models <ckpt> ... --labels ... --split test
```

`roman_urdu/corpus/batch_003.txt` holds 2,000 drafts, of which 1,000 are done as
`batch_003part1.txt`. Annotating the rest would reach the 2,000-5,000 band the
README asks for, but stage 2 already works at 1,249 — measure before annotating
more.

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

Loose ends, all outside the report:

1. **Roman Urdu is still at 250 of 500 blocks** — that is where the work was
   before the recursion detour, and the two known fixes in `batch_001` block 1
   and `batch_002` block 156 are still unfixed.
2. **The backend does not call `check_response`.** Until it does, contribution 3
   is true of the repository and not of the product.
3. **28 pairs are one field short of being verified.**
   `my_data_annotation/recursion_optimization/seed_todo.jsonl` holds them with
   `"stdin": ""` waiting; most need a single number. Append the filled rows to
   `seed.jsonl` and re-run `verify_optimization_pairs.py`. Of the 62 rejections
   there, only **9 were bad rewrites** — the rest were un-runnable, not wrong.
4. **The share experiment is built but not run.** `--repeat 30` puts the
   verified slice at 12.05% instead of 2.23%; the bundle is in `dist/` and the
   reading of each outcome is pre-registered in `model_improvement/REPORT.md`
   §3a-ii. Optional: the report stands without it.

## What not to try again, with the number that closed it

- **Generating tree or linked-list pairs from this corpus.** 20 tree functions,
  0 linked-list, among 582 drivable.
- **A bigger teacher for recursion→iteration.** Four proposers on the same 40
  corpus functions: GPT-OSS-120B **0/40**, nemotron-30b **0/40**,
  gemini-3.5-flash-lite **4/40**. Size does not predict yield; the cheap fast
  model won, at 14% over 250 functions where the historical figure was 1.5%.
- **Adding a `comments` task.** 47.3% of that field is a rewritten copy of the
  code — the format Phase 0 abandoned, preserving input lines only 14.5% of the
  time. Only 377 rows are prose carrying a real defect claim, not 18,681.
- **More epochs, or a bigger LoRA rank.** Improvement plateaued at step ~300 of
  1035; the adapter already carries 7.7 trainable parameters per supervised
  token and still does not overfit (eval loss sits *below* train).

## API providers

`.env` (gitignored) holds Azure `gpt-oss-120b`, four Gemini keys pooling to
~5,200 requests/day, and NVIDIA nemotron/muse. `scripts/probe_teacher.py` and
`build_optimize_dataset.py --backend api` read it.
**`gemini-3.5-flash-lite` is the one to use** — best yield *and* 6× the speed of
the flash models. `deepseek-v4-flash` times out and Gemini `pro` models are not
in the free tier. Spend the pool on generation and bulk classification, not on
recursion→iteration beyond what is already gathered.
