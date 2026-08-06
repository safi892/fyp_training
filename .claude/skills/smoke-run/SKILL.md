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
   The `kaggle-storage` preflight check must also pass before the smoke run
   starts; a smoke run that dies on disk proves nothing about the pipeline.
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
