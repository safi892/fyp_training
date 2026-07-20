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

The final adapter is saved under `final_adapter/`. Checkpoints are resumed
automatically from the latest `checkpoint-*` directory unless
`training.resume_from_checkpoint` is set.

Training saves:

- `best_adapter/` and `best_adapter.pth`
- `last_adapter/` and `last_adapter.pth`
- `final_adapter/` and `final_adapter.pth`

`best_adapter` comes from `trainer.state.best_model_checkpoint`.
`last_adapter` comes from the newest checkpoint. `final_adapter` is the model
state held by the trainer after training finishes.

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
