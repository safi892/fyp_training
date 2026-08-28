---
name: cpu-only-local-machine
description: This local machine has no GPU — always run and test on CPU here; GPU training happens on Kaggle
metadata:
  type: feedback
---

Always run on CPU on **the Linux laptop** (`usama-GL502VT`). Stated
directly on 2026-08-24. This file is committed and therefore travels: on a
machine with a working GPU it does not apply, so check `nvidia-smi` rather
than assuming. The Mac in this project is a 2019 Intel i9 - also no CUDA,
but faster on CPU (DDR4-2666 against 2133).

Verified at the time: `nvidia-smi` fails with "couldn't communicate with the
NVIDIA driver", and `.venv` has no `torch` at all — the `gpu` extra
(`torch`, `bitsandbytes`, `peft`, `trl`, `accelerate`) is not installed.

**Why:** there is no CUDA device here, so anything assuming a GPU fails rather
than falling back. The GPU work for this project runs on Kaggle free-tier
T4s, not locally — see the `kaggle-run`, `kaggle-storage` and `vram-profiles`
skills in `.claude/skills/`.

**How to apply:**
- Local work = tests, dataset builders, scoring/report scripts, prompt
  rendering, static analysis. `uv sync --extra dev` is enough for those.
- Do not propose `nvidia-smi`, `accelerate launch`, QLoRA loading, or any
  4-bit/bitsandbytes path as something to run here.
- Do not install the `gpu` extra locally to "check something" — inspect the
  Kaggle-side config or the skill files instead.
- If a script needs a device, pass CPU explicitly rather than relying on an
  `auto` default that assumes CUDA.
- Real training runs and adapter evaluation are Kaggle-side; treat local runs
  as verification of the code path, not of model quality.
