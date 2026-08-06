## Qwen2.5 C++ Code Review Fine-Tuning

Production-oriented QLoRA fine-tuning pipeline for
`Qwen/Qwen2.5-Coder-1.5B-Instruct`. The model learns to turn raw C++ source
code into structured review output: comments, explanation, improved code, and
complexity analysis.

The trainer is field-agnostic. To add future outputs such as `issues`,
`security_review`, `best_practices`, or `roman_urdu_explanation`, add those
field names to `configs/train_qlora.yaml` under `data.output_fields` and make
sure the dataset rows contain matching keys.

## Repository Layout

```text
configs/
  accelerate_single_gpu.yaml
  accelerate_multi_gpu.yaml
  train_qlora.yaml
cleaned/
  *.jsonl
  merged_cleaned.jsonl
src/qwen_cpp_review/
  config.py
  dataset.py
  prompt.py
  tokenizer.py
  model.py
  trainer.py
  callbacks.py
  checkpoint.py
  metrics.py
  logging_utils.py
  seed.py
  utils.py
  cli.py
train.py
evaluate.py
inference.py
merge_lora.py
export_onnx.py
kaggle_training.ipynb
tests/
```

## Local Setup With uv

```bash
python -m pip install --upgrade uv
uv sync --extra dev
uv run --extra dev pytest
```

For GPU training, use a Linux CUDA environment. `bitsandbytes` is not suitable
for native Apple Silicon GPU training.

## Kaggle Setup

Create a Kaggle notebook with GPU enabled, upload this repository or attach it
as a dataset, then run:

```bash
cd /kaggle/working/fyp8th_clean
bash scripts/kaggle_setup.sh
```

Or open `kaggle_training.ipynb` directly on Kaggle and run the cells from top
to bottom.

If Kaggle already has compatible CUDA builds of `torch`, you can avoid changing
the system package set by installing the project dependencies manually:

```bash
python -m pip install --upgrade uv
uv pip install --system -r requirements.txt
uv pip install --system -e .
```

## Dataset Merge

The four cleaned JSONL shards are merged into one file:

```bash
uv run python scripts/merge_datasets.py
```

Current merged output:

```text
cleaned/merged_cleaned.jsonl
```

The default training config already uses this merged file.

## Variable Name Robustness

To make the model handle weak names like `a`, `b`, `x`, `f`, and stronger names
like `count`, `result`, or `is_valid`, generate variable-renaming augmentation:

```bash
uv run python scripts/augment_identifiers.py \
  --input cleaned/merged_cleaned.jsonl \
  --output cleaned/augmented_merged_cleaned.jsonl
```

To protect Kaggle's limited `/kaggle/working` disk, the notebook does not write
the full augmented dataset by default. It enables in-pipeline augmentation and
stores Hugging Face dataset cache under `/kaggle/temp/hf-datasets`.

## Training

Single GPU:

```bash
uv run accelerate launch --config_file configs/accelerate_single_gpu.yaml train.py \
  --config configs/train_qlora.yaml
```

Multi-GPU on one Kaggle/VM machine:

```bash
NUM_PROCESSES=2 bash scripts/train_multi_gpu.sh
```

The same `train.py` works for one or many GPUs. Launching with Accelerate sets
the distributed environment; model loading maps each quantized worker to its
local GPU when `WORLD_SIZE > 1`.

Outputs are written to:

```text
outputs/qwen2.5-coder-1.5b-cpp-review-qlora/
```

The final adapter is saved under `final_adapter/`.

Training saves:

- `best_adapter/` and `best_adapter.pth`
- `last_adapter/` and `last_adapter.pth`
- `final_adapter/` and `final_adapter.pth`

`best_adapter` comes from `trainer.state.best_model_checkpoint`.
`last_adapter` comes from the newest checkpoint. `final_adapter` is the model
state held by the trainer after training finishes.

## Resuming

Re-running `train.py` continues from the newest usable checkpoint in
`output_dir`. Nothing needs to be set: `training.resume_mode: auto` picks the
strongest continuation the checkpoint supports.

| Mode | Restores | Use when |
| --- | --- | --- |
| `exact` | adapter, optimizer moments, LR schedule, step, epoch, RNG | default; a true continuation |
| `state` | adapter, LR schedule, step, epoch | the saved optimizer state is unusable |
| `adapter` | adapter weights only | only adapter files survived |
| `scratch` | nothing | deliberately restarting |

Preview the decision before spending GPU time — this reads the checkpoints and
writes nothing:

```bash
uv run qwen-review-resume-status --config configs/train_qlora.yaml
```

Every run prints a `RESUME MODE:` banner naming the starting step and whether
the optimizer, LR schedule and step counter were restored.

Overrides:

```bash
uv run python train.py --resume-from outputs/.../checkpoint-750  # specific checkpoint
uv run python train.py --resume-mode exact                       # fail if not exact
uv run python train.py --fresh                                   # archive and restart at 0
```

`--fresh` moves the existing run to `output_dir/archive/run-<timestamp>/`
rather than deleting it.

### Why exact resume can fail, and what happens instead

The optimizer state in a checkpoint can only be read back by the same
optimizer. Changing `training.optim` between runs — for example from
`paged_adamw_8bit` to `adamw_torch` — leaves a `optimizer.pt` full of
bitsandbytes 8-bit moment tensors that a `torch.optim.AdamW` cannot use; the
load appears to succeed and then dies on the first step. **Keep `optim` fixed
for the lifetime of a run.**

When a mismatch is detected the run does not crash and does not silently reset.
It degrades to `state`: the adapter, the step counter, the epoch, the data
position and the LR schedule position are all restored, and only the Adam
moment estimates start fresh — a few dozen steps of warm-up rather than the
hundreds of steps a full restart throws away. The unusable file is renamed to
`optimizer.pt.unusable`, so an exact resume is still possible later by
restoring the original `optim`.

Also handled automatically:

- A checkpoint directory left half-written by a killed session is skipped in
  favour of the previous complete one, instead of raising
  `Can't find a valid checkpoint at ...`.
- A checkpoint mounted read-only (a Kaggle input dataset) is staged into
  `output_dir` so the resumed run can keep saving.
- A `best_model_checkpoint` path from a dead session is remapped if the
  directory exists locally, and otherwise cleared so `load_best_model_at_end`
  tracks a reachable checkpoint.
- A training set that changed size since the checkpoint is reported, because
  the step counter no longer refers to the same point in the schedule.

Each checkpoint carries a `resume_manifest.json` recording the optimizer, the
step accounting, the dataset fingerprint and library versions, which is what
makes these checks possible before a resume is attempted.

## Evaluation

Evaluate during training every `training.eval_steps`. Standalone evaluation:

```bash
uv run python evaluate.py --config configs/train_qlora.yaml \
  --adapter outputs/qwen2.5-coder-1.5b-cpp-review-qlora/final_adapter
```

The script reports validation loss and perplexity.

## Inference

With a LoRA adapter:

```bash
uv run python inference.py --config configs/train_qlora.yaml \
  --adapter outputs/qwen2.5-coder-1.5b-cpp-review-qlora/final_adapter \
  --code-file sample.cpp
```

Streaming:

```bash
uv run python inference.py --config configs/train_qlora.yaml \
  --adapter outputs/qwen2.5-coder-1.5b-cpp-review-qlora/final_adapter \
  --code-file sample.cpp --stream
```

Batch JSONL inference expects a `code` field in each row:

```bash
uv run python inference.py --config configs/train_qlora.yaml \
  --adapter outputs/qwen2.5-coder-1.5b-cpp-review-qlora/final_adapter \
  --batch-jsonl cleaned/results_0_cleaned.jsonl
```

## Test a Trained Model

Smoke-test the best adapter on built-in easy, medium, and hard C++ examples:

```bash
uv run python scripts/test_model.py
```

The script has its test configuration embedded and also tests renamed-variable
versions by default.

On Kaggle:

```bash
UV_PROJECT_ENVIRONMENT=/kaggle/temp/project-venv uv run python scripts/test_model.py
```

## Merge LoRA Adapter

```bash
uv run python merge_lora.py \
  --base-model Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --adapter outputs/qwen2.5-coder-1.5b-cpp-review-qlora/final_adapter \
  --output-dir outputs/qwen2.5-coder-1.5b-cpp-review-merged
```

Merged models are saved with `safe_serialization=True`.

## Export ONNX

Export ONNX from the merged model:

```bash
uv run python export_onnx.py \
  --model outputs/qwen2.5-coder-1.5b-cpp-review-merged \
  --output outputs/qwen2.5-coder-1.5b-cpp-review.onnx
```

Exporting directly from an unmerged 4-bit LoRA adapter is not recommended. The
notebook merges the best adapter first, then exports the merged model.

## Configuration

All model, data, LoRA, generation, and training hyperparameters live in
`configs/train_qlora.yaml`.

Important defaults:

- QLoRA with 4-bit NF4 quantization and double quantization.
- LoRA on Qwen attention and MLP projection modules.
- TRL `SFTTrainer` with `SFTConfig`.
- `paged_adamw_8bit`, cosine scheduler, gradient clipping, warmup, and
  gradient checkpointing.
- Non-reentrant gradient checkpointing and
  `ddp_find_unused_parameters: false` for stable multi-GPU DDP training.
- TensorBoard logging, best-model loading, early stopping, automatic checkpoint
  discovery, and final adapter save.
- Chat-template prompt formatting by default.

## VRAM Guidance

Approximate starting points for `Qwen2.5-Coder-1.5B-Instruct` QLoRA:

| GPU VRAM | max_seq_length | batch size | grad accumulation | packing |
| --- | ---: | ---: | ---: | --- |
| 16 GB | 2048 | 1 | 8 | true |
| 24 GB | 4096 | 1 | 8 | true |
| 32 GB | 4096 | 2 | 8 | true |
| 48 GB | 8192 | 1-2 | 8 | true |
| 80 GB | 8192+ | 2-4 | 8 | true |

If training runs out of memory, reduce `data.max_seq_length` first, then
`per_device_train_batch_size`. Keep `packing: false` on Kaggle T4 unless you
install and enable a supported flash-attention implementation.

## Common Issues

- `bitsandbytes` CUDA errors: use a Kaggle/Colab/Linux CUDA GPU runtime.
- Flash attention import failures: keep `model.flash_attention: false`; the
  default `sdpa` attention is portable.
- Slow preprocessing: increase `data.preprocessing_num_proc` when CPU cores are
  available.
- Poor output schema: improve prompt wording or add the field to
  `data.output_fields`; trainer code does not need to change.
