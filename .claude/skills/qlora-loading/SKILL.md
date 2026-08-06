---
name: qlora-loading
description: >-
  Correct QLoRA model-loading configuration for Qwen2.5-Coder-1.5B-Instruct:
  4-bit NF4 quantization, double quantization, compute dtype, k-bit training
  preparation, gradient checkpointing, attention implementation selection, and
  LoRA target module names. Use this skill whenever editing model.py, whenever
  constructing BitsAndBytesConfig or LoraConfig, whenever adjusting quantization
  or adapter settings, and whenever a run reports unexpected memory use or
  reports zero trainable parameters.
paths: src/model.py, src/config.py, merge_lora.py
---

# QLoRA loading for Qwen2.5-Coder

## Precision on the T4 — not negotiable

Our hardware is the Tesla T4, compute capability 7.5. bf16 requires compute
capability 8.0 or newer, so **there is no bf16 on this GPU**. That forces two
settings, and they must agree with each other:

- `fp16=True` with the gradient scaler, `bf16=False`.
- `bnb_4bit_compute_dtype=torch.float16`.

A quantization compute dtype of `bfloat16` underneath fp16 autocast is a known
cause of **`nan` loss on step 1**. The autocast dtype and the compute dtype are
not independent knobs; a mismatch does not raise, it produces `nan`.

Derive both from a single capability check so they cannot drift apart:

```python
supports_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
compute_dtype = torch.bfloat16 if supports_bf16 else torch.float16
# bf16=supports_bf16, fp16=not supports_bf16, bnb_4bit_compute_dtype=compute_dtype
```

Log the selected dtype at startup. If a run reports `nan` on the first step,
check this before anything else — see the `smoke-run` pass criteria.

## Order of operations

The sequence matters. Getting it wrong produces either a crash or, worse, a run
that trains nothing:

1. Build the quantization config (4-bit, NF4, double quantization on, compute
   dtype from the check above — float16 on our T4).
2. Load the base model with that quantization config and the chosen attention
   implementation.
3. Call the k-bit training preparation helper.
4. Enable gradient checkpointing **with non-reentrant mode**, and make sure input
   gradients are enabled — otherwise checkpointing silently breaks the backward
   pass through the frozen base.
5. Build the LoRA config and wrap the model.
6. Print the parameter report.

Steps 3 and 4 must come before step 5. Confirm the exact helper names and
argument names with the `hf-api-currency` skill before writing this.

## Attention implementation

FlashAttention-2 requires Ampere or newer (compute capability 8.0+). The T4 is
7.5, so **on our hardware the implementation is `sdpa`**, and that is the correct
outcome rather than a degraded one.

Try flash attention, fall back cleanly. Never hard-require it — the model must
load on a machine without it, and on Apple Silicon during local development.
Wrap the import check in a try/except.

The fallback **must log which implementation was selected**, at INFO, every run.
A silent fallback is the problem: it turns a large throughput difference into an
invisible one, and the tokens/sec figure in the FYP report becomes unattributable.
Logging "attention implementation: sdpa (flash_attention_2 requires CC>=8.0,
device is 7.5)" costs nothing and answers the question permanently.

## LoRA target modules

Qwen2.5 uses standard Llama-style projection names. Target the attention
projections plus the MLP projections. Do not guess: enumerate the actual module
names once and confirm against the loaded model:

```bash
python -c "
import re
from transformers import AutoConfig, AutoModelForCausalLM
m = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-Coder-1.5B-Instruct', torch_dtype='auto')
names = {n.split('.')[-1] for n, _ in m.named_modules() if isinstance(_, __import__('torch').nn.Linear)}
print(sorted(names))
"
```

Target modules must be a config value, never a literal inside `model.py`.

## Mandatory parameter report

After wrapping, always log:

- trainable parameters (absolute)
- total parameters (absolute)
- trainable percentage
- frozen parameters

If trainable is 0, or the percentage is above roughly 5% for a rank in the
normal 8–64 range, something is wrong — stop and diagnose rather than starting
the run.

## Merging

The merged model must be dequantized before merging; you cannot merge an adapter
into a 4-bit base and get a usable fp16 checkpoint. Load the base in bf16/fp16
without the quantization config, attach the adapter, merge, then save with safe
serialization along with the tokenizer.
