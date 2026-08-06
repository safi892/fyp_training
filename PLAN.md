# Project Plan — C++ Code Understanding Model

Extending the existing QLoRA pipeline for `Qwen2.5-Coder-1.5B-Instruct` from
single-task review output to three capabilities:

- **A — Line-by-line explanation of a whole file**, not just a snippet.
- **B — Code optimization**, specifically recursion → iteration/DP.
- **C — Semantic understanding that survives variable renaming.**

Every claim of fact in this plan is either measured from this repository or
cited to a paper listed under [References](#references).

---

## 1. Where the project stands

### 1.1 Measured baseline

Run on `cleaned/merged_cleaned.jsonl`, 19,033 rows:

| Measure | Value | Consequence |
| --- | --- | --- |
| Code length | p50 **14 lines**, p90 31, p99 53, max **149** | No full-file training signal exists |
| Code tokens (est.) | p50 101, p90 239, p99 463 | `max_seq_length: 2048` is generous today, far too small for real files |
| `comments` field | Code re-emitted with inline comments | Right *shape* for goal A |
| …preserving input lines verbatim | **14.5%** | The annotated copy silently rewrites user code |
| `improved_code` identical to input | **0.4%** | The model always claims an improvement, never "already fine" |
| Complexity labels | `O(n³)` on 8.5%, `O(2^n)` on **4 rows** | Labels are noisy; recursion is under-labelled |

The dataset is a single logical corpus: `merged_cleaned.jsonl` is the four
shards concatenated (7,160 + 7,160 + 2,421 + 2,292 = 19,033), and
`merged_cleaned.jsonl.zip` is a byte-identical compressed copy for Kaggle
upload. Re-zip after any rebuild or Kaggle will train on stale rows.

### 1.2 What Phase 0 already fixed

`scripts/build_line_anchored.py` (complete, 14 passing tests) realigns comments
onto original source lines:

| Result | Value |
| --- | --- |
| Rows kept | **13,087** of 19,033 (68.8%) |
| Verified anchors | **80,703** (median 5/row) |
| Anchors whose stored text ≠ source line | **0** |
| Hallucinated comments removed | **2,729** |
| Mean match ratio (kept) | 0.970 |
| Coverage | p10 0.33 / p50 **0.55** / p90 0.80 |

**Key discovery in the rejects.** The largest bucket — 4,445 `no_anchors` rows —
is not corrupt data. 4,093 are *header-style summaries* rather than line-by-line
annotation, and **98% still carry a usable `explanation`**. The dataset has been
mixing two annotation styles under one field name. They belong to a different
task, not the bin.

Only **492 rows** were genuine drift. The raw 85% figure was mostly
reformatting, which the aligner absorbs.

Quality flags now attached to every row: 2,735 `low_complexity_confidence`,
1,635 `suspect_time_complexity`.

### 1.3 What does not exist yet

- No trained adapter in this repo (`outputs/` is absent; weights live on Kaggle).
- No compile/execute/timing harness — `improved_code` has never been compiled.
- No obfuscation evaluation.
- No chunker, stitcher, or file-level inference path.

---

## 2. Design decisions

### 2.1 One model, one LoRA, three tasks

Tasks share the same code-understanding substrate and the corpus is small
(18,942 rows carry a usable explanation; 13,087 carry verified anchors; 14,587
serve both). A single adapter trained on a task-tagged mixture avoids splitting
scarce data three ways.

Fallback if per-task evaluation shows interference (optimization degrading
explanation): per-task adapters in the Mixture-of-LoRAs style [11]. PEFT can
serve multiple adapters, so this stays reversible. **Do not start there.**

### 2.2 Line-anchored output, not re-emitted code

```json
{"line": 14, "code": "s /= 10;", "comment": "drop the lowest digit"}
```

The anchor is mechanically verifiable: if `code` does not equal input line 14,
reject it. This is what makes goal A safe at inference and what makes the
full-file case work — chunks stitch back by line number instead of relying on
the model to reproduce 600 lines.

### 2.3 Chunk on AST boundaries, never on token count

cAST [8] split-then-merge with tree-sitter: split at structural boundaries
(function/class/method), recursively merge small chunks with neighbours up to a
token budget, never split mid-function. Beats fixed-token chunking on SWE-bench
and CodeRAG-bench.

### 2.4 Optimization as a diff, not a rewrite

Supersonic [3] is a **700M** model that emits optimizations as diffs and beats
GPT-3.5-Turbo and GPT-4 on C/C++ optimization while changing less code — 600×
smaller than GPT-3.5. Diff formulation is what makes small-model optimization
work. Full-file rewriting at 1.5B is not a realistic target.

### 2.5 Constrained decoding at inference

XGrammar [10]: a 1B model with SFT + grammar constraints reaches 96.2% schema
accuracy, and constraints let Llama-3.2-3B beat an unconstrained 70B on
structured tasks. Removes JSON parse failure as an experimental variable.

### 2.6 Serving pipeline

```
source file
  → tree-sitter chunker (cAST split-then-merge)
  → file-level summary pass
  → per-chunk model call (constrained decoding)
  → validator  (anchors match input? improved_code compiles?)
  → stitcher   (merge by line number)
  → structured output
```

---

## 3. Phases

Effort is rough working-days for one person. Phases 1–2 are the minimum viable
FYP; 3–5 are the substance; 6 is optional.

### Phase 0 — Line anchoring ✅ COMPLETE

**Delivered:** `src/qwen_cpp_review/line_anchoring.py`,
`scripts/build_line_anchored.py`, `tests/test_line_anchoring.py`,
`cleaned/line_anchored.jsonl`, `cleaned/line_anchored_rejected.jsonl`.

**Acceptance met:** 0 of 80,703 anchors mismatch their source line.

---

### Phase 1 — Two-task dataset, wired into training

**Goal.** Make both annotation styles trainable and get one clean Kaggle run.

**Why now.** Everything downstream trains on this. It also recovers the 4,445
rejected rows instead of discarding a quarter of the corpus.

**Steps**

1. Emit a task-tagged mixture:
   - `line_comments` task ← **13,087** anchored rows.
   - `explanation` task ← **18,942** rows (anchored + header-style); 14,587 rows
     serve both tasks and appear once per task, not once overall.
   - Add an explicit task field to the instruction so the model can tell them apart.
2. Add `line_comments` to `FIELD_TITLES` in `src/qwen_cpp_review/prompt.py`.
   `build_response` already composes generically from `data.output_fields`, so no
   trainer change is required.
3. Add `line_comments` to `data.output_fields` in `configs/train_qlora.yaml`.
4. Filter on `quality_flags` at load time — exclude `low_complexity_confidence`
   and `suspect_time_complexity` from the complexity target while keeping the
   row's other fields.
5. Re-zip `cleaned/` for Kaggle.
6. One training run; save the adapter **off** Kaggle this time.

**Deliverables.** Task-tagged JSONL, updated prompt/config, one trained adapter
retrieved locally.

**Acceptance.** Training completes; eval loss decreases; the model emits parseable
`line_comments` whose anchors validate against held-out inputs at >90%.

**Effort.** 2 days + one training run. **Risk:** low.

---

### Phase 2 — Obfuscation evaluation (headline result)

**Goal.** Measure how much of the model's apparent understanding is really
identifier-name pattern-matching.

**Why this is the strongest part of the FYP.** *When Names Disappear* [1] found
GPT-4o dropping **87.3% → 58.7%** on ClassEval summarization under obfuscation,
and — surprisingly — execution prediction falling **9–24 Pass@1 points**, which
should depend only on structure. Their memorization stress test showed
identifier names acting as *retrieval cues for memorized outputs* rather than
triggers for reasoning. They recommend always reporting the original-vs-obfuscated
**delta**. That delta is a publishable-quality result and no one else in an FYP
cohort will have it.

**Steps**

1. Build a held-out eval set from rows the model never saw.
2. Implement the four obfuscation strategies from [1]:
   - alpha-rename (`var1`, `class2`)
   - ambiguous identifiers (`llllIII`)
   - cross-domain terms (unrelated field vocabulary)
   - **misleading semantics** (names implying wrong behaviour) — the most diagnostic
3. Extend `scripts/test_model.py`, which already generates renamed-variable
   variants, rather than writing a new harness.
4. Score each variant and report per-task deltas with a paired significance test.

**Deliverables.** Obfuscation eval suite; a delta table across four strategies ×
three tasks.

**Acceptance.** Deltas reproducible across two seeds; misleading-semantics is the
worst case (expected).

**Effort.** 2–3 days, **no GPU training required**. **Risk:** low.

---

### Phase 3 — Robustness training

**Goal.** Shrink the Phase 2 delta.

**Steps**

1. **Replace regex augmentation with tree-sitter or libclang.** The current
   `scripts/augment_identifiers.py` cannot see scopes, will rename inside string
   literals, and cannot distinguish a local from a member.
2. Add ContraCode's [4] non-naming transforms so the model learns invariance to
   *structure*, not just names: dead-code insertion, constant folding, statement
   reordering, loop-form changes.
3. Retrain with augmented data; re-run Phase 2 and report delta reduction.
4. *Optional:* a contrastive auxiliary objective (InfoNCE over transform pairs,
   ContraCode/ContraBERT style [4][5]). ContraCode held 58% AUROC under 16
   adversarial edits where RoBERTa collapsed below 5%.

**Deliverables.** Tree-sitter augmenter; retrained adapter; before/after delta table.

**Acceptance.** Measurable delta reduction vs Phase 2 on the *same* eval set.

**Effort.** 3–4 days + training. **Risk:** medium — the contrastive objective is
the risky part; the augmentation upgrade alone is likely to carry most of the gain.

---

### Phase 4 — Optimization (recursion → loop)

**Goal.** Verified recursion→iteration/DP transformation.

**Scope warning.** Full PIE with gem5 is not achievable in an FYP. The scoped
version below is.

**Steps**

1. Take a slice of PIE's [2] C++ slow→fast pairs (~77k available, from CodeNet [12]).
2. **Filter to the recursion→iteration/DP subset.** PIE's taxonomy is 34%
   algorithmic and calls out recursion→DP as one of the most frequent transforms.
3. Build the harness — **this is the real work, not the training**:
   - compile both versions
   - run against CodeNet test cases for correctness
   - time with repeated runs and medians (skip gem5; accept the added noise and
     document it as a deviation from [2])
4. Represent each example as a **diff**, per Supersonic [3].
5. Train as a third task in the mixture.
6. Report `%OPT`, aggregate speedup, `%Correct` — the metrics from [2].

**Non-negotiable.** Every pair must compile, pass tests, and be timed before it
enters training. *Verification Limits Code LLM Training* [9] is direct on this:
synthetic code data needs execution-based verification or a genuinely stronger
teacher. This project currently has neither.

**Deliverables.** Verification harness; filtered diff-formatted dataset;
optimization-capable adapter; metrics table.

**Acceptance.** `%Correct` > 95% on held-out (correctness is the floor);
`%OPT` > 0 with a documented mean speedup.

**Effort.** 5–8 days, harness-dominated. **Risk:** high — the largest single risk
in the plan. Cut first if time runs short.

---

### Phase 5 — Full-file capability

**Goal.** Handle a real 500+ line file end to end.

**Steps**

1. Implement the cAST [8] chunker: tree-sitter parse → split at structural
   boundaries → recursive merge to a token budget → never split mid-function.
2. Synthesize multi-function training files by concatenating related snippets
   (the corpus maxes out at 149 lines, so this signal must be manufactured).
3. Raise `data.max_seq_length` past 2048; re-tune batch size / gradient
   accumulation against the VRAM table in `README.md`.
4. Two-pass inference: file-level summary, then per-chunk annotation conditioned
   on it — the standard 2025 comment-generation pattern.
5. Implement the stitcher: merge per-chunk anchors by absolute line number.
6. Add the validator: reject anchors that do not match the input file.

**Deliverables.** Chunker, stitcher, validator, file-level CLI entry point.

**Acceptance.** A 500-line file processes end to end; 100% of returned anchors
validate against the input; no line is annotated twice.

**Effort.** 4–5 days. **Risk:** medium — mostly engineering, little training risk.

---

### Phase 6 — Optional extensions

Only with time to spare, in this order:

1. **XGrammar constrained decoding** [10] at inference. Cheap, high certainty.
2. **GALLa** [7] graph alignment: a GNN encodes AST+DFG, a single cross-attention
   adapter projects into the LLM embedding space during training, and the graph
   encoder is **discarded at inference** — no architecture change, no graphs
   needed at serving, no speed penalty. Reported **+12% on Qwen2.5-Coder-1.5B**,
   exactly this base model.
3. **GRPO/RLVR** on measured speedup for Phase 4. Note the caveat [13]: RLVR
   sharpens what a model can already do rather than teaching new capability, so
   SFT on verified pairs must come first.

---

## 4. Evaluation protocol

| Goal | Primary metric | Secondary |
| --- | --- | --- |
| A — Line comments | **Anchor validity rate** (fraction of returned anchors matching input) | Coverage; human rating on a sample |
| A — Full file | End-to-end anchor validity on 500+ line files | No double-annotated lines |
| B — Optimization | `%Correct`, then `%OPT`, then aggregate speedup [2] | Diff size (smaller is better [3]) |
| C — Robustness | **Original-vs-obfuscated delta** across 4 strategies [1] | Delta reduction after Phase 3 |
| All | Structured-output parse rate | eval loss / perplexity |

Report obfuscated *and* original scores side by side, always — that is the
methodological recommendation from [1] and it is what separates measured
understanding from memorization.

**Complexity analysis** should be evaluated as classification against a cleaned
subset, not trained on unfiltered labels. CodeComplex [15] and BigO(Bench) [14]
are the reference datasets if the complexity task is developed further.

---

## 5. Risks and scope cuts

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Phase 4 harness overruns | High | Cut Phase 4 entirely; A + C is a complete FYP |
| 1.5B too small for optimization | Medium | Diff formulation [3] is the mitigation; narrow scope hard |
| Task interference in one LoRA | Medium | Per-task eval each run; fall back to per-task adapters [11] |
| Kaggle session limits | Medium | Resume logic already exists and is documented |
| Complexity labels stay unreliable | High | Flag and exclude; do not present as a headline result |
| Coverage stuck near 0.55 | Medium | Frame as "every meaningful line", not literally every line |

**If time runs out, cut in this order:** Phase 6 → Phase 4 → Phase 5. Phases
1–3 alone constitute a defensible project with a novel measured result.

---

## 6. Expectation setting

At 1.5B parameters, goals **A and C are very achievable**. Goal **B is achievable
only** in the narrow diff-based, verified-data formulation — Supersonic's 700M
result [3] proves the ceiling exists, but it came from tight scope and clean
data, not from scale.

---

## References

1. [When Names Disappear: Revealing What LLMs Actually Understand About Code](https://arxiv.org/html/2510.03178) (2025)
2. [Learning Performance-Improving Code Edits (PIE)](https://pie4perf.com/) — ICLR 2024 · [paper](https://openreview.net/pdf?id=ix7rLVHXyY)
3. [Supersonic: Learning to Generate Source Code Optimizations in C/C++](https://arxiv.org/abs/2309.14846)
4. [ContraCode: Contrastive Code Representation Learning](https://ar5iv.labs.arxiv.org/html/2007.04973)
5. [ContraBERT: Enhancing Code Pre-trained Models via Contrastive Learning](https://arxiv.org/pdf/2301.09072)
6. [ECO: Enhanced Code Optimization via Performance-Aware Prompting](https://arxiv.org/pdf/2510.10517) (2025)
7. [GALLa: Graph Aligned Large Language Models](https://arxiv.org/html/2409.04183)
8. [cAST: Structural Chunking via Abstract Syntax Tree](https://arxiv.org/pdf/2506.15655) (2025)
9. [Verification Limits Code LLM Training](https://arxiv.org/pdf/2509.20837) (2025)
10. [XGrammar: Flexible and Efficient Structured Generation](https://arxiv.org/pdf/2411.15100)
11. [Mixture-of-LoRAs: Efficient Multitask Tuning for LLMs](https://arxiv.org/abs/2403.03432)
12. [Project CodeNet](https://arxiv.org/pdf/2105.12655) — NeurIPS 2021
13. [RLVR analysis: makes models faster, not smarter](https://www.promptfoo.dev/blog/rlvr-explained/)
14. [BigO(Bench)](https://arxiv.org/html/2503.15242v1) (2025)
15. [CodeComplex: Worst-Case Time Complexity Prediction](https://arxiv.org/abs/2401.08719)
