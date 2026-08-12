# Writing the report from what already exists

Almost nothing here needs new work. The measurements are done, the decisions
were written down as they were made, and the references were each attached to a
decision rather than collected at the end. What is missing is the prose that
joins them.

This maps every chapter to the file that already holds its material, states the
claim that chapter has to land, and names the trap that would weaken it.

The order below is the order to write in — not the order it is read in.
Chapter 4 first, because it is nearly written already and it tells you what the
introduction has to promise.

---

## The argument the whole report makes

Write this on a sticky note and check every chapter against it:

> A 1.5-billion-parameter model, small enough to run on a laptop, can explain
> working C++ reliably and keep doing so when every identifier in the file is
> misleading. It cannot tell you the code is broken. Reliability and
> understanding are separate properties, and the measures normally reported
> capture the first while being read as evidence of the second.

Every chapter either sets that up, supports it, or qualifies it. Anything that
does none of the three is padding.

---

## Chapter 1 — Introduction

**Claim:** students learning C++ get compiler errors, not explanations, and the
tools that do explain are cloud services that see your code.

| Section | Material |
| --- | --- |
| Problem | Nothing written yet — 3 paragraphs, the only real writing in this chapter |
| Aims | `PLAN.md` opening: three capabilities (explain, optimise, survive renaming) |
| Contributions | The four below |
| Structure | Written last, in ten minutes |

State the contributions plainly:

1. A line-anchored output format that makes hallucinated comments **detectable**
   rather than merely unlikely (`src/qwen_cpp_review/line_anchoring.py`)
2. A measured result on identifier robustness, against a published baseline
   (`test_results/robustness.md`)
3. Execution-based verification of proposed optimisations
   (`src/qwen_cpp_review/verification.py`)
4. A measured limit, with evidence that it is not a prompting artefact
   (`test_results/hard_examples.md`, `test_results/defect_probe.md`)

**Trap:** promising bug detection. The report does not deliver it, says so, and
is stronger for the honesty — but only if Chapter 1 never claimed it.

---

## Chapter 2 — Literature review

**Claim:** every design decision came from somewhere, and the sources are named.

The hard part is done. `PLAN.md` §2 and the references section already tie each
paper to the decision it changed. Most FYP literature reviews are a disconnected
summary followed by unrelated work; yours can be written as *"we read X, which
is why the system does Y"*, which is what a reviewer actually wants.

Group the 15 references by the decision they informed:

| Theme | References | The decision it produced |
| --- | --- | --- |
| Do models understand code, or names? | *When Names Disappear* [1] | The entire Phase 2 evaluation, and the misleading-identifier variant |
| Code optimisation by learning | PIE [2], Supersonic [3], ECO [6] | Optimisation framed as a verified diff, not a rewrite |
| Robustness through transformation | ContraCode [4], ContraBERT [5] | Identifier augmentation during training |
| Structure-aware chunking | cAST [8] | Splitting on AST boundaries, never on token count |
| Synthetic data needs execution | *Verification Limits Code LLM Training* [9] | Why `improved_code` is compiled and run, never trusted |
| Structured output | XGrammar [10] | Considered, and why it was not needed |
| Efficient multi-task tuning | Mixture-of-LoRAs [11] | One adapter on a task-tagged mixture, with a documented fallback |
| Datasets and benchmarks | CodeNet [12], BigO(Bench) [14], CodeComplex [15] | Complexity labels excluded rather than reported |
| Limits of RL | RLVR analysis [13] | Why SFT on verified pairs must come first |

**Trap:** reviewing papers you did not use. Nine themes that each changed
something beat twenty summarised and abandoned.

---

## Chapter 3 — Design and methodology

**Claim:** the architecture follows from one decision — make the model's output
checkable.

`PLAN.md` §2 is this chapter in note form. Expand each subsection into prose:

| From PLAN.md | The point to land |
| --- | --- |
| §2.1 One adapter, task-tagged mixture | Scarce data split three ways is worse than one adapter that knows which task it is on |
| §2.2 Line-anchored output | **The keystone.** Quoting the line makes invention detectable; a rewritten file makes it invisible |
| §2.3 AST-boundary chunking | The corpus is 14-line functions; a 500-line file matches nothing it saw |
| §2.4 Optimisation as a verified diff | A rewrite that changes the answer is not an optimisation |
| §2.6 Serving pipeline | Two processes, and why the model is not loaded in the API |

Add one section PLAN.md does not have, because it was discovered later:

**Repairing anchors.** Measured on real output, ~25% of line numbers were
correct and ~100% of quotes were. Trusting the quote over the number recovers
comments that would otherwise be discarded or, worse, shown against the wrong
line. Evidence: 42 proposed → 29 relocated, 3 dropped, 39 shown.

**Trap:** describing the code instead of the decisions. A reader wants to know
*why* comments are records rather than a commented file. The class diagram
belongs in Chapter 4 if anywhere.

---

## Chapter 4 — Implementation

**Claim:** it is built, it runs on ordinary hardware, and someone else can run it.

| Section | Material |
| --- | --- |
| Dataset construction | `scripts/build_line_anchored.py`, `build_task_mixture.py` — 19,033 rows → 66,103 training rows |
| Training | `configs/train_qlora.yaml`, the Kaggle notebook, QLoRA on a T4 |
| Loss masking | `scripts/verify_loss_masking.py` — 311 prompt tokens masked, 443 supervised |
| Deployment | `docs/SETUP.md`, `RUNNING_ON_A_NEW_MACHINE.md` |
| API | `docs/API.md` |
| Known issues | `docs/KNOWN_ISSUES.md` |

Two implementation details are worth a paragraph each because they were bugs
found by measurement, which is a better story than code that worked first time:

- **`train_on_inputs` was a dead setting.** Declared in the config and read
  nowhere, so the trainer supervised the whole sequence and roughly half the
  gradient signal taught the model to reproduce prompts. Found, fixed, and
  proved fixed by decoding a real batch.
- **Identifier augmentation broke the anchors.** Renaming touched `code` but not
  `line_comments[*].code`, silently destroying the guarantee the whole design
  rests on. Verified afterwards: 0 broken anchors across 7,980 variants.

**Trap:** pasting code. Show the two or three fragments that carry a decision;
put the rest in an appendix or cite the file.

---

## Chapter 5 — Evaluation

**Already written.** The published chapter covers it: the four headline numbers
from one run, the identifier-robustness table with the GPT-4o comparison, twenty
broken programs with verbatim output, the three-instruction probe, the
verification results, and a section on what the numbers do not say.

Scripts, if the report needs a reproducibility statement:

| Script | Produces |
| --- | --- |
| `eval_hard.py` | The twenty broken programs |
| `probe_defects.py` | The three instructions compared |
| `eval_robustness.py` | The renaming test |
| `compare_quantizations.py` | The compression table |
| `report_ablation.py` | Base model vs fine-tuned |
| `test_verification.py` | The compile-and-compare checks |

**Still to add:** the base-model comparison, once its outputs are scored with the
same harness. Until then the claim "fine-tuning helped" is supported by
observation rather than measurement, and should be worded that way.

---

## Chapter 6 — Conclusion and future work

**Claim:** the aims were met, the limit is understood, and the route past it is
known and costed.

Three parts:

1. **What was achieved** — restate against Chapter 1's aims, one line each.
2. **The limit, and what it means.** Reliability and understanding came apart.
   Report both. This is the finding, not an apology.
3. **Future work, costed.** The model never saw broken code, so it never learned
   a program can fail to do what it looks like it does. That is a **composition**
   problem, not a shortage — more correct code would not help. A verified
   broken-code corpus is roughly two weeks: mutate working functions, run both
   versions, keep only pairs whose output differs, so the label is proven by
   execution rather than asserted. The harness for the running part already
   exists.

**Trap:** "with more time and data we would have improved accuracy." You know
more data would not have. Say the specific thing instead — it demonstrates
understanding, which is what the marks are for.

---

## The three questions to have an answer ready for

**"How do you know fine-tuning helped?"** — the base-model comparison. Get the
numbers into Chapter 5.

**"Your twenty broken programs are self-written. Isn't that cherry-picking?"** —
they are synthetic on purpose: the ground truth is exact, so the marking is
checkable rather than arguable. The cost is that they are not a sample of
anything, which the evaluation chapter states before anyone asks. Mined
wrong-answer submissions would answer a different question and could not answer
this one.

**"Half the descriptions are wrong. Why is that acceptable?"** — it is not, and
the system is built for it. Comments are filtered against the source before the
user sees them; proposed optimisations are compiled and run and discarded if the
answer changes. The measured error rate on a real file after filtering is 1 in
43. The honest framing is that the model is a component that is checked, not an
oracle that is trusted.
