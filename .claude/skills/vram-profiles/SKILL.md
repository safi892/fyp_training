---
name: vram-profiles
description: >-
  Hardware-specific training configuration profiles for QLoRA fine-tuning of a
  1.5B model. The primary target is the Kaggle free-tier T4; the 24GB, 32GB,
  48GB and 80GB profiles are kept for reference only, alongside CPU/MPS
  smoke-test settings. Use this skill whenever choosing or changing batch size,
  gradient accumulation, max sequence length, packing, optimizer or precision
  settings, whenever writing a config file, and whenever diagnosing an
  out-of-memory error. Do not guess these values from memory.
paths: configs/**, src/config.py
---

# VRAM profiles

## Our hardware

Kaggle free-tier notebooks: **2 × Tesla T4, 16GB each** (Turing, compute
capability 7.5), 32GB system RAM, 9–12h session ceiling, roughly 30 GPU-hours
per week.

Two T4s are **two separate 16GB devices, not 32GB pooled**. Anything that does
not fit in 16GB does not fit, and the second card does not change that. We train
on a single device for now:

```bash
export CUDA_VISIBLE_DEVICES=0
```

Moving to both cards is a throughput decision, not a memory one, and it is a
later change. Weekly GPU hours are the binding constraint — see the `kaggle-run`
budget check before launching anything long.

## How to use this

Pick the profile matching the GPU, then write it into a config file under
`configs/`. Never hardcode these numbers anywhere else. Effective batch size is
`per_device_batch * grad_accum`; keep it constant across profiles so results stay
comparable, and change only how it is split.

Target effective batch size for this project: **32**.

## Profiles

| Profile | per_device | grad_accum | max_seq_len | packing | precision | optimizer |
|---|---|---|---|---|---|---|
| **kaggle-t4 (primary)** | 2 | 16 | 1024 | on | fp16 + scaler | paged_adamw_8bit |
| smoke (CPU/MPS) | 1 | 2 | 512 | off | fp32 | adamw_torch |

Gradient checkpointing is **on** for `kaggle-t4`. It is not optional at 16GB.

The `kaggle-t4` batch and sequence-length values are **starting points, not
measurements**. Tune them after the first smoke run against the peak memory that
run actually reports. If `per_device` changes, change `grad_accum` by the inverse
factor so the effective batch stays 32.

`max_seq_length: 1024` is half the 2048 used on larger cards, so it will drop or
truncate more examples. Before accepting it, run the `loss-masking-verify`
procedure and report what percentage of examples exceed 1024 tokens. Truncating a
response is never acceptable; dropping the example and logging the count is.

## Reference profiles — not our hardware

These are kept for the scaling discussion in the FYP report. Do not select one
for a real run on Kaggle; none of this hardware is available to us.

| Profile | per_device | grad_accum | max_seq_len | packing | precision | optimizer |
|---|---|---|---|---|---|---|
| 24GB | 2 | 16 | 2048 | on | bf16 | paged_adamw_8bit |
| 32GB | 4 | 8 | 2048 | on | bf16 | paged_adamw_8bit |
| 48GB | 8 | 4 | 4096 | on | bf16 | paged_adamw_8bit |
| 80GB | 16 | 2 | 4096 | on | bf16 | paged_adamw_32bit |

Those rows assume bf16, which needs compute capability 8.0 or newer. The T4 is
7.5 and has no bf16 — see `qlora-loading` for the precision rule that follows
from that. Gradient checkpointing can be turned off at 48GB and above for roughly
20–30% more throughput if memory allows — measure, do not assume.

## When OOM happens

Work down this list in order, and change one thing at a time:

1. Lower `per_device` and raise `grad_accum` by the same factor (free — keeps
   effective batch size identical).
2. Confirm gradient checkpointing is actually enabled.
3. Lower `max_seq_length`, but first check what fraction of examples that drops
   using the `loss-masking-verify` procedure.
4. Turn off packing, which raises padding waste but lowers peak memory spikes.
5. Switch to a paged 8-bit optimizer if not already using one.

Only after all five: lower LoRA rank.

On Kaggle, an OOM three hours in costs real weekly budget. Get peak memory from
the smoke run first and leave headroom rather than launching at the edge.

## Always report

Every run must log peak allocated memory, peak reserved memory, and tokens/sec.
Without those numbers there is no basis for tuning, the `kaggle-run` budget check
cannot be computed, and the FYP report needs them anyway.
