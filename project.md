

# ROLE

You are a Senior Machine Learning Engineer and LLM Infrastructure Engineer specializing in

* HuggingFace Transformers
* TRL
* PEFT
* QLoRA
* BitsAndBytes
* Accelerate
* PyTorch
* Distributed Training
* Production ML systems

Your task is to build a COMPLETE production-ready repository for fine-tuning **Qwen2.5-Coder-1.5B-Instruct**.

This repository will be used in a Final Year Project (FYP).

The repository must follow the latest HuggingFace recommendations.

Do NOT generate a toy example.

Do NOT simplify anything.

The goal is to build something maintainable, modular, extensible, and suitable for future research.

---

# PROJECT DESCRIPTION

This project is an AI-powered C++ Code Review Assistant.

The model receives raw C++ source code.

The model generates structured documentation and review output.

Each dataset example contains fields similar to:

```
{
    "code": "...",
    "language":"cpp",

    "comments":"...",

    "explanation":"...",

    "improved_code":"...",

    "complexity_analysis":
    {
        "time":"...",
        "space":"..."
    }
}
```

Future versions of the dataset may also include

```
issues
security_review
best_practices
refactoring
code_smells
confidence
roman_urdu_explanation
```

Design the training pipeline so adding new output fields later requires only modifying prompt templates, not changing the trainer.

---

# MODEL

Use

Qwen/Qwen2.5-Coder-1.5B-Instruct

Use

QLoRA

4-bit NF4 quantization

PEFT

BitsAndBytes

Latest Transformers

Latest TRL

Latest Accelerate

Latest PEFT

No deprecated APIs.

---

# OBJECTIVES

The trained model must learn to generate

1. Line-by-line comments

2. Human-readable explanation

3. Improved code

4. Time complexity

5. Space complexity

6. (Future) Issues

7. (Future) Security review

8. (Future) Best practices

The architecture should support future tasks without changing the training pipeline.

---

# TRAINING STYLE

Implement supervised instruction tuning.

Prompt format should be configurable.

Support

Chat template

or

Instruction template.

Example:

```
### Instruction

Analyze the following C++ code.

Generate:

- Line-by-line comments
- Explanation
- Improved code
- Time complexity
- Space complexity

### Code

...

### Response
```

Prompt formatting must be isolated inside a dedicated module.

---

# REPOSITORY STRUCTURE

Use a clean modular architecture.

Example

```
project/

configs/

train.py

inference.py

merge_lora.py

evaluate.py

requirements.txt

README.md

src/

config.py

dataset.py

prompt.py

tokenizer.py

model.py

trainer.py

metrics.py

callbacks.py

utils.py

logging_utils.py

checkpoint.py

seed.py

cli.py

tests/

scripts/
```

Do not put everything into one file.

---

# CONFIGURATION

All hyperparameters must live inside config classes.

Nothing should be hardcoded.

Support

learning_rate

epochs

batch_size

gradient_accumulation

max_seq_length

packing

scheduler

optimizer

weight_decay

warmup_ratio

logging_steps

eval_steps

save_steps

save_total_limit

seed

flash_attention

gradient_checkpointing

bf16

fp16

max_grad_norm

evaluation_strategy

save_strategy

output_dir

resume_from_checkpoint

LoRA parameters

r

alpha

dropout

target_modules

bias

task_type

Modules should use dataclasses or Pydantic.

---

# DATASET PIPELINE

Implement

JSON

JSONL

Arrow

datasets.load_dataset

Support

train

validation

test

splits.

Implement

parallel preprocessing

dataset caching

packing

dynamic padding

efficient tokenization

truncation

mask prompt tokens if desired

Support

max_seq_length

packing=True

---

# TOKENIZATION

Use

AutoTokenizer

Set

pad_token

EOS token

Qwen chat template when appropriate.

Support configurable

ignore_prompt_loss

or

train_on_inputs

---

# MODEL LOADING

Implement

QLoRA

BitsAndBytesConfig

NF4

double quantization

Flash Attention if available

Gradient Checkpointing

prepare_model_for_kbit_training()

get_peft_model()

Print

Trainable parameters

Frozen parameters

Total parameters

---

# TRAINING

Use

TRL SFTTrainer

if appropriate.

Otherwise justify using Trainer.

Implement

Gradient accumulation

Gradient checkpointing

Mixed precision

BF16 if supported

otherwise FP16

Gradient clipping

Cosine scheduler

Warmup

Weight decay

Paged AdamW

TensorBoard

Optional WandB

Automatic checkpoints

Resume training

Save adapter

Save tokenizer

Save config

Save best model

Early stopping callback

---

# EVALUATION

Evaluate every N steps.

Compute

Validation loss

Perplexity

Save best checkpoint.

Implement evaluation script.

---

# LOGGING

Use Python logging.

Rich console logging.

TensorBoard

CSV logs

Optional WandB.

Print

learning rate

loss

grad norm

tokens/sec

GPU memory

epoch

global step

ETA

---

# CHECKPOINTING

Support

resume automatically

resume manually

save best

save latest

save final

merge adapter after training.

---

# INFERENCE

Create inference.py

Support

LoRA adapter

Merged model

Streaming generation

Batch generation

temperature

top_p

top_k

max_new_tokens

repetition penalty

CLI arguments.

---

# MERGING

Create merge_lora.py

Merge adapter

Save merged model

Save tokenizer

Support

safe_serialization=True

---

# PERFORMANCE

Optimize for

Single GPU

24GB

32GB

48GB

80GB

VRAM

Memory efficiency is critical.

Use latest recommendations for

QLoRA.

---

# CODE QUALITY

Use

Python typing

Docstrings

Logging

Comments

Error handling

Dependency injection where appropriate

Reusable modules

PEP8

No duplicated logic.

---

# TESTING

Add unit tests for

prompt formatting

dataset preprocessing

configuration loading

tokenization

---

# DOCUMENTATION

Generate

README.md

Explain

installation

training

evaluation

resume

merge

inference

expected VRAM

performance tuning

common issues

---

# REQUIREMENTS

Generate

requirements.txt

with pinned versions that are mutually compatible.

---

# FINAL OUTPUT

Produce the COMPLETE repository.

Do not omit files.

Do not leave TODOs.

Do not use placeholder code.

Everything should be runnable.

Explain major architectural decisions.

Follow the latest HuggingFace recommendations for

Qwen2.5

TRL

PEFT

Accelerate

QLoRA

BitsAndBytes.


