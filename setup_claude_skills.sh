#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup_claude_skills.sh
#
# Creates the six project-level Claude Code skills for the Qwen2.5-Coder
# QLoRA fine-tuning repo. Run this from your repository root:
#
#     bash setup_claude_skills.sh
#
# Existing SKILL.md files are backed up to SKILL.md.bak before overwrite.
# ---------------------------------------------------------------------------

set -euo pipefail

ROOT="$(pwd)"
SKILLS_DIR="${ROOT}/.claude/skills"

echo "Installing Claude Code skills into: ${SKILLS_DIR}"
echo

write_skill() {
    # write_skill <skill-name>  ; body comes from stdin
    local name="$1"
    local dir="${SKILLS_DIR}/${name}"
    mkdir -p "${dir}"
    if [ -f "${dir}/SKILL.md" ]; then
        cp "${dir}/SKILL.md" "${dir}/SKILL.md.bak"
        echo "  ~ ${name}  (existing file backed up to SKILL.md.bak)"
    else
        echo "  + ${name}"
    fi
    cat > "${dir}/SKILL.md"
}

# ---------------------------------------------------------------------------
# 1. hf-api-currency
# ---------------------------------------------------------------------------
write_skill hf-api-currency << 'SKILLEOF'
---
name: hf-api-currency
description: >-
  Verify TRL, PEFT, Transformers and BitsAndBytes API signatures against the
  versions actually installed in this environment before writing or editing any
  training code. Use this skill whenever touching trainer.py, model.py,
  train.py, evaluate.py, merge_lora.py, or any file importing trl, peft,
  transformers, bitsandbytes, accelerate or datasets. Use it even when the code
  looks obviously correct, because these libraries deprecate arguments between
  minor releases and remembered signatures are frequently stale.
paths: src/**/*.py, train.py, evaluate.py, merge_lora.py, inference.py
---

# HuggingFace API currency

## Installed versions

```!
pip show transformers trl peft accelerate bitsandbytes datasets 2>/dev/null | grep -E "^(Name|Version)" | paste - - | sed 's/Name: //; s/Version: //'
```

## Standing rules

Never write TRL / PEFT / Transformers code from memory. These APIs move fast and
training data contains deprecated patterns that still *look* correct and fail at
runtime or, worse, silently no-op.

Before writing or editing code that constructs any of these objects, inspect the
real signature first:

```bash
python -c "import inspect, trl; print(inspect.signature(trl.SFTTrainer.__init__))"
python -c "import inspect, trl; print([f.name for f in __import__('dataclasses').fields(trl.SFTConfig)])"
python -c "import inspect, peft; print(inspect.signature(peft.LoraConfig.__init__))"
python -c "import inspect, transformers; print(inspect.signature(transformers.BitsAndBytesConfig.__init__))"
```

Write against what the inspection returned, not against what you expected.

## Known trap areas

Check these specifically, since they are the ones that have moved:

- Where the tokenizer/processor is passed to the trainer.
- Whether sequence length, packing and dataset-text-field settings belong on the
  trainer call or on the config object.
- Whether completion-only loss masking is a collator, a config flag, or both.
- Which optimizer string names are still accepted.
- Whether `evaluation_strategy` or `eval_strategy` is the current field name.

## Record what you find

Every deprecation or signature surprise discovered goes into
`references/known-migrations.md` next to this file, as a one-line entry:

    <date> | <library> <version> | old -> new | where it bit us

Read that file before starting, and append to it before finishing.
SKILLEOF

mkdir -p "${SKILLS_DIR}/hf-api-currency/references"
cat > "${SKILLS_DIR}/hf-api-currency/references/known-migrations.md" << 'SKILLEOF'
# Known API migrations

Append one line per surprise discovered. Format:

    <date> | <library> <version> | old -> new | where it bit us

## Entries

(empty — add entries as they are found)
SKILLEOF

# ---------------------------------------------------------------------------
# 2. prompt-schema
# ---------------------------------------------------------------------------
write_skill prompt-schema << 'SKILLEOF'
---
name: prompt-schema
description: >-
  Rules for the extensible prompt/output-field architecture of this C++ code
  review model. Use this skill whenever adding, renaming or removing an output
  field (comments, explanation, improved_code, complexity, issues,
  security_review, best_practices, refactoring, code_smells, confidence,
  roman_urdu_explanation), whenever editing prompt.py or the templates, and
  whenever a change is about to touch trainer.py in order to support a new
  dataset field. Use it even for small changes, because the whole point of the
  design is that field changes stay out of the trainer.
paths: src/prompt.py, src/dataset.py, src/config.py, templates/**
---

# Prompt and output schema

## The invariant

Adding a new output field must require changes to **only**:

1. the field registry / schema definition,
2. the prompt template,
3. tests.

If a change requires editing `trainer.py`, `model.py` or the training loop to
support a new output field, the design has been violated. Stop and refactor the
field back out into the registry instead.

## Structure

- Field definitions (name, human label, required/optional, render order) live in
  one registry in `src/prompt.py`.
- The instruction block is generated *from* the registry, not hardcoded, so a new
  field automatically appears in the "Generate:" list.
- The target/response block is likewise rendered from the registry, so a dataset
  example missing an optional field degrades gracefully instead of producing a
  malformed target.

## Two formats, one code path

Both formats must be supported and selected by config, never by editing code:

- **Chat template**: build a messages list and apply the tokenizer's Qwen chat
  template. This is the default for an `-Instruct` checkpoint.
- **Instruction template**: the plain `### Instruction / ### Code / ### Response`
  layout.

The two formats share the same registry and the same field renderer. Only the
outer wrapping differs.

## Boundaries

- The prompt module returns strings. It never tokenizes, never touches the model,
  never reads config files directly — config is passed in.
- The response section must end with the EOS token so generation terminates.
- Language tag (`cpp`) comes from the dataset record, not from a constant.

## After any change here

Run the prompt tests, and print one fully rendered example (prompt + target) to
stdout so a human can eyeball it. A silently malformed template is the most
expensive bug in this repo.
SKILLEOF

# ---------------------------------------------------------------------------
# 3. qlora-loading
# ---------------------------------------------------------------------------
write_skill qlora-loading << 'SKILLEOF'
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

## Order of operations

The sequence matters. Getting it wrong produces either a crash or, worse, a run
that trains nothing:

1. Build the quantization config (4-bit, NF4, double quantization on, compute
   dtype bf16 where supported else fp16).
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

Try flash attention, fall back cleanly. Never hard-require it — the model must
load on a machine without it, and on Apple Silicon during local development.
Wrap the import check in a try/except and log which implementation was selected.

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
SKILLEOF

# ---------------------------------------------------------------------------
# 4. loss-masking-verify
# ---------------------------------------------------------------------------
write_skill loss-masking-verify << 'SKILLEOF'
---
name: loss-masking-verify
description: >-
  Mandatory verification procedure for tokenization, label masking, packing and
  truncation. Use this skill after any change to dataset.py, prompt.py,
  tokenizer.py, the collator, max_seq_length, packing, or the train_on_inputs /
  ignore_prompt_loss setting. Use it before any real training run. Broken
  completion-only masking does not raise an error — the loss curve looks
  healthy and the model learns to echo prompts — so this check is not optional.
paths: src/dataset.py, src/tokenizer.py, src/prompt.py
---

# Verify loss masking

## Why this exists

Wrong label masking is the highest-cost silent failure in supervised fine-tuning.
Training proceeds, loss falls, checkpoints save, and the resulting model produces
garbage or parrots the instruction back. There is no exception and no warning.
The only defence is to decode a real batch and look at it.

## The procedure

Run this after any change to the data path, before launching a real run.

1. Build the dataset exactly as training would, using the real config.
2. Pull one batch through the real collator.
3. For that batch, print:
   - the decoded full sequence,
   - the decoded portion where `labels != -100`,
   - counts: total tokens, masked tokens, supervised tokens.
4. Assert, in code, not by eye:
   - the supervised span decodes to the response only,
   - no instruction or code text appears in the supervised span,
   - the supervised span is non-empty for every example in the batch,
   - the sequence ends with EOS,
   - padding positions are masked.

## Read the numbers, not the vibes

- If supervised tokens equal total tokens, masking is not applied at all.
- If supervised tokens are 0, the response marker did not match — usually a
  whitespace or template mismatch between the prompt module and the collator.
- If the supervised ratio is far below expectation, truncation is eating the
  response. Long C++ files plus a five-field target overflow easily. Check how
  many examples hit `max_seq_length` and report that number.

## Packing

When packing is enabled, additionally confirm that example boundaries are
respected and that attention does not cross documents. If the packing
implementation cannot guarantee this, prefer packing off and say so explicitly
rather than accepting cross-contamination.

## Truncation policy

Truncating the response is never acceptable — it teaches the model to stop
mid-output. If an example does not fit, drop it and log the count. Report the
percentage dropped so the max sequence length can be tuned deliberately.
SKILLEOF

# ---------------------------------------------------------------------------
# 5. vram-profiles
# ---------------------------------------------------------------------------
write_skill vram-profiles << 'SKILLEOF'
---
name: vram-profiles
description: >-
  Hardware-specific training configuration profiles for QLoRA fine-tuning of a
  1.5B model across 24GB, 32GB, 48GB and 80GB single-GPU setups, plus CPU/MPS
  smoke-test settings. Use this skill whenever choosing or changing batch size,
  gradient accumulation, max sequence length, packing, optimizer or precision
  settings, whenever writing a config file, and whenever diagnosing an
  out-of-memory error. Do not guess these values from memory.
paths: configs/**, src/config.py
---

# VRAM profiles

## How to use this

Pick the profile matching the GPU, then write it into a config file under
`configs/`. Never hardcode these numbers anywhere else. Effective batch size is
`per_device_batch * grad_accum`; keep it constant across profiles so results stay
comparable, and change only how it is split.

Target effective batch size for this project: **32**.

## Profiles

| Profile | per_device | grad_accum | max_seq_len | packing | precision | optimizer |
|---|---|---|---|---|---|---|
| smoke (CPU/MPS) | 1 | 2 | 512 | off | fp32 | adamw_torch |
| 24GB | 2 | 16 | 2048 | on | bf16 | paged_adamw_8bit |
| 32GB | 4 | 8 | 2048 | on | bf16 | paged_adamw_8bit |
| 48GB | 8 | 4 | 4096 | on | bf16 | paged_adamw_8bit |
| 80GB | 16 | 2 | 4096 | on | bf16 | paged_adamw_32bit |

Use bf16 only where the GPU supports it; fall back to fp16 with the gradient
scaler otherwise. Turing-era and older cards need fp16.

Gradient checkpointing stays **on** for 24GB and 32GB. It can be turned off at
48GB and above for roughly 20–30% more throughput if memory allows — measure,
do not assume.

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

## Always report

Every run must log peak allocated memory, peak reserved memory, and tokens/sec.
Without those numbers there is no basis for tuning, and the FYP report needs
them anyway.
SKILLEOF

# ---------------------------------------------------------------------------
# 6. smoke-run
# ---------------------------------------------------------------------------
write_skill smoke-run << 'SKILLEOF'
---
name: smoke-run
description: >-
  Short pre-flight training run on a tiny subset to prove the pipeline works
  before committing GPU hours. Invoke manually with /smoke-run before any real
  training run and after any change to the data, model or trainer modules.
disable-model-invocation: true
---

# Smoke run

A smoke run is not a training run. Its only job is to fail fast and cheaply.

## Procedure

1. Confirm the data path first by running the `loss-masking-verify` procedure.
   Do not skip this — a smoke run with broken masking passes happily.
2. Build a config from the current one with these overrides:
   - 64 training examples, 16 validation examples
   - `max_steps = 10`
   - `logging_steps = 1`
   - `eval_steps = 5`
   - `save_steps = 5`, `save_total_limit = 1`
   - output directory under `outputs/smoke/` so it never collides with real runs
3. Launch it in the foreground and watch the output.

## Pass criteria

All of these must hold, checked explicitly:

- The run reaches step 10 without exception.
- Loss at step 10 is lower than at step 1. Flat loss means the adapter is not
  attached or the labels are all masked.
- Loss is not `nan`. `nan` on the first step usually means fp16 without the
  scaler, or a bad learning rate.
- Trainable parameter count printed at startup is greater than zero.
- Evaluation ran at step 5 and produced a finite validation loss.
- A checkpoint directory exists and contains adapter weights.
- Peak memory and tokens/sec were logged.

## After it passes

Generate one sample from the step-10 checkpoint on a held-out C++ snippet. The
output will be poor — that is expected after 10 steps. What matters is that it is
*shaped* correctly: the expected sections appear, and generation stops instead of
running on forever. Wrong shape means a template or EOS problem, not a training
problem, and no amount of further training will fix it.

Delete `outputs/smoke/` afterwards.

## After it fails

Report which pass criterion failed and the relevant log lines. Do not start the
real run "to see if it works at scale". It will not.
SKILLEOF

echo
echo "Done. Installed skills:"
find "${SKILLS_DIR}" -name SKILL.md | sed "s|${SKILLS_DIR}/|  /|; s|/SKILL.md||"
echo
echo "Next steps:"
echo "  1. Restart Claude Code so it starts watching the new directory."
echo "  2. Type / to confirm the skills appear, or ask 'what skills are available?'"
echo "  3. git add .claude/skills && git commit -m 'Add project Claude Code skills'"
