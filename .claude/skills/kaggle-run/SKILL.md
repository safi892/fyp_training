---
name: kaggle-run
description: >-
  End-to-end procedure for launching and resuming a training run inside a Kaggle
  free-tier notebook: dependency bootstrap and kernel restart, install
  verification, model access with and without internet, the GPU-hour budget
  check, launch, and resume verification. Invoke manually with /kaggle-run
  before starting or continuing any training session on Kaggle.
disable-model-invocation: true
---

# Kaggle run

Kaggle sessions end at 9–12 hours and the weekly allowance is roughly 30 GPU
hours. Every step below exists because skipping it wastes a share of that.

## 1. Bootstrap: install, then RESTART the kernel

Kaggle preinstalls its own torch, transformers and accelerate. They are older
than what this project pins, and **an already-imported preinstalled version
shadows the one you just installed** — `pip install -U` inside a running kernel
does not change what is already in `sys.modules`, and partially-upgraded
dependency trees fail in ways that look like code bugs.

The order is not negotiable:

1. In the first cell, `pip install -U` the pinned versions.
2. **Restart the kernel.** Not "run all again" — an actual restart.
3. Only then import anything.

Do not import transformers, torch, trl or peft in the install cell, not even
indirectly, and not to "check the version".

## 2. Verify the install actually took effect

After the restart, before anything else, print what is really loaded:

```python
import torch, transformers, trl, peft, accelerate, bitsandbytes
for m in (torch, transformers, trl, peft, accelerate, bitsandbytes):
    print(f"{m.__name__:>14} {m.__version__:>12}  {m.__file__}")
print("cuda:", torch.cuda.is_available(), torch.cuda.get_device_name(0))
```

Check the **paths**, not only the versions. A path under the Kaggle system
site-packages instead of the user site-packages means the restart did not take
and the old version is still winning. Stop and restart again.

Cross-check the resulting signatures with the `hf-api-currency` skill before
writing or editing any training code against them.

## 3. Model access

Pulling `Qwen/Qwen2.5-Coder-1.5B-Instruct` from the Hub requires the notebook's
**Internet setting to be enabled** (Settings → Internet on). Without it the
download fails at load time, after the session has already started spending
budget.

Offline fallback, and the more reliable option for repeat runs: upload the model
once as a **Kaggle Dataset**, mount it, and point `model_name_or_path` at the
mounted path. This also removes the download from every subsequent session's
startup time.

Either way, the download must land in `/tmp` — see `kaggle-storage` for the cache
environment variables and why they must be set before the first import.

## 4. Pre-flight budget check

Do not launch a run that cannot finish. Estimate from the throughput the smoke
run actually measured, never from a guess:

```
steps_per_sec = measured in the smoke run (the throughput callback logs it)
total_steps   = ceil(train_rows / (per_device * grad_accum)) * num_train_epochs
est_hours     = (total_steps / steps_per_sec) / 3600 * 1.15
```

The 1.15 covers evaluation and checkpoint saves. It is an allowance, not a
measurement — refine it once a real run has produced numbers.

**Refuse to launch if `est_hours > 8.`** The session ceiling is 9–12 hours, so
8 leaves margin for startup, evaluation and the final save. Exceeding it means
the run dies mid-training and the hours are spent either way.

If the estimate is over 8 hours, in preference order:

1. Reduce `num_train_epochs`.
2. Reduce `max_seq_length` — check the drop rate first with `loss-masking-verify`.
3. Split the run deliberately across sessions using the resume procedure below.

Report the estimate before launching, so the number is on the record.

## 5. Launch

Prerequisites, all of which must already have passed:

- `kaggle-storage` preflight (disk floor, caches redirected to `/tmp`)
- `loss-masking-verify`
- `smoke-run`
- the budget check above

Then launch in the foreground and watch the first 20 steps. Confirm loss is
finite, memory is below the ceiling with headroom, and tokens/sec matches what
the smoke run predicted. A throughput figure well under the estimate means the
budget check is now wrong — recompute it rather than hoping.

## 6. Resume

Re-running training continues from the newest usable checkpoint in the persistent
output directory. Checkpoints must be under `/kaggle/working` (see
`kaggle-storage`); anything in `/tmp` is gone with the session and cannot be
resumed from.

If the previous session's checkpoints were saved into a Kaggle version output,
mount that output as a dataset input and copy the `checkpoint-*` directories into
the working output directory before launching.

## 7. Verify the resume actually worked

A resume that silently restarts at step 0 wastes the entire previous session, and
it looks like a normal run in the log. Check all of these explicitly:

- A log line names the checkpoint being resumed from.
- **The first logged step is the checkpoint's step, not 1.** Seeing `1/6072`
  after resuming from step 750 means the resume did not happen.
- **Optimizer state was restored, not created fresh.** A fresh optimizer means
  the moment estimates were lost even if the step counter survived.
- The learning rate at the resume point matches the schedule position. A rate
  back at the warm-up peak means the scheduler restarted.
- Training loss continues near where the previous session stopped, rather than
  jumping back toward its initial value.

If the step counter advanced but the optimizer did not restore, the run is still
usable — it costs the moment estimates, not the training. If the step counter
restarted, stop immediately and fix the resume before spending more hours.

## 8. Before the session ends

Save the version so `/kaggle/working` persists. Confirm the final adapter, the
best checkpoint and the logs are all present, and that the output respects the
~500 file cap.
