# Model improvement work

Everything here is an attempt to make the model *better*, kept separate from
`test_results/`, which records what the model **is**. Nothing in this folder
changes the model on its own — two of the three steps produce a number, and one
produces training data that a Kaggle run would then learn from.

Background and the measurements these follow from: `docs/PHASE2_INVESTIGATION.md`.

## The one thing to understand first

**The API and the GPU do different jobs. You need both.**

| | API (`.env`) | Kaggle GPU |
| --- | --- | --- |
| Job | **make the data** | **train on the data** |
| Runs on | this laptop (network calls only) | Kaggle |
| Costs | API quota | GPU hours |
| Produces | `.jsonl` files | a LoRA adapter |

An API can never train the model. A GPU can never invent new data.

---

## step3_prompt/ — does asking about correctness help?

**No training. No API. Just a different question, asked of the model we already
have.**

The trained instruction asks for "line-by-line comments" and "explanation".
Both are *describing* jobs, and 99.97% of the training explanations follow a
fixed `Purpose / Input / Output / Algorithm` form that has no slot for "this is
broken". So the model never says it.

`scripts/probe_defects.py` asks the same 20-ish broken programs three ways:

| phrasing | what it adds |
| --- | --- |
| `trained_wording` | nothing — the control, exactly what the product sends today |
| `describe_effect` | asks what each line *does* rather than what it is for |
| `assume_nothing` | asks the model not to assume the code is correct |

**Already measured on the phase-1 model** (`test_results/defect_probe.md`):

| phrasing | problems named | false claims (of 8) | defects invented in *correct* code (of 4) |
| --- | :---: | :---: | :---: |
| `trained_wording` | 3/23 | 4 | 0 |
| `describe_effect` | 3/23 | 4 | 0 |
| **`assume_nothing`** | **5/23** | **3** | **0** |

So a wording change already bought +2 on phase 1 *without* inventing defects in
correct code — which is the constraint that matters, because correct code is the
product's normal input and imagining bugs in it is a worse failure than missing
real ones.

This run repeats it on **phase 2**, which has never been probed this way.

```bash
export PATH="$HOME/Downloads/saffi_fyp/llama.cpp/build/bin:$PATH"
.venv/bin/python scripts/probe_defects.py \
  --gguf models/gguf/qwen-cpp-review-v2-q4_k_m.gguf \
  --tokenizer models/Qwen2.5-Coder-1.5B-Instruct \
  --output model_improvement/step3_prompt/defect_probe_phase2 --port 8099
```

**How to read it:** if `assume_nothing` again beats `trained_wording` while
keeping the last column at 0, change the served instruction. That is a one-line
product change worth more than a training run, because it costs nothing.

---

## step4_verified_pairs/ — more of the thing that already worked

**API yes. GPU later, to train on what this produces.**

This is the only improvement with direct evidence behind it. Phase 2 added 58
execution-verified `optimize` pairs, upsampled to 795 rows — **1.19% of the
corpus** — and the model's rate of genuine algorithmic transformation went
**17% → 40%** (p = 5.2e-04, contamination-controlled). Meanwhile the `improve`
task's 18,935 unverified rows, holding **37% of the entire loss budget**, taught
`const`-sprinkling: 64% of its pairs leave control-flow token counts identical.

Verification of the target beat volume by three orders of magnitude. So: make
more verified pairs.

### Why this needed a code change

`scripts/build_optimize_dataset.py` had two backends, both using the *small
local model* as the proposer:

    --backend llama   llama-server on CPU
    --backend hf      transformers on a GPU

A weak proposer is not fatal — the gate decides what exists, not the proposer —
but the yield was punishing. `CLAUDE.md` records **5.8 GPU-hours, 130 functions
attempted, 2 verified: a 1.5% yield.**

Added `--backend api`, so a hosted model proposes instead. The gate is
unchanged, the prompt asks for the same thing in the same words, and a pair
still only exists if it **compiled, ran, and printed exactly what the original
printed**. A stronger proposer raises the yield without weakening the guarantee.

```bash
.venv/bin/python scripts/build_optimize_dataset.py \
  --backend api --provider azure-saffi --model gpt-oss-120b --rpm 10 \
  --limit 60 --samples 2 --task optimize \
  --out model_improvement/step4_verified_pairs/pairs_api.jsonl
```

Credentials come from the same `.env` that `scripts/probe_teacher.py` reads, so
a provider that works for one works for the other. `--rpm 10` matches the free
tier's throttle; raise it if yours allows more. The run is **resumable** —
finished functions are skipped, so it can be stopped and restarted.

### Reading the log

    [  1/60] kept  0  unchecked: original: exit -11:

`unchecked` means the **original** program crashed, so there was nothing to
compare a rewrite against. That is the gate refusing to guess, not a failure of
the model. Other reasons you will see:

| reason | meaning |
| --- | --- |
| `still recursive` | the rewrite kept the recursion — the usual failure |
| `no code found` | the reply had no extractable C++ |
| `output differs` | it compiled and ran but computed something else |
| `KEPT` | compiled, ran, identical output — a real pair |

### What to do with the output

```bash
uv run python scripts/add_verified_pairs.py --repeat 5   # fold into the mixture
uv run python scripts/build_task_mixture.py              # rebuild
# upload to Kaggle, train once
```

**Aim the next batch at the failures.** Phase 2 scores 4/4 on tabulation
problems (`grid_paths`, `coin_change`, `binomial`) and **0/4** on every case
needing explicit stack simulation — `reverse_list`, `binary_search`,
`tree_height`, `quicksort`, `flood_fill`. Generating more DP examples will not
move those. Generate for trees, linked lists, and partition.

---

## Not started: fixing `improve`, and adding `comments`

Both are edits to `scripts/build_task_mixture.py`, so they cost **one** Kaggle
run between them, not two.

1. **Drop the `improve` rows that change nothing structural.** 37% of the loss
   budget currently teaches tidying. Keep only pairs whose control-flow token
   counts actually differ.
2. **Add a `comments` task.** `cleaned/merged_cleaned.jsonl` has a `comments`
   field non-empty in **18,681 of 19,033 rows**, carrying the defect language
   the model never learned (196 `bug`, 302 `undefined behaviour`, 105
   `incorrect`). `emit_tasks()` emits four tasks and this is not one of them —
   the signal is already annotated and is being discarded.

---

## What will not help

Measured, not guessed:

- **More epochs.** Improvement plateaued at step ~300 of 1035, and 98% of the
  learning-rate budget was spent by step 800. The last 250 steps moved held-out
  token accuracy by **9 parts per million**.
- **A bigger LoRA rank.** The adapter already carries 7.7 trainable parameters
  per supervised token and still does not overfit — eval loss sits *below*
  train loss. Capacity is not the limit.
- **More correct C++.** This is a composition problem. Targets asserting the
  code is fine outnumber defect claims **5.9 : 1**; another 19,000 working
  examples moves that ratio the wrong way.

## The rule that would have saved a month

Before any retrain, write down **which number should move if this works**, and
check that the evaluation actually prompts the task being changed. Phase 2
worked, but `eval_hard.py` only asks for `line_comments` and `explanation`, so
nobody could see it.
