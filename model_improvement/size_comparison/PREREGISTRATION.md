# 3B against 1.5B — what each outcome will mean, written before the run

Decided 2026-09-20, before any number arrived, because after the numbers arrive
every outcome can be told as a success.

## What is being compared

| | file | size label | layers |
| --- | --- | --- | ---: |
| **1.5B** | `models/gguf/qwen-cpp-review-v3-q4_k_m.gguf` | 1.5B | 28 |
| **3B** | `models/qwen2.5-coder-3b-q4_k_m.gguf` | 3B | 36 |

The 3B's GGUF header says `general.finetune: merged`, `general.name: "Qwen 3b
Merged"`, so it is a merged fine-tune rather than stock Qwen2.5-Coder-3B. That
is the *only* provenance available: there is no adapter, no `training_config.yaml`
and no `train.log` for it anywhere on disk, so the mixture, the step count and
the number of epochs are unknown. Every claim below is therefore about **this
checkpoint's behaviour**, and none of them is about what training produced it.

Both are measured on this Linux box, in one session, at `temperature: 0`, with
**the same tokenizer for both** (`Qwen/Qwen2.5-Coder-1.5B-Instruct`) so the
prompt bytes are identical. Cross-machine numbers are worth nothing here: the
same weights score 7/55 on the Mac and 9/55 on Linux.

Speed, measured with `llama-bench` before starting: **1.5B 7.53 tok/s, 3B 4.83
tok/s** generation on 8 CPU threads. The 3B is 1.56x slower, which is itself a
result for a CPU-served product.

## The four tiers, and which harness prompts them

Every tier prompts **both** `line_comments` and `explanation`, because those are
the two things being judged. A harness that does not prompt the task cannot see
it — that mistake cost this project a month.

| tier | harness | programs | what it is |
| --- | --- | ---: | --- |
| easy | `eval_tiers.py` | 6 | 4-9 line functions, correct, unambiguous |
| medium | `eval_tiers.py` | 6 | 12-16 line functions, correct, loops and edge cases |
| hard | `eval_hard.py` | 20 | 3-11 lines, each hiding one real defect |
| extra hard | `annotate_seed.py` | 6 | 45-58 line tree and graph programs |

`easy`/`medium` are the in-distribution case the product serves most of the
time; `hard` is defect finding; `extra hard` is the out-of-distribution end
where 9 of 20 explanations carried a false statement.

## The numbers that decide it

Primary, for "are the comments and the explanation any good":

1. **said something false** — a claim the code refutes. Worse than saying nothing.
2. **concepts described** — what a true description must contain, each point
   shipping the phrase that earned it.
3. **problems named** (hard tier only) — `found/of` over 55 sub-claims.
4. **anchors on the right line unaided** — reported *before* repair, because a
   post-repair number reads ~100% however badly the model counts.

Control: `easy` should be near ceiling for both models. If the 3B drops on
`easy`, the checkpoint is broken and nothing else in the table means anything.

## The reading, fixed now

| result | reading |
| --- | --- |
| 3B names more problems **and** says nothing more false, easy/medium hold | the extra parameters bought comprehension; ship the 3B if the latency is acceptable |
| nothing moves beyond noise | parameter count is not the constraint either — the sixth null, and the strongest form of the report's argument |
| 3B names more problems **but** also says more false things | more fluent, not more correct. A reviewer that invents defects is worse than one that misses them |
| 3B better on hard, worse on easy/medium | traded the common case for the rare one; do not ship |

`n` is small on purpose-built sets, so differences are tested with **McNemar
exact on paired items**, and anything that does not reach significance is
reported as "no detectable difference", never as "no difference".

## Known limits of this design, stated in advance

- 12 easy/medium programs and 6 extra-hard programs are few. They can show a
  large effect and cannot rule out a small one.
- The easy/medium concept patterns are new code, so they are the most likely
  place for a ninth scoring bug. One was already found and fixed while writing
  them: `unsorted` matched the pattern for `sorted`, so a description saying the
  opposite of the truth scored a point.
- The 3B may have been trained on different data, not merely more parameters.
  Without its config, "3B is better" and "its mixture was better" cannot be
  separated. Any conclusion has to say so.
