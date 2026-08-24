# Why phase 2 did not improve accuracy

Investigation of 2026-08-24. Everything below was measured on this machine
(i7-6700HQ, CPU only, llama.cpp build 10606) unless stated otherwise. Numbers
without a command behind them are marked as such.

---

## The one-line answer

**Phase 2 worked. The evaluation could not see it.**

Phase 2 added 795 rows (1.19% of the corpus) in two tasks — `optimize` and
`iterate` — and `eval_hard.py` prompts neither of them. Measured on the task it
actually trained, on the same machine in the same session, phase 2 more than
doubles phase 1:

| | phase 1 | phase 2 |
| --- | ---: | ---: |
| Algorithm actually transformed (all 17 samples) | 11/68 (16%) | **28/68 (41%)** |
| **Contamination removed (15 samples)** | **10/60 (17%)** | **24/60 (40%)** |

Paired McNemar on the clean subset: 15 gained, 1 lost, **p = 5.2e-04**.

The flat `eval_hard.py` result was arithmetically guaranteed before the GPU
started, and it is not evidence that the training failed. See §2.3.

```
mixture rows 0–66,102  : line_comments 13,569 · explanation 18,939
                         complexity    14,660 · improve     18,935
mixture rows 66,103+   : optimize 290 · iterate 505      <- the only change

scripts/eval_hard.py:657 : for task in ("line_comments", "explanation")
```

The 795 new rows produce `improved_code`. `eval_hard.py` never asks for it.
Phase 2 was not a failed experiment; it was an experiment whose result was
measured with the wrong instrument.

---

## 1. What was actually run

| Step | Artefact |
| --- | --- |
| Merged `best_adapter` into the base on CPU (fp32) | shard sizes byte-identical to the Aug-11 merge |
| Converted to GGUF f16 | 3,093,668,960 B vs phase-1's 3,093,668,864 B (96 B of metadata) |
| Quantised to Q4_K_M | 986,048,096 B vs phase-1's 986,048,000 B — identical quantisation |
| `eval_hard.py` on phase 2 | `test_results/hard_examples_v2.{json,md}` |
| `eval_hard.py` on phase 1, **same machine, same build** | `test_results/hard_examples_v1_rerun.{json,md}` |
| `report_ablation.py` base vs phase 2 | `test_results/ablation_v2.md` |

The phase-1 re-run is the important one, and it is the reason the first
conclusion of the day had to be thrown out.

---

## 2. Results

### 2.1 The headline comparison

| Run | Problems named | Confidently false |
| --- | ---: | ---: |
| Phase 1 — Mac, committed Aug 12 | 7/55 | 10/20 |
| Phase 1 — **this machine** | 9/55 | 8/20 |
| Phase 2 — **this machine** | 8/55 | 7/20 |
| Untuned base | 9/55 | 8/20 |

Phase 2 sits *between the two phase-1 measurements on both axes*.

Same-machine delta: **−1 problem named, −1 false claim.** Both inside noise.

### 2.2 The eval numbers are machine-dependent

The identical phase-1 weights, identical greedy decoding (`temperature: 0`),
scored **7/55 on the Mac and 9/55 here**. Floating-point reduction order differs
with thread count and SIMD path; at temperature 0 one flipped token cascades
through the whole generation.

**±2 of machine-dependent variance is larger than the effect being measured.**
Any future comparison must run both models on the same machine in the same
session. The committed Aug-11 numbers are not a valid baseline for anything
measured elsewhere.

### 2.3 The optimize probe — where phase 2 actually shows up

`scripts/probe_optimization.py`, `--draws 0`, both models back to back on this
machine, `temperature: 0`, 17 samples × 4 phrasings = 68 paired conditions.
A "win" is the harness's own criterion: the rewrite **compiles, runs, produces
the same answers, and actually changed the algorithm** — not a keyword match.

| Phrasing | phase 1 | phase 2 | Δ |
| --- | ---: | ---: | ---: |
| `trained_wording` (what the product sends) | 1/17 | **5/17** | +4 |
| `explicit_faster` | 1/17 | **7/17** | +6 |
| `explicit_loop` | 4/17 | **10/17** | +6 |
| `explicit_memo` | 5/17 | 6/17 | +1 |
| **Total** | **11/68 (16%)** | **28/68 (41%)** | **+17** |

**Contamination check.** Two of the 17 probe samples — `fibonacci` and
`gcd_euclid` — appear verbatim in `test_results/distilled.jsonl`, so the model
was trained on them. Excluding both:

```
phase 1 : 10/60 (17%)
phase 2 : 24/60 (40%)
gained 15, lost 1     McNemar exact two-sided p = 5.19e-04
```

The contaminated pair contributes 3 of the 18 raw gains. **The effect survives
their removal at p < 0.001.** This is a genuine capability gain, not recall.

**What this means.** 58 execution-verified pairs, upsampled 5× to 795 rows —
**1.19% of the corpus** — moved a capability that 66,103 unverified rows never
did. The `improve` task has 18,935 rows and 37% of the entire loss budget, and
teaches `const`-sprinkling (64% of its pairs leave control-flow token counts
identical). The `optimize` task has 290 rows and teaches the real
transformation.

That is the project's strongest quantitative result: **a small execution-verified
corpus beats a large asserted one, by a wide and significant margin.**

---

## 3. Issues found

### ISSUE 1 — The model's raw line numbers are wrong, and phase 2 made it worse

**Status: measured, mitigation already exists, regression is invisible to current metrics.**

| | Quoted code text verbatim | **Raw line number correct** |
| --- | ---: | ---: |
| Phase 1 | 77/77 (100%) | **26/77 (34%)** |
| Phase 2 | 72/72 (100%) | **6/72 (8%)** |

Off by exactly +1 in 49 and 60 cases respectively.

**Cause.** `src/qwen_cpp_review/prompt.py:178` (and `:287`) renders the code as:

```python
{"role": "user", "content": f"{instruction}\n\n### Code\n\n```cpp\n{code}\n```"}
```

The model counts the ```` ```cpp ```` fence as line 1, so source line *N* is
reported as *N+1*. The training data is not at fault — all 82,224 anchors in the
mixture carry the correct 1-based number.

**This is already mitigated.** `repair_anchors` in `line_anchoring.py` trusts the
quoted text over the number and relocates. Measured on today's outputs:

```
phase 1   raw 26/77 (34%)  ->  repaired 77/77 (100%)   exact 26 / repaired 51 / dropped 0
phase 2   raw  6/72 ( 8%)  ->  repaired 72/72 (100%)   exact  6 / repaired 66 / dropped 0
```

Zero anchors dropped in either run: every quoted line was found in the source.
`repair_anchors` is called from `checked_response.py` (serving), `chunking.py`
(whole-file), `report_ablation.py`, `probe_defects.py`, `eval_robustness.py`,
`compare_quantizations.py` and others. `eval_hard.py` is one of the few that
does not, which is why the raw numbers were visible there at all.

**So why does it matter?** Because the repair *masks a real regression*. The
"100% anchor validity" headline is true, but it is measured post-repair, so it
cannot distinguish a model that counts perfectly from one that counts correctly
8% of the time. Phase 2 degraded 4× on this axis and no reported metric moved.

**Fix.** Report `report.exact` and `report.repaired` separately, not just the
post-repair total. One extra column turns an invisible regression into a visible
one. Optionally number the lines in the prompt (`1: void foo() {`) — but that
puts the model off its training distribution, so measure before adopting.

---

### ISSUE 2 — The base-model comparison is unfair to the fine-tune

**Status: identified, `ablation.md` should be regenerated or footnoted.**

`score_external.py:read_explanation` falls back to the **entire raw reply** when
the JSON does not parse — which for the base model is 20/20 of the time. The
base therefore has its "Actionable Recommendations", its rewritten `main()`, and
its invented JSON schemas fed to the scorer. The tuned models, whose JSON always
parses, have only their `comment` strings and `explanation` harvested.

Trimming the base to comparable prose volume:

| Base text scored | chars | problems named | confidently false |
| --- | ---: | ---: | ---: |
| full (as reported) | 40,865 | 9/55 | 8/20 |
| code blocks removed | 29,459 | 8/55 | — |
| only prose analysing *this* code | **16,445** | **6/55** | **9/20** |

Against phase 2's 12,207 chars, the fair figure is **6/55, not 9/55** — and the
base's false-claim count *rises* to 9/20.

The base is also demonstrably not reasoning. It volunteers worked examples and
gets them wrong: it states the primes below 100 sum to **768** (correct: 1060),
and on `recursion_without_base_case` it invents a base case that does not exist
— **scoring a point for the hallucination.**

**Conclusion.** `ablation.md`'s "no evidence the fine-tuning improved
comprehension" is too harsh. Defensible finds: base ≈5, phase-2 = 7, phase-1 = 9.

---

### ISSUE 3 — The scoring harness errs in both directions

**Status: identified, ~5 credits are unearned, ~2 real finds are missed.**

Missed real finds:

- `self_shadowing_counter` / phase-1 — wrote *"increment the counter; this is a
  no-op because the variable is re-declared"*. Correct diagnosis of the
  shadowing bug, in words no `finds` group covers. Scored 0/3.
- `grow_during_range_for` / base — named iterator invalidation but filed it as a
  performance tip. Scored 0/3.

Unearned credits:

| Sample | What earned it | Why it is wrong |
| --- | --- | --- |
| base / `recursion_without_base_case` | *"the base case … is when `n` is 0"* | hallucinated a base case that is not there |
| base / `integer_division_before_widening` | `static_cast<double>` | matched inside an emitted code block, not prose |
| phase-2 / `loop_bound_off_by_one` | *"the loop runs one extra time to include the last element"* | **endorses** the out-of-bounds read as intentional |
| phase-1+2 / `switch_fallthrough` | *"the switch body is empty"* | right keyword, fabricated reason |

Correcting both directions moves the ranking *away* from the base, not toward it.

---

### ISSUE 4 — The resume path discards optimizer state every session

**Status: real bug, affected both runs equally, does not explain the null result.**

`callbacks.py:254` writes `"optim": str(args.optim)`, which serialises the
transformers enum as `"OptimizerNames.ADAMW_TORCH"`. `resume.py:498` compares
that against the YAML string `"adamw_torch"`. They can never be equal, so every
cross-session resume silently downgrades `exact` → `state` and restarts Adam's
moments from zero.

```
WARNING: checkpoint was written with optim=OptimizerNames.ADAMW_TORCH but this
         run uses optim=adamw_torch; the saved optimizer moments are not loadable
```

**Fix.** Normalise both sides:
`str(x).split(".")[-1].lower()`. Until then `resume_mode: auto` can never reach
`exact`, and the README's resume table is describing a mode the code cannot select.

Related: `resume.py:551` only warns on dataset drift above 2%. Phase 2's growth
was 1.19%, so a stale checkpoint would have resumed across changed data silently.

---

### ISSUE 5 — `final_adapter/` contains no weights, and the README points at it

**Status: FIXED today (directory deleted). README still needs editing.**

`final_adapter/` held tokenizer files and `training_config.yaml` only — no
`adapter_model.safetensors`. Every inference and evaluation example in
`README.md` says `--adapter .../final_adapter`. Those commands would fail or
silently load a bare base model.

**Fix.** Point the README at `best_adapter/`, which is the byte-identical copy of
`checkpoint-1000` that `load_best_model_at_end` selected (`best_metric` 0.411108).

---

## 4. Why the model cannot find defects at all

Separate question from "why didn't phase 2 help", and the more important one.

### 4.1 It reads the code. It just does not evaluate it.

The `line_comments` schema makes the model echo each line verbatim. **100% of
echoed lines are exact source text** in both phases. From `broken_swap`:

```
echoes:  data[j] = data[j + 1];    comments: "Move the larger element to the front."
echoes:  data[j + 1] = data[j];    comments: "Place the smaller element at the current position."
```

The destructive assignment is in the model's own output buffer and it still
writes the swap story. This is 55–70% of all failures: the model recognises the
algorithm's *shape* and emits the prior for that shape instead of reading the lines.

**The boundary is drawn precisely by the one sample every model passes.**
`misleading_function_name` (3/3 everywhere) is the only sample whose body is
*correct code* — the trap is purely the name. Naming that requires description,
never a correctness judgement. All 19 samples that require *"this line does not
do what it looks like"* fail.

### 4.2 The corpus is 6:1 biased toward approval

Of 66,898 training rows:

| Signal | Rows | Share |
| --- | ---: | ---: |
| Any assertive defect claim in the target | ~700 | 1.05% |
| …of which genuine C++ logic defects (hand-verified sample) | **~150** | **~0.2%** |
| Targets asserting the code is correct / efficient | 4,143 | **6.19%** |

**Ratio 5.9 : 1 in favour of "this code is fine."** The model is not merely
untrained to object — it is trained six times harder to approve.

Additionally: 41% of distinct programs carry scraper-corruption markers, and 42%
of the explicit `BUG:` comments annotate that damage (missing `||`, spaced char
literals) rather than defects a reviewer would meet.

### 4.3 The field that carries the signal is dropped before training

`merged_cleaned.jsonl` has a `comments` field non-empty in **18,681 of 19,033
rows**, and that is where the defect language lives — 196 `bug` hits, 302
`undefined behaviour`, 105 `incorrect`.

`scripts/build_task_mixture.py:50` emits only `line_comments`, `explanation`,
`complexity`, `improve`. **`comments` contributes zero training rows.**

This is the highest-leverage fix available and requires no re-annotation.

### 4.4 The complexity filter deleted exactly the informative labels

`COMPLEXITY_BLOCKING_FLAGS` drops rows by annotator confidence, which correlates
with complexity class:

| Label | Raw | Trained | Survival |
| --- | ---: | ---: | ---: |
| O(1) | 6,251 | 6,249 | 100% |
| O(n) | 6,160 | 5,423 | 88% |
| O(n²) | 2,118 | 123 | **5.8%** |
| **O(n³)** | 1,623 | **0** | **0%** |
| **O(2^n)** | 4 | **0** | **0%** |

The adapter has never seen `O(n³)` and cannot emit it. The whole task has **7
distinct target strings**; a constant `{"time":"O(1)","space":"O(1)"}` scores 42.6%.

### 4.5 Half the loss is spent on copying and templates

- **99.97%** of explanation targets match `Purpose: → Input: → Output: → Algorithm:`
  in order; 92.9% are exactly 4 lines.
- `line_comments` targets: 43.7% JSON scaffolding, 23.3% verbatim copy of an
  input line, **33.0%** actual comment text.
- `improve`: 68% add `const`, **64% leave control-flow token counts identical**,
  0.77% introduce memoisation or DP.
- Rolled up: **~47% of supervised tokens are pure copy-or-template.**

So `eval_mean_token_accuracy: 0.880` and perplexity **1.51** are measuring format
compliance, not review judgement. Cross-entropy weights every token equally, and
the handful encoding an actual review decision is a rounding error in the loss.

---

## 5. Training itself was sound

Ruling out the obvious alternative explanations, with evidence.

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| Overfitting | **Ruled out** | eval 0.4111 is *below* real train 0.4252 |
| Undertrained | **Ruled out** | plateau at step ~300; last 250 steps bought +9e-6 held-out token accuracy |
| Bad gradients | **Ruled out** | grad_norm max 0.149 vs 0.3 limit — **0 of 100 points clipped**; no NaN |
| Dead adapter | **Ruled out** | 0 of 196 LoRA B matrices at zero |
| LoRA too weak | **Unlikely** | see below |

**`train_loss: 0.2243` is a resume artefact.** HF accumulated loss over the 535
steps this session ran but divided by `global_step` 1035. The real end-of-run
train loss is **0.4252**. There is no train/eval gap.

**There were four eval points, not two:**

| step | eval_loss | Δ | eval token acc |
| ---: | ---: | ---: | ---: |
| 250 | 0.455081 | — | 0.869858 |
| 500 | 0.424128 | −0.030952 | 0.877770 |
| 750 | 0.412864 | −0.011264 | 0.880264 |
| 1000 | **0.411108** | **−0.001756** | 0.880273 |

Held-out token accuracy moved **9 parts per million** over the final 250 steps.

**On `lora_alpha=16` with `r=64`.** Scaling is `alpha/r = 0.25`, which is low —
convention is `alpha = r` or `2r`. Measured `‖ΔW‖_F / ‖W‖_F` is 1.28% (it would
be 5.1% at α=64). But this was **not the binding constraint**: the B matrices used
only **4.7% of their Adam travel budget**, so the optimiser had ~20× the room and
declined it. Raise alpha next run because it is free and conventional, not
because it will fix accuracy.

**Capacity is not the limit either.** 73,859,072 trainable params against ~9.6M
supervised tokens — **7.7 trainable parameters per token predicted**. Wildly
over-parameterised, and *still* no overfitting. That combination is diagnostic:
the task carries so little learnable signal that a 74M-parameter adapter could
not memorise its way into overfitting.

---

## 6. What the literature says

| Claim | Source |
| --- | --- |
| Imitation transfers style, not capability — tested at **1.5B–13B**, the same scale | [The False Promise of Imitating Proprietary LLMs](https://arxiv.org/abs/2305.15717) (2023) |
| Base and aligned models decode near-identically except on *stylistic* tokens | [URIAL](https://arxiv.org/abs/2312.01552) (ICLR 2024) |
| "SFT stabilizes the model's output format", enabling later RL | [SFT Memorizes, RL Generalizes](https://arxiv.org/abs/2501.17161) (ICML 2025) |
| Examples teaching *new* knowledge are learned far more slowly — predicts the flat second epoch | [Gekhman et al.](https://arxiv.org/abs/2405.05904) (EMNLP 2024) |
| LoRA underperforms full FT **specifically in code**; full FT learns rank 10–100× greater | [LoRA Learns Less and Forgets Less](https://arxiv.org/abs/2405.09673) (TMLR 2024) |
| Schema constraints on **Qwen2.5-1.5B**: validity 61.5%→100%, accuracy 19.7%→**11.0%** | [The Constraint Tax](https://arxiv.org/abs/2605.26128) (2026 preprint) |
| Asking a model to *explain and fix* drives it to invent defects — 35.9%→**87.9%** false rejection | [Systematic Overcorrection](https://arxiv.org/html/2603.00539) (2026 preprint) |
| Bug detection needs injected negatives; random injection is too easy | [BugLab](https://arxiv.org/abs/2105.12787) (NeurIPS 2021) |
| Models trained on injected bugs overfit to them — filter against real code | [Learning Defect Prediction from Unrealistic Data](https://arxiv.org/html/2311.00931) (2023) |

**~15% defect naming is normal at this scale**, not a failure:

- [To Err is Machine](https://arxiv.org/abs/2403.17218): SOTA reaches **54.5%**
  balanced accuracy on *binary* vulnerability detection (chance = 50%), and
  fine-tuning did not significantly improve it.
- [PrimeVul](https://arxiv.org/abs/2403.18624): 7B SOTA drops 68% F1 → **3.09%**
  once the benchmark is de-duplicated properly.
- [VulDetectBench](https://arxiv.org/html/2406.07595): on *localisation*, most
  sub-7B models score **under 10%**.
- [Qwen2.5-Coder tech report](https://arxiv.org/html/2409.12186v3): this exact
  base model scores CRUXEval-O **37.5** at 1.5B vs **65.9** at 7B.

### Two corrections to the project's current citations

1. **`Verification Limits Code LLM Training` (arXiv:2509.20837) is cited
   backwards in `PLAN.md`.** Its headline is that verification is often *too
   strict* — 100%-pass filtering underperforms relaxed 0.6–0.8 thresholds, and
   LLM-based soft verification matched or beat unit tests. Cite it for its
   *verification-ceiling* argument instead: when one model both authors and
   judges its own output, a closed loop forms in which only what the verifier
   recognises survives. That fits this project's teacher exactly.

2. **Do not conclude "1.5B is too small."** [R2Vul](https://arxiv.org/abs/2504.04699)
   (2025) trains a **1.5B** student with reasoning distillation + RLAIF and
   reports it exceeding its own 32B teacher. The defensible claim is that **the
   binding constraint was the training signal, not the parameter count.**
   (Caveat: R2Vul is binary classification over labelled CVE data, not
   open-ended defect naming.)

---

## 7. How to actually improve the model

Ranked by measured leverage per unit of effort. Items 1–4 need **no GPU**.

### 1. ✅ DONE — evaluate what you actually changed

Run on 2026-08-24: **16% → 41% raw, 17% → 40% contamination-controlled,
p = 5.2e-04.** See §2.3. Phase 2 worked; `eval_hard.py` simply never asked.

The follow-on is now the obvious one: **make more verified pairs.** 58 of them
bought this. `scripts/verify_optimization_pairs.py` already gates them (side A
recursive, side B not, both compile, identical stdout), and
`scripts/build_optimize_dataset.py` generates candidates. The yield is low —
`CLAUDE.md` records 2 verified from 130 attempted on one run — so budget for
that, and prefer a stronger teacher for the generation step.

### 2. Report `exact` vs `repaired` anchors separately — no GPU, ~30 minutes

One column. Turns Issue 1's invisible 4× regression into a tracked metric.

### 3. Add a `comments` task to the mixture — no GPU, ~1 day

18,681 rows of defect-bearing text are currently discarded
(`build_task_mixture.py:50`). This is the single highest-leverage data change
available and needs no re-annotation. Rebuild, retrain, re-probe.

### 4. Fix the corpus's approval bias — no GPU for the data work

The 5.9 : 1 skew toward "this code is fine" is the root cause. Two options:
down-weight the `improve` task (37% of supervised tokens teaching `const`-sprinkling),
or up-weight defect-bearing rows. Neither requires new annotation.

### 5. Build a verified broken-code corpus — ~2 weeks, then GPU

The one intervention that addresses the actual gap:

1. Take working functions from the corpus
2. Mutate them (remove a `temp`, `<` → `<=`, drop a `break`)
3. **Compile and run both versions**
4. Keep only pairs whose output differs

The label "this is broken" is then *proven by execution*, not asserted by a
teacher. `src/qwen_cpp_review/verification.py` already has the compile-and-compare
harness. Filter against real code per
[Alrashedy et al.](https://arxiv.org/html/2311.00931) so the model does not
overfit to synthetic mutations.

### 6. Distil reasoning traces, not answers — GPU

The current corpus distils the teacher's *conclusions*. [Distilling
Step-by-Step](https://arxiv.org/abs/2305.02301) (ACL Findings 2023) got a **770M**
model to beat few-shot 540B PaLM using 80% of the data by distilling the
*rationale*. This directly addresses the answers-only defect.

### 7. Cheap hyperparameter corrections — free, do them anyway

| Setting | Now | Change to | Why |
| --- | --- | --- | --- |
| `lora_alpha` | 16 | 64 | scaling 0.25 → 1.0; conventional |
| `learning_rate` | 2e-4 | ~4e-4 | effective batch was 4× the config's assumption |
| `validation_split_ratio` | 0.01 (run) | 0.05 | 669 → 3,345 eval rows |
| `eval_steps` | 250 (run) | 100 | 4 → 10 eval points |
| `resume.py:498` | enum vs string | normalise both | Issue 4 |

None of these will move accuracy on this evidence. Make them because they are
correct.

### What will NOT help

- **More epochs.** Improvement stopped at step 300 and 98% of the LR budget was
  spent by step 800.
- **More correct C++.** This is a *composition* problem, not a quantity problem.
  Another 19,000 working examples changes nothing.
- **A bigger LoRA rank.** The adapter already has 7.7 trainable parameters per
  supervised token and does not overfit.

---

## 8. What to claim in the report

**Defensible:**

> Fine-tuning produced a model that emits valid structured output on 20/20 held-out
> programs where the base model manages 0/20, with every returned anchor
> verifiable against the source. It did not measurably improve the model's ability
> to detect defects (8/55 vs a base model's fair-scored ~6/55, n=55 — underpowered
> to exclude a small effect). Reliability and understanding are separate
> properties, and the metrics normally reported capture the first while being read
> as evidence of the second.

**Also defensible, and stronger than anything else here:**

> 58 execution-verified optimisation pairs — 1.19% of the corpus — more than
> doubled the model's rate of genuine algorithmic transformation, from 17% to 40%
> (p = 5.2e-04, contamination-controlled, paired same-machine comparison), on a
> metric decided by compiling and running the output rather than by matching
> keywords. The 18,935-row `improve` task, built from unverified teacher output
> and consuming 37% of the loss budget, did not. Verification of the training
> signal mattered more than three orders of magnitude of data volume.

**Not defensible:**

- "Phase 2 achieved nothing" — it achieved a large, significant gain on the task
  it was trained for. `eval_hard.py` prompts only `line_comments` and
  `explanation` and therefore cannot observe it. **An evaluation that does not
  exercise the changed capability is not evidence of its absence.**
- "Fine-tuning improved comprehension" — the same-machine defect delta is −1.
- "1.5B is too small for defect detection" — R2Vul refutes it.
- "No improvement" — say **"no detectable improvement (n=55)"**; you can exclude
  a large effect, not a small one.
- Any comparison against the committed Aug-11 numbers — they were measured on
  different hardware and carry ±2 of drift.

**Worth claiming as a methodological contribution:** at `temperature: 0`, this
evaluation carries ±2 machine-dependent variance, larger than the effect it was
built to detect. Greedy decoding is not reproducible across machines, and
comparisons must be run same-machine, same-session.

---

## Appendix — corrections made during this investigation

Recorded because three of them were stated confidently before being checked.

| Claim | Status |
| --- | --- |
| "`task_mixture_verified.jsonl` is a copy, so verification never reached training" | **WRONG.** `origin/language:cleaned/task_mixture_verified.jsonl` has the same md5 as the local plain-named file. The verified build was copied over the plain name for the Kaggle bundle. Phase 2 trained on the verified mixture. |
| "The verification step didn't run" | **WRONG.** `add_verified_pairs.py` is additive *by design* — its docstring explains that mixing verified rows into an unverified pile "makes the pile look better without making it better." |
| "505 `iterate` rows raise `ValueError`" | **WRONG.** Checked against stale local `main`. `origin/language:prompt.py:70` registers `iterate`. No bug. |
| "Only two eval points" | **WRONG.** Four: steps 250/500/750/1000. |
| "train_loss 0.2243 vs eval 0.4111 is a large gap" | **WRONG.** Resume artefact; real train loss 0.4252 and eval sits *below* it. |
| "Phase 1's 17.7 tok/s is this machine's baseline" | **WRONG.** That figure was measured on the Mac (commit `cfe36fb`, authored `MacBook Pro`). |
| "Phase 2 bought nothing for 10.4 GPU-hours" | **WRONG, and this was the headline.** It bought 17% → 40% on algorithmic transformation (p = 5.2e-04). The claim rested entirely on `eval_hard.py`, which prompts only `line_comments` and `explanation` — neither of which phase 2 touched. |

**Process lesson:** the local `main` branch was 45 commits behind
`origin/language`, which is what actually produced phase 2. Three of the six
errors above came from reading stale code. Work on `language`.
