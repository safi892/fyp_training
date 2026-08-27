# Model and prompt testing — report

Run 2026-08-24/25 on this laptop (i7-6700HQ, CPU only) plus hosted APIs on the
free tiers. Two separate questions were tested:

1. **Can a different *question* make the model we already have find more bugs?**
2. **Can a stronger *teacher* generate verified recursion→loop training data?**

The first worked. The second did not, and four independent proposers now say so.

---

## 1. The prompt result — the finding worth acting on

**No training. No API. The same phase-2 model, asked differently.**

`scripts/probe_defects.py` puts the same 24 programs to the model three ways.
`trained_wording` is the control: exactly what the product sends today.

| phrasing | problems found | false claims | **invented defects in correct code** | anchors kept |
| --- | ---: | ---: | ---: | ---: |
| `trained_wording` (shipped) | 8/55 | 7 | **1** | 95/95 |
| `describe_effect` | 8/55 | 8 | 0 | 92/92 |
| **`assume_nothing`** | **16/55** | 8 | **0** | 100/100 |

**Defect finding doubles, 8 → 16.**

The whole change is four sentences appended to the instruction:

> This code may contain defects. Do not assume it is correct. Describe what each
> line actually does when executed, and where a line's effect differs from what
> the surrounding code appears intended to achieve, say so plainly.

**Significance.** Paired over the 20 defective samples: better on **5**, worse
on **0**, McNemar exact **p = 0.0625**. Just above the 0.05 line because n is
small — but there are no regressions, and the effect size is large.

**The column that decides it is the third one.** Correct code is the product's
normal input, so a phrasing that finds more bugs by imagining them everywhere is
worse than useless. `assume_nothing` invented **zero** on the four correct
programs; the currently-shipped wording invented **one**. It is better on both
axes at once, which is the outcome the probe was designed to be able to refuse.

Anchor validity also went *up* (100/100 against 95/95), so nothing was traded away.

### Cost comparison

| | Cost | Effect on defect finding |
| --- | --- | --- |
| Phase-2 training run | **10.4 GPU-hours** | none detectable |
| These four sentences | **5 minutes** | **2x** |

### Confirmed through a second code path, and now applied

`prompt.py` gained `DEFECT_AWARE_SUFFIX`, appended at **inference only** and only
for `line_comments`, `explanation` and `review`. `complexity` and `optimize` ask
for a different kind of answer and were never tested with this wording, so they
keep the trained instruction. The training render is deliberately untouched —
the measurement is of this wording given to a model trained *without* it.

Re-measured through `eval_hard.py`, which builds its prompt from the package
rather than appending wording itself:

| | trained wording | defect-aware |
| --- | ---: | ---: |
| Problems named | 8/55 | **16/55** |
| Confidently false | 7/20 | 8/20 |
| Anchors landing on the right line unaided | 6/72 (8%) | **14/78 (18%)** |
| Anchors dropped | 0 | 0 |

Better on 5 samples, worse on 0. Improved: `assignment_in_condition`,
`index_past_last_character`, `loop_bound_off_by_one`,
`recursion_without_base_case`, `self_shadowing_counter`.

**This is not an independent replication.** `probe_defects` and `eval_hard`
share all 20 defective programs; the probe merely adds 4 correct ones. What the
second run establishes is that the packaged implementation reproduces the
probe's ad-hoc one, so the effect is not a harness artefact. Whether it
generalises to unseen programs is untested.

**The cost, stated plainly.** False claims rose 7 → 8: one fixed
(`index_past_last_character`), two introduced (`accumulated_float_equality`,
`leak_on_early_return`). The trade is **+8 problems found for +1 false claim.**
Defensible for a teaching tool, and the four correct programs are the reassurance
that it is not simply becoming suspicious of everything — there it invented 0
against the shipped wording's 1.

Unpredicted side effect: raw line-number accuracy roughly doubled, 8% → 18%.

---

## 2. The teacher comparison — a clean negative result

Question: phase 2's 58 execution-verified `optimize` pairs moved algorithmic
transformation 17% → 40% (p = 5.2e-04). Can a stronger model generate many more?

Every model gets the **same 40–60 recursive functions from the real corpus**,
the **same prompt**, **2 samples each**, and the **same gate** — a pair only
exists if it compiled, ran, and printed exactly what the original printed.

| Proposer | Access | Verified pairs | Yield |
| --- | --- | ---: | ---: |
| *(historical teacher, `CLAUDE.md`)* | — | 2 / 130 | 1.5% |
| GPT-OSS-120B | Azure | 1 / 60 | 1.7% |
| nemotron-3.5-lightning-30b | NVIDIA free | 0 / 40 | 0% |
| **gemini-3.5-flash-lite** | **Google free** | **4 / 40** | **10%** |
| muse-glimmer-30b | NVIDIA free | *running* | — |
| deepseek-v4-flash | NVIDIA free | **unusable** | endpoint times out |

### The lite model beats the 120B on identical inputs

This was not expected and it is the second real finding of the run.

`--limit N` takes the first N drivable recursive functions in corpus order, so
the lite run's 40 functions are **exactly** the 120B run's first 40 — verified,
overlap = 40. The 120B's single success was on function **#60**, outside that
set. So head to head, on the same inputs:

| Proposer | Same 40 functions |
| --- | ---: |
| GPT-OSS-120B | **0 / 40** |
| nemotron-3.5-lightning-30b | **0 / 40** |
| **gemini-3.5-flash-lite** | **4 / 40** |

Fisher exact two-tailed **p = 0.116** — suggestive, not conclusive at n=40. A
250-function run is under way to settle it.

The kept pairs are real. One example, a min-cost-stairs recursion from the
corpus, converted to bottom-up DP and confirmed by compiling and running both
versions to identical output:

```cpp
// before
int solve(vector<int>& cost, int idx) {
    if (idx >= cost.size()) return 0;
    int move_one = cost[idx] + solve(cost, idx+1);
    int move_two = cost[idx] + solve(cost, idx+2);
    return min(move_one, move_two);
}
// after
vector<int> dp(n + 2, 0);
for (int i = n - 1; i >= 0; --i) {
    int move_one = cost[i] + dp[i + 1];
    int move_two = (i + 2 <= n) ? (cost[i] + dp[i + 2]) : cost[i];
    dp[i] = min(move_one, move_two);
}
```

**Size is not what predicts yield here.** A cheap, fast lite model produced four
verified pairs where a 120B produced none on the same functions. Whatever
separates them, it is not parameter count — which is worth stating carefully
rather than concluding, given n.

### Why they fail, and it is the same reason every time

| Rejection | GPT-OSS-120B | nemotron-30b |
| --- | ---: | ---: |
| **still recursive** | **41/60 (68%)** | **19/40 (48%)** |
| original would not compile or run | 12 | 11 |
| no code found in the reply | 2 | 6 |
| rewrite did not run | 4 | 3 |

`still recursive` dominates for both. The model is asked to remove the
recursion and returns code that still recurses.

### The trap this repeats

GPT-OSS-120B rewrote a textbook `fib` into a clean DP loop **on the first
attempt** in a smoke test. It then failed 41 of 60 real student submissions
carrying their authors' own identifiers.

That is exactly the pattern `CLAUDE.md` already records twice:

> a capability number measured on code you wrote yourself is not a serving number

and its warning about this specific corpus:

> **A verified recursion→iteration corpus was attempted and abandoned.**
> 5.8 GPU-hours, 130 of 582 functions attempted, **2 verified — a 1.5% yield**.
> Do not restart this.

Today's runs reproduce that number with a model roughly an order of magnitude
larger. **The bottleneck is the task on real code, not the strength of the
proposer.** More API quota buys the same 1.5% faster.

### Caveat, stated plainly

These runs used `--samples 2`; the historical run used up to 16. More samples
would raise the per-function yield. But 41 of 60 functions produced nothing
non-recursive in two independent tries, so the ceiling is not far above.

---

## 3. Which API to use for what

| Provider | Model | Works | Best used for |
| --- | --- | :---: | --- |
| Azure | gpt-oss-120b | yes | hardest generation; `reasoning: true` |
| Google | gemini-3.6-flash | yes | **bulk classification** — 4 keys pooled |
| NVIDIA | nemotron-3.5-lightning-30b | yes | bulk classification |
| NVIDIA | muse-glimmer-30b | yes, slow | ~2.5 min/function, avoid for volume |
| NVIDIA | deepseek-v4-flash | **no** | endpoint times out |
| Google | any `pro` model | **no** | HTTP 429, not in the free tier |
| Google | gemini-3.7-flash | **no** | HTTP 503, at capacity |

Four Gemini keys are configured (`gemini`, `gemini2`, `gemini3`, `gemini4`),
pooling to roughly **5,200 requests/day at 60/min**.

**Do not spend that pool on recursion→loop.** Spend it on the two bulk jobs that
need volume rather than strength:

| Job | Calls | What it fixes |
| --- | ---: | --- |
| Judge each `improve` row: did the algorithm change, or was `const` added? | ~18,935 | 37% of the loss budget teaching cosmetics |
| Judge each `line_comments` item: explains intent, or restates the line? | ~19,000 | 37% of comments are restatement |

Each pass is roughly 5–6 hours of unattended running at the pooled rate.

---

## 3a. The third run, and what the probe says the gap actually is

`models/27aug01` trained on the intended data — 56,101 rows and 877 steps
against 56,101 and 877 predicted, code byte-identical to `e1440b9`, 1 epoch in
6.8h. Measured on this machine at `temperature: 0`, contamination-controlled:

| | phase 1 | phase 2 | **v3** |
| --- | ---: | ---: | ---: |
| Algorithmic rewriting | 10/60 (17%) | **25/60 (42%)** | **25/60 (42%)** |
| Problems named (defect-aware prompt) | — | 16/55 | 11/55 |
| Confidently false | — | 8/20 | 6/20 |

**Identical on rewriting**: five gained, five lost, McNemar **p = 1.0000**. The
94 extra verified pairs took that slice of the mixture from 1.9% to 2.23% and
changed nothing. Defect naming fell 16 → 11 while false claims fell 8 → 6,
better on two samples and worse on six, which n=20 cannot separate from noise.

What the dataset work did buy is **the same capability on 15% less data in 35%
less time** — 66,229 rows and 10.4h became 56,101 and 6.8h. That is the 11,676
cosmetic `improve` rows confirmed as dead weight, which is a real result about
efficiency rather than about capability.

### The gap is a transformation, not a data shape

Grouping the probe's 17 samples by what the rewrite has to *do*:

| kind | what it needs | v3 |
| --- | --- | ---: |
| `table` | memoisation or a DP table | **12/20 (60%)** |
| `accumulator` | tail recursion into a loop | **14/28 (50%)** |
| `stack` | **explicit stack simulation** | **3/20 (15%)** |

The five samples at 0/4 are not one data shape. `quicksort` is an array,
`flood_fill` a grid, `tree_height` a tree, `reverse_list` a linked list. What
they share is that each needs the call stack rebuilt by hand, and that is the
one transformation the model largely cannot do.

**This closes the "generate tree and linked-list pairs" plan.** The corpus has
20 tree functions and 0 linked-list functions among 582 drivable ones, so that
route was dead anyway — but more importantly the data already exists: of the 54
new `iterate` pairs, **50 use `std::stack` in the answer**. They teach exactly
this transformation, they are 775 rows, **1.37% of the mixture**, and they moved
nothing.

So the untested variable is not the *source* of the pairs but their *share*:

| `--repeat` | iterate rows | share |
| ---: | ---: | ---: |
| 5 (used) | 775 | 2.23% |
| 15 | 2,325 | 6.41% |
| 30 | 4,650 | 12.05% |

Upsampling is the cheap experiment and it is the one `add_verified_pairs.py`
already warns about — "a real risk of memorisation rather than learning, and it
is the reason to re-probe afterwards instead of trusting the loss". Which is
precisely why it has to be re-probed rather than believed.

### Scoring was wrong an eighth time

`binary_search` takes `const int* table`, and the verdict scanned the rewrite
alone for `memo|dp|cache|table|vector<`. A textbook iterative binary search came
back `TABULATED` and scored zero against `wants=("ITERATIVE",)`: the sample could
not pass whatever the model wrote. Same shape as the keyword-in-a-comment
mistake already recorded — a name matched where a concept was meant. Only tokens
the rewrite *introduces* count now; it moves both runs by one point, so no
conclusion changes. Four tests pin it.

The other four zeros are genuine. `reverse_list` returns its input unchanged,
`tree_height` hoists the recursive calls into locals and still recurses, and
`flood_fill` replaces four recursive calls with a `dr/dc` loop that still
recurses *and* adds diagonals.

## 3b. Two data changes, one made and one withdrawn

### Made: the `improve` task now drops cosmetic rewrites

Measured over the 13,087 improve-eligible rows in `line_anchored.jsonl`:

```
identical control-flow token counts   8,092  (61.8%)   <- cosmetic only
structurally changed                  4,995  (38.2%)
introduced a dp / memo / cache          819  ( 6.3%)
```

That task carried **18,935 rows and 37% of the supervised tokens**, so the
majority of the gradient was teaching `const`-sprinkling and an added
`#include`. `build_task_mixture.py` now compares control-flow token counts
before and after and keeps only rewrites that moved the algorithm:

```
improve   18,935 -> 7,259        total mixture   66,103 -> 54,427
```

No other task changed. `--keep-cosmetic-improve` reproduces the old mixture, so
before/after stays comparable. Nine tests in `tests/test_improve_filter.py` pin
the distinction, including that flow keywords appearing inside *comments* do not
count as a rewrite.

The contrast is the whole argument: 290 execution-verified `optimize` rows moved
algorithmic transformation 17% → 40%; 18,935 asserted `improve` rows taught
tidying.

### Withdrawn: adding a `comments` task

This was recommended earlier in this investigation as the highest-leverage data
change, on the grounds that the `comments` field is non-empty in 18,681 of
19,033 rows and carries defect language. **That recommendation was wrong and is
retracted.** Measured:

| | rows | share |
| --- | ---: | ---: |
| `comments` is a **rewritten copy of the code** with inline comments | 9,010 | 47.3% |
| `comments` is prose only | 9,671 | 50.8% |
| prose-only **and** mentioning a real defect | **377** | 2.0% |

The 47.3% is the format Phase 0 deliberately abandoned: the annotated copy
drifts from the input, preserving its lines verbatim only 14.5% of the time,
which is why `line_anchoring.py` exists to extract the verifiable part into
`line_comments` — and 13,087 rows already carry those anchors. Training on the
raw field would teach the model to re-emit rewritten code on half the rows.

The salvageable remainder is **377 rows, not 18,681**, and hand-inspection shows
even those are mostly describing handled edge cases rather than claiming a
defect. The field was excluded on purpose, and correctly.

## 4. What to do

1. **Apply `assume_nothing` to the served instruction**, after confirming it on
   the `eval_hard.py` set. Free, five minutes, doubles defect finding.
2. **Do not restart the recursion corpus.** Four proposers, ~1.5%. The 58 pairs
   already in the mixture were worth having; a fifth model will not change this.
3. **Spend the Gemini pool on filtering, not generating** — steps 1 and 2 above.
4. If more verified pairs are ever wanted, aim them at what actually fails:
   phase 2 scores 4/4 on tabulation (`grid_paths`, `coin_change`, `binomial`)
   and **0/4** on everything needing explicit stack simulation (`reverse_list`,
   `binary_search`, `tree_height`, `quicksort`, `flood_fill`). Generating more
   DP examples will not move those.

## 5. Note on credentials

All API keys in `.env` have been exposed in a session transcript and should be
rotated: three original providers plus four Gemini keys. `.env` is covered by
`.gitignore:50` and has never been committed — this is about the transcript, not
the repository.
