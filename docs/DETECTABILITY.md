# Making wrong output detectable

Every capability measurement in this project points the same way, and it is not
the direction the work started in. Asking the model to be better has a ceiling
that arrives quickly. Asking whether the model's answer can be *checked* does
not.

This chapter is the argument for the second, the evidence for it, and an honest
account of where it stops working.

---

## 1. The measurements that force the argument

### Fine-tuning bought format, not comprehension

The ablation is the load-bearing result. Untuned Qwen2.5-Coder-1.5B against the
fine-tune, same twenty programs:

| | base | fine-tuned |
| --- | ---: | ---: |
| usable JSON | 0/20 | **20/20** |
| anchor validity | 68% | **100%** |
| problems named | 9/55 | 7/55 |

The first two rows are what training changed. The third is what it did not — and
the base model had 3.3× more text scored, so that comparison already favours the
base by construction.

### Prompting has a ceiling, and it is low

Recursion into iteration, measured on **60 real submissions** drawn from
`cleaned/merged_cleaned.jsonl`, with their authors' own identifiers and nothing
renamed:

| wording | rewrote the function |
| --- | ---: |
| the wording that ships today | **3/60** |
| naming the container to use | **10/60** |
| a worked before/after example | 6/60 |

All three successes of the shipped wording are the same function — `gcd`, turned
into the identical Euclidean loop each time. That is recall of one memorised
pattern, not a capability.

Better wording more than triples the result and still leaves 83% unconverted.
The prompt change is worth shipping (`TASKS["iterate"]` in `prompt.py`) and it is
not a fix.

### Written samples overstate what serving will do

The same question asked of seventeen functions written for the purpose:

| what the rewrite needs | passed |
| --- | ---: |
| a cache (memoisation) | 5/5 |
| a running variable | 4/7 |
| a real container | **0/5** |

Between 47% and 100% on hand-written samples against 17% on real submissions.
The samples were short, single-function and textbook-clean; real code is
embedded in classes, surrounded by helpers, and written by someone in a hurry.

**A capability number measured on code you wrote yourself is not a serving
number.** It answers "can the model do this", which is a different question from
"will it do this for a user", and only the second one ships.

### Description fails the same way, on the same code

Twenty programs of tree, graph and pointer code, each written twice — once
recursively, once with an explicit container, under the **same function name**,
so a description following the name rather than the code is wrong about one half.

| | |
| --- | ---: |
| valid JSON | 13/13 |
| anchors quoting a real line | 176/188 (94%) |
| named the container the code declares | 11/11 |
| **explanations containing a false statement** | **9/20** |

Every mechanical metric passes. The prose is a coin flip.

The clearest case is `sum_digits_tree`, whose explanation says:

> Count all root-to-leaf paths whose node values form a decimal number
> **divisible by 10**.

The function sums the root-to-leaf numbers. There is no divisibility test in it.
The model invented a purpose and stated it identically and confidently for both
the recursive and iterative halves.

**This is a worst case, not the serving rate**, and the same test run on
in-distribution code says so. The 46 collected recursion/iteration pairs -
92 programs of ordinary competitive-programming C++, p50 29 lines - give:

| | off-distribution (20 tree/graph programs) | in-distribution (92 programs) |
| --- | ---: | ---: |
| valid JSON | 13/13 | 89/90 |
| anchors quoting a real line | 176/188 (**94%**) | 636/644 (**99%**) |
| loops described as recursive | 1/10 | **1/46** |

Anchor validity recovers to 99% and the false-recursion rate falls by a factor
of four. The seed programs are 45-58 lines against a corpus p50 of 14 and p99 of
53, and they use shapes that are 1.6-1.9% of the training data:

| shape | share of the 19,033-row corpus |
| --- | ---: |
| `struct Node` (tree, linked list) | 1.9% |
| `std::stack` | 1.6% |
| `std::queue` | 1.4% |

The labels themselves are not the problem: only 0.7% of corpus annotations claim
recursion the code does not contain, and 1.9% name a container it does not
declare. **The training data is not wrong. It is missing these shapes**, and the
failure rate tracks how far the input sits from them.

---

## 2. The argument

Three of those numbers can be improved by training and one cannot be improved
cheaply at all. But all four have a property that has nothing to do with the
model: **the output can be checked against the code it describes.**

That was always the design of the anchoring layer, stated for one field:

> Comments are `{line, code, comment}` records, never a rewritten file. The
> quoted line is checked against the submission, so an invented comment is
> *detectable*.

The claim of this chapter is that the same move generalises, and that it is worth
more than the next fine-tune:

| field | what the code proves | mechanism |
| --- | --- | --- |
| `line_comments` | the quoted line exists | `line_anchoring.repair_anchors` |
| `improved_code` | it computes the same thing | `verification.verify` — compile both, run both, compare |
| `explanation` | the source does not say otherwise | `claim_checks.check_claims` |

`checked_response.check_response` composes all three. Each existed before;
nothing had put them on the same response, so a served answer had its anchors
repaired while its `improved_code` went out unverified and its prose went out
unread.

**The trade is deliberate: recall falls, precision rises.** For a review tool
read by a student, that is the correct direction. A confident wrong comment is
worse than no comment, because it is read, believed and acted on.

---

## 3. What it catches, replayed over real output

Run over all 112 saved responses, without re-calling the model:

| | 20 off-distribution | 92 in-distribution |
| --- | ---: | ---: |
| anchors dropped (quoted a line not in the file) | 12 | 8 |
| comments dropped (contradicted their own line) | 1 | 0 |
| explanation sentences flagged | 1 | 1 |
| responses marked `needs_review` | 8/20 | 7/92 |

All three content catches were checked by hand and all three are real:

> `stack<pair<int, int>> pending;` — commented *"BFS queue for flood-filling."*

> *"Subsequent calls process the left and right partitions, **recursively**
> sorting them until the stack is empty."* — over a function containing no
> recursion.

> *"For each possible split point `i`, **recursively** try to match the prefix"* —
> over a `while` loop.

**Precision was 1 in 3 before this was run on real output.** Two of the first
three flags were wrong, and neither would have been found by writing more tests:

- *"Prints the phrase `"I love Recursion"` exactly n times"* — a correct
  description of a loop. The word sits inside a quoted string literal the program
  prints, and a quotation is not an assertion.
- *"...leading to **stack** overflow"* — the runtime stack, which no program
  declares, not a `std::stack`.

Both are excluded now, and both have a test. A filter that drops correct output
is worse than no filter, because it costs the user something real in exchange for
nothing.

On `improved_code` the check is decisive rather than partial, because behaviour
is decidable: a rewrite that prints something different is rejected outright.
The seed set exercises this — 10 of 10 pairs pass compile-run-compare, while 9 of
the 76 hand-collected pairs were caught printing different output, two of them
because the *original* was buggy.

---

## 4. Where it stops working, stated plainly

**It catches 1 of the 9 wrong explanations.**

That is the honest limit and it should not be buried. The checks fire on claims
the source can refute — a named structure that is not declared, recursion in a
function that never calls itself. They cannot touch:

- `sum_digits_tree`'s invented "divisible by 10" — nothing in the code
  contradicts a purpose that was never mentioned
- `tree_postorder`'s reversed mechanism (children onto the output stack rather
  than the node) — both stacks exist, so no structure claim is false
- `flood_fill`'s "replaces the starting cell" — a wrong summary made of true words

Detectability is bounded by decidability. `improved_code` is fully checkable
because equivalence can be tested by running it. Anchors are fully checkable
because a quote is a string. Free prose is checkable only where it makes a claim
the source happens to answer, which is a minority of the sentences it writes.

A checker that guessed beyond that boundary would stop being evidence. The
implementation therefore fires only when the opposite is established from the
source; vague, incomplete and badly written prose all pass, because there is no
way to be sure they are wrong.

---

## 5. What this means for the contribution

The result is not "we built a model that reviews C++". It is:

> Reliability and understanding are separable. The usual metrics measure the
> first while being read as evidence of the second — and where the two come
> apart, the useful response is to make the model's output checkable rather than
> to make the model larger.

The evidence for the first sentence is the ablation, the 13% defect rate, and
the 9/20 false-explanation rate reproduced on unseen code. The evidence for the
second is section 3: the same errors, caught by code, without retraining
anything.

The honest qualifier is section 4. Two of the three fields are fully checkable.
The third is checkable at the edges, and that is a real limit rather than a
detail — which is itself worth reporting, because it says where the remaining
work is.

---

## 6. Reproducing every number here

```bash
# fine-tuning bought format, not comprehension
uv run python scripts/report_ablation.py

# prompting has a ceiling, on real submissions with their authors' names
uv run python scripts/probe_corpus_recursion.py --limit 60

# written samples overstate it
uv run python scripts/probe_optimization.py --draws 3
uv run python scripts/probe_wordings.py --probe test_results/optimization_probe_v3.json

# description fails on the same code
uv run python scripts/annotate_seed.py
uv run python scripts/annotate_seed.py --report-only    # rebuild the markdown, re-scored

# improved_code is decidable
python3 scripts/verify_optimization_pairs.py my_data_annotation/recursion_optimization
```

Every scored claim in `test_results/seed_annotation.md` is printed with the
sentence that produced it. Four scoring bugs were found while producing this
chapter — a keyword matched inside a comment, a closed list of verbs, a code
pattern matched against prose, and a function name guessed by regular expression
— and **all four flattered the model**. That direction is consistent with the
three earlier scoring errors recorded in `CLAUDE.md`, and it is the reason no
number here is quoted without the phrase behind it.
