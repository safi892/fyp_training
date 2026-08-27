---
name: measuring-changes
description: >-
  How to tell whether a change to this model actually did anything. Use this
  skill before running any evaluation, before reporting that a training run
  helped or did not help, whenever comparing two checkpoints, and whenever
  writing a number into the report. Use it even when the result looks obvious,
  because every wrong conclusion in this project's history came from an
  evaluation that could not see what changed, a comparison across machines, or a
  score that matched a name where a concept was meant.
paths: scripts/eval_*.py, scripts/probe_*.py, scripts/report_*.py, test_results/**
---

# Measuring a change

Training is the cheap part. Every expensive mistake here has been in the
measurement, and the same four mistakes keep recurring.

## 1. An evaluation that does not prompt the changed task cannot see the change

**This cost a month.** Phase 2 added 795 rows under `optimize` and `iterate`,
and was judged by `eval_hard.py`, which prompts only:

```python
for task in ("line_comments", "explanation"):     # eval_hard.py
```

Those 795 rows produce `improved_code`. The evaluation never asked for it. The
flat result was arithmetically guaranteed before the GPU started, and was read
for a month as "the training failed". Probed on the task it actually trained,
the same checkpoint went **17% → 42%, p = 5.2e-04**.

Before any run, write down **which number should move if this works**, then
check that harness actually prompts the task being changed:

| harness | prompts |
| --- | --- |
| `eval_hard.py` | `line_comments`, `explanation` |
| `probe_defects.py` | `line_comments`, `explanation` |
| `eval_robustness.py` | `line_comments`, `explanation` |
| `probe_optimization.py` | `optimize`, `iterate` |
| `compare_quantizations.py` | `line_comments` |

A null result from a harness that does not exercise the change is not evidence
of anything.

## 2. Greedy decoding is not reproducible across machines

`temperature: 0` is deterministic *on one machine*. It is not deterministic
across machines: thread count and SIMD path change floating-point reduction
order, one token flips, and the whole generation diverges.

Measured, same weights, same prompts, same settings:

```
phase-1 GGUF on the Mac        7/55 problems named,  10/20 false claims
phase-1 GGUF on the Linux box  9/55 problems named,   8/20 false claims
```

**±2 of machine variance, larger than most effects being measured.** A
cross-machine comparison is not a comparison. Re-run the baseline on the
machine doing the measuring, in the same session, and say so in the report.

The committed numbers in `test_results/` were measured on the Mac. They are not
a valid baseline for anything measured elsewhere.

## 3. Scoring has been wrong eight times, and the shape repeats

Every time, a **name** was matched where a **concept** was meant:

| what matched | what it did |
| --- | --- |
| `cache` inside `// cache next node` | scored an unchanged function as memoised |
| a closed list of verbs | missed "recursively sorting" |
| a code pattern run against prose | could only ever return zero |
| pairs named before filtering | printed one program's source beside another's comments |
| a single word, "to avoid overflow" | scored as having found an overflow bug |
| `table`, in `const int* table` | scored a textbook iterative rewrite as TABULATED, so the sample could never pass |

The last one is instructive: `binary_search`'s **parameter** is named `table`,
and the verdict scanned the rewrite for `memo|dp|cache|table|...`. A perfect
`while` loop scored zero against `wants=("ITERATIVE",)`.

Defences that work:

- Match against **what the rewrite introduced**, not what it contains — compare
  to the original and subtract.
- Strip comments before reading code. `//S.C : O(26)` parses as a function.
- Ship the phrase that earned each point, so a human can audit it
  (`tests/test_hard_scoring.py` guards this).
- Assume the ninth exists and is in the same direction.

**Read the model's actual output before believing a score.** Four of five
"failures" on the stack samples were genuine; the fifth was this bug.

## 4. A post-repair metric cannot see the model degrade

`repair_anchors` relocates an anchor by its quoted text, so anchor validity
reads ~100% however badly the model counts lines. That is the right number to
*serve* and the wrong number to *track*:

```
phase 1   26/77 anchors landed on the right line unaided  (34%)
phase 2    6/72                                            ( 8%)
reported  100% both times
```

A 4× regression, invisible. `eval_hard.py` now reports `exact` and `repaired`
separately. Any metric computed after a repair step needs the pre-repair number
beside it.

## 5. Check the probe samples are not in the training data

Two of `probe_optimization.py`'s 17 samples — `fibonacci` and `gcd_euclid` —
appear verbatim in `test_results/distilled.jsonl`. Always report the
contamination-controlled number:

```
all 17 samples     28/68 (41%)
clean 15 samples   24/60 (40%)      <- report this one
```

The effect survived here. It will not always.

## 6. Decide what each outcome means before the run

After the numbers arrive, every outcome can be told as a success. Write the
reading down first — `model_improvement/REPORT.md` §3a-ii is the worked example:

| result | reading |
| --- | --- |
| target metric rises, controls hold | the change worked |
| nothing moves | the ceiling for this approach |
| target rises, controls fall | memorisation, not learning |

Name the **control group** explicitly. When testing `stack`, the controls are
`table` and `accumulator`; a gain that costs them is not a gain.

## 7. Share of the mixture, not count of rows

A task's influence is its share of the supervised tokens, not how many rows you
added:

```
159 verified pairs -> 253 verified pairs     1.9% -> 2.23% of the mixture
result: 25/60 -> 25/60, McNemar p = 1.0000
```

`add_verified_pairs.py` prints the share for this reason and tells you to
re-probe rather than believe the loss. Upsampling raises the share and raises
the memorisation risk with it — at `--repeat 30` each pair is seen thirty times,
so a falling loss is equally consistent with having memorised them.

## 8. What is worth measuring, and what is not

`eval_loss` on a random 1% slice of the same file measures teacher-forced
imitation of the annotation generator. It moved 0.4111 → 0.4120 across two runs
whose task scores differed by 25 points in one direction and 0 in the other. It
cannot see task ability and should never be quoted as if it can.

Perplexity 1.51 and token accuracy 88% look impressive and are mostly measuring
copying: **~47% of supervised tokens are verbatim code or fixed template**, and
one task (`complexity`, 22% of rows) has 7 distinct target strings, where a
constant answer scores 42.6%.

Generation harnesses that compile and run the output are the only ones whose
numbers mean what they appear to mean.

## Before writing a number into the report

1. Did the harness prompt the task that changed?
2. Was the baseline measured on this machine, this session?
3. Is the contamination-controlled number the one being quoted?
4. Is there a pre-repair number beside any post-repair one?
5. Did you read some raw output, or only the score?
6. Was the reading of this outcome decided before the run?
7. Is n large enough for the claim? 8 vs 16 of 55 is `p = 0.0625`; say "no
   detectable change" rather than "no change".
