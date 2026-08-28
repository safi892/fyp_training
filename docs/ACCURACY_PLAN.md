# Making the model more accurate on code it has not seen

Three goals: explain code accurately, comment it accurately, and optimise it —
on **unseen** input. This plan is ranked by what the measurements and the
literature jointly support, and it names what not to do as carefully as what
to do.

Read `.claude/skills/measuring-changes/SKILL.md` before acting on any of it.

---

## The diagnosis

The model is not bad at explaining code. It is bad at explaining code whose
*shape* it has not seen.

| | in-distribution | out-of-distribution |
| --- | ---: | ---: |
| anchors valid | 99% | — |
| loops wrongly called recursive | 1/46 | — |
| explanations carrying a false statement | — | **9/20 (45%)** |

The axis is length and shape. Measured over `task_mixture_verified.jsonl`:

```
p10 6 · p50 13 · p90 30 · p99 52 · max 141 lines
>= 30 lines : 6,784 rows (10.8%)
>= 45 lines : 1,385 rows ( 2.2%)
>= 60 lines :   345 rows ( 0.5%)
```

The 45% failures were on **45-58 line** tree and graph programs, using shapes
that are 1.6-1.9% of the corpus. **This is a generalisation gap, not a capability
gap**, and that determines which interventions can possibly work: anything that
only adds more of the same distribution cannot reach it.

Already established here, and not to be re-derived:

- Scaling verified pairs 159 → 253 changed nothing (**p = 1.0000**).
- Improvement plateaued at step ~300 of 1035; 98% of the LR budget was spent by
  step 800.
- The adapter carries 7.7 trainable parameters per supervised token and still
  does not overfit — eval loss sits *below* train. Capacity is not the limit.

---

## Tier 1 — no GPU, generalises by construction

These check a claim against **the code in front of them**. That is why they work
on unseen input: nothing about them depends on having seen the shape before.
This is the same move as `repair_anchors`, which is 100% valid with 0 dropped on
every corpus it has been run against.

### 1.1 Extend claim checking ⭐ start here

`claim_checks.py` catches **1 of 9** false explanations. It checks two claim
types — recursion, and declared data structures. Every claim the source can
answer is checkable:

| claim in prose | checkable against the source |
| --- | --- |
| "iterates over the array" | is there a loop over that variable? |
| "returns the sum / product / maximum" | the operator in the return expression |
| "modifies the array in place" | is the parameter a reference or pointer? |
| "handles the empty case" | is there a zero or null guard? |
| "sorts in ascending order" | the comparison direction in the swap |
| "returns -1 when not found" | does `-1` appear in a return? |
| "uses two pointers" | how many index variables move? |

Each type added works on unseen code permanently. The design rule from the
existing module holds: **fire only when the opposite is established from the
source.** A checker that fires on uncertainty stops being evidence, and a filter
that drops correct output is worse than no filter — precision was 1 in 3 until
the first version was run on real output.

**Measure against the nine known false explanations**, not against intuition.

### What has been tried, and the number that settled each

| claim type | sentences claiming it | fires | verdict |
| --- | ---: | ---: | --- |
| **divisibility** | 4 | **4** | **shipped** — 2 → 4 catches, 0 false positives on 92 in-distribution programs |
| prints / outputs | 43 | 0 | every source has a `cout`; nothing to refute |
| empty / null guard | 10 | 0 | every source has a guard |
| traversal order (pre/in/post) | 3 | 0 | all three sources match their prose |

The last three were implemented and measured before being rejected, not guessed
at. **Do not re-derive them.** A check that fires zero times on the evidence
available cannot have its precision tested, and shipping one is how a filter
that drops correct output gets written.

Two bugs were found while measuring them, both of which would have produced
false positives on correct code:

- `\bmultiple of\s+\d\b` never matches "multiple of 10" — the word boundary
  after a single digit falls *inside* the number. `\d+` fixes it.
- Scanning for the recursive calls without bounding the search to the function
  body ran into `main()`, so `postorder(sample())` appeared *after* the `cout`
  and a correct postorder traversal read as inorder. `_block()` bounds it.

**The remaining false explanations are not decidable from the source.**
`flood_fill`'s "replaces the starting cell" is a wrong summary made of true
words; `tree_postorder`'s reversed mechanism describes two stacks that both
exist. Catching those needs semantics, not pattern matching, which is the
boundary `docs/DETECTABILITY.md` already states. Tier 1.2 is the response to it:
if a claim cannot be refuted, generate several and prefer the one with fewest
refutable claims.

### 1.2 Sample and verify at inference — MEASURED, works

Over the twenty out-of-distribution seed programs, five samples each, sample 0
drawn at temperature 0 so the baseline is what serving does today:

| | single sample | best of 5 |
| --- | ---: | ---: |
| total objections | **24** | **4** |
| clean answers | 6/20 | **16/20** |

Improved 12, unchanged 8, worse 0. McNemar exact **p = 4.88e-04**.

Two caveats belong with that number. *Worse = 0* is largely structural rather
than empirical: sample 0 is always among the candidates, so the selection can
only lose if the content filter discards it. And **sample 0 was already the best
answer only 6/20 times** - in fourteen cases the deployed answer was not the best
one the model produced, which is the finding.

Where it fails is as informative. Four programs stayed flawed, and each had an
objection in *every* sample - `tree_count_leaves recursive` scored [1,1,1,1,1].
That is a persistent error rather than a sampling artefact, and no amount of
resampling reaches it. The variance elsewhere is enormous - [2, 11, 3, 2, 0] on
one program - which is exactly the condition under which picking is worth doing.

Cost: 5x inference. At 940 MB and ~12 tok/s on a CPU that is seconds, which is
the whole reason it is affordable here.

### The original argument

Small models can self-verify when given tools, and sampling a larger pool
improves verification accuracy — a 3B model beats far larger ones this way
([T1, 2025](https://arxiv.org/html/2504.04718v1);
[Sample, Scrutinize and Scale, 2025](https://arxiv.org/abs/2502.01839)).

`checked_response.py` is already the verifier. What is missing is the sampling:
generate 5 explanations at temperature ~0.7, run each through the checker,
return the one with fewest contradictions. Costs 5× inference, needs no training,
and the cost is affordable precisely because the model is 940 MB.

### 1.3 Execution-grounded comment checking

~20% of comments from the best LLMs contain demonstrably inaccurate statements,
detectable by generating a test from the comment and running it
([Kang, Milliken & Yoo, 2024](https://arxiv.org/pdf/2406.14836)).

`verification.py` already compiles and runs C++ with a generated driver. A
comment claiming "returns the largest element" is a claim a driver can falsify.
Narrower than 1.1 and more expensive, so it comes after it.

---

## Tier 2 — needs a GPU, and only these two

### 2.1 Train on longer code

The failures are at 45-58 lines; **2.2%** of rows are ≥45 lines. This is the
clearest data gap in the corpus and, unlike the tree/linked-list hunt, it is
fixable without a new source: `chunking.py` implements cAST split-then-merge and
can synthesise multi-function files by concatenating related snippets. PLAN.md
§Phase 5 already specifies this.

### 2.2 Finish the share experiment

`--repeat 30` puts the verified slice at 12.05% instead of 2.23%. Bundle is
built; the reading of each outcome is pre-registered in
`model_improvement/REPORT.md` §3a-ii. This is the last untested variable for the
`stack` transformation (3/20 against `table` 12/20 and `accumulator` 14/28).

---

## Tier 3 — do not do these

| | why |
| --- | --- |
| More same-distribution verified pairs | 159 → 253 gave p = 1.0000 |
| **Reasoning-trace distillation** | see below |
| Bigger LoRA rank, more epochs | plateaued at step 300; no overfitting at 7.7 params/token |
| More correct C++ | composition problem: targets asserting correctness outnumber defect claims 5.9 : 1 |
| Tree/linked-list pair generation from this corpus | 20 tree functions, 0 linked-list, among 582 drivable |

### On reasoning-trace distillation

This was recommended earlier in the project and is **withdrawn for the unseen-data
goal**. [Enhancing Generalization in CoT Reasoning for Smaller
Models](https://arxiv.org/html/2501.09804v1) (2025) reports that CoT distillation
causes "the shift of model ability from generalization to memorization", and that
the student "performs CoT reasoning well on the well-informed source domain but
fails to generalize to the new, unseen domain."

At 1.5B that trades exactly the property being asked for. If it is revisited, use
the validator-filtered variants (CODI, DocVAL) that the same literature reports
generalise better than explicit CoT.

---

## Order of work

| # | action | GPU | attacks |
| ---: | --- | :---: | --- |
| 1 | Extend `claim_checks.py` | no | false statements on unseen code |
| 2 | Sample-5-and-verify in serving | no | false statements, any code |
| 3 | Synthesise 45-90 line training files | yes | the measured 2.2% length gap |
| 4 | Share experiment | yes | the `stack` transformation |
| 5 | Execution-grounded comment checks | no | comment accuracy specifically |

Items 1 and 2 need no GPU and work on unseen code by construction. Start there.

---

## Why this is the right shape for the report

The project's thesis is that **reliability and understanding are separable**.
Every Tier 1 item makes the model more reliable *without* making it understand
more: it does not teach a 1.5B model to comprehend tree code, it makes the model
unable to say false things about tree code and detectable when it tries.

That is consistent with the thesis rather than a retreat from it, and it extends
the contribution already claimed in `docs/DETECTABILITY.md` — that a
line-anchored format makes hallucination *detectable* rather than merely
unlikely. Tier 1 is that same argument applied to prose.

---

## Sources

- [Enhancing Generalization in Chain of Thought Reasoning for Smaller Models](https://arxiv.org/html/2501.09804v1) (2025)
- [T1: Tool-integrated Self-verification for Test-time Compute Scaling in Small Language Models](https://arxiv.org/html/2504.04718v1) (2025)
- [Sample, Scrutinize and Scale: Effective Inference-Time Search by Scaling Verification](https://arxiv.org/abs/2502.01839) (2025)
- [Identifying Inaccurate Descriptions in LLM-generated Code Comments via Test Execution](https://arxiv.org/pdf/2406.14836) (2024)
- [Citation-Grounded Code Comprehension](https://arxiv.org/pdf/2512.12117)
- [Small Encoders Can Rival Large Decoders in Detecting Groundedness](https://arxiv.org/html/2506.21288) (2025)
