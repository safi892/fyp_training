---
name: kaggle-storage
description: >-
  Disk layout, cache redirection and checkpoint retention policy for training
  inside a Kaggle notebook, where /kaggle/working is a hard 20GB persistent
  limit and /tmp is ~60GB of ephemeral scratch. Use this skill whenever setting
  output_dir, cache_dir, save_total_limit, save_steps or load_best_model_at_end,
  whenever adding a save callback, whenever choosing where a model or dataset
  cache is written, and whenever a run reports "no space left on device". Use it
  before every real run, not only after a failure.
paths: src/config.py, src/checkpoint.py, configs/**
---

# Kaggle storage

## Why every rule here is mandatory

A run that dies at hour 7 with "no space left on device" costs roughly a quarter
of the weekly GPU budget and produces nothing. Disk exhaustion is the cheapest
failure to prevent and one of the most expensive to hit. None of the rules below
are optional or "nice to have".

## Verified storage facts

| Path | Size | Lifetime |
|---|---|---|
| `/kaggle/working` | **20GB** | persistent — survives into the saved version output |
| `/tmp` | **~60GB** | ephemeral — wiped when the session ends |

The output directory also has a **~500 file cap**.

These numbers are verified. Plan against them directly, do not re-derive them.

## Where things go

The governing rule: **anything reproducible from a rerun belongs in `/tmp`.**
Only artifacts you need after the session ends belong in `/kaggle/working`.

| Content | Location |
|---|---|
| Checkpoints | `/kaggle/working/checkpoints/` |
| Final adapter, merged model, logs to keep | `/kaggle/working/` |
| HF hub cache (model downloads) | `/tmp/hf_cache` |
| HF datasets cache (arrow files) | `/tmp/hf_datasets` |
| Tokenized / packed dataset cache | `/tmp` |

### Set the cache environment BEFORE the first transformers import

This is the single biggest cause of unexpected 20GB exhaustion. If these are set
late, the model download and the dataset arrow cache have already landed on the
persistent disk, and the limit is gone before training starts.

Put this in the **first cell**, above every import:

```python
import os
os.environ["HF_HOME"] = "/tmp/hf_cache"
os.environ["HF_DATASETS_CACHE"] = "/tmp/hf_datasets"
# only now import transformers / datasets / trl
```

Verify it took: after the first import, print `HF_HOME` and confirm nothing large
has appeared under `/kaggle/working` with `du -sh`.

## Checkpoint policy — exactly two checkpoints

Keep the **latest** and the **best**, and nothing else:

```python
save_total_limit=2,
load_best_model_at_end=True,
metric_for_best_model="eval_loss",
greater_is_better=False,
save_safetensors=True,
```

`load_best_model_at_end=True` protects the best checkpoint from rotation, so
`save_total_limit=2` yields last + best rather than the two most recent. Setting
the limit without the flag loses the best checkpoint the moment it ages out.

### A checkpoint is a directory, not a file

HF Trainer writes checkpoint **directories**, not `.pth` files. Each one holds:

- adapter weights
- **optimizer state** — the largest single part
- scheduler state
- RNG state

The optimizer state is what makes resume possible. **Never strip it to save
space.** A checkpoint without it cannot resume exactly; it can only restart the
step counter, which throws away every step already paid for in GPU hours.

### Adapter only during training

Never save the merged model during training. Merging happens **once, at the end,
after the run**, and the merged fp16 model is ~3GB — enough to end a run on its
own if written mid-training.

## Guards to implement in code

Document-only rules get skipped at hour 7. Implement all four.

**1. Startup preflight.** Refuse to begin training without headroom:

```python
import shutil, logging
LOGGER = logging.getLogger(__name__)
MIN_FREE_GB = 5.0

def assert_disk_headroom(path="/kaggle/working", floor_gb=MIN_FREE_GB):
    free_gb = shutil.disk_usage(path).free / 1024**3
    if free_gb < floor_gb:
        raise RuntimeError(
            f"{path} has {free_gb:.1f}GB free, below the {floor_gb}GB floor. "
            "Clear old checkpoints, or move the HF caches to /tmp, before training."
        )
    LOGGER.info("disk preflight: %s has %.1fGB free", path, free_gb)
```

Call it before the trainer is built, and make the floor a config value.

**2. Disk check in the save callback.** Log free space after every save and warn
loudly below the floor:

```python
class DiskGuardCallback(TrainerCallback):
    def __init__(self, path="/kaggle/working", floor_gb=MIN_FREE_GB):
        self.path, self.floor_gb, self._sized = path, floor_gb, False

    def on_save(self, args, state, control, **kwargs):
        checkpoint = Path(args.output_dir) / f"checkpoint-{state.global_step}"
        if not self._sized and checkpoint.is_dir():          # guard 3
            size_gb = sum(
                f.stat().st_size for f in checkpoint.rglob("*") if f.is_file()
            ) / 1024**3
            LOGGER.info(
                "checkpoint size %.2fGB; %d kept = %.2fGB total footprint",
                size_gb, args.save_total_limit, size_gb * args.save_total_limit,
            )
            self._sized = True
        free_gb = shutil.disk_usage(self.path).free / 1024**3
        if free_gb < self.floor_gb:
            LOGGER.error("LOW DISK: %.1fGB free on %s", free_gb, self.path)
        else:
            LOGGER.info("disk after save: %.1fGB free", free_gb)
```

**3. Size the checkpoint once, at the first save** (folded into the callback
above). The total footprint must be a number known at minute five, not a
discovery at hour seven.

**4. Respect the ~500 file cap.** A tokenizer plus adapter directory is a dozen
files, so two checkpoints stay well clear — but zip the adapter before the
session ends if the final output has accumulated many small files:

```python
shutil.make_archive("/kaggle/working/final_adapter", "zip", adapter_dir)
```

## Before launching

Confirm all of these, in this order:

1. `HF_HOME` and `HF_DATASETS_CACHE` point into `/tmp` and were set before any
   import.
2. `du -sh /kaggle/working` shows nothing unexpected.
3. The preflight check passes at the configured floor.
4. `save_total_limit=2` and `load_best_model_at_end=True` are both set.
