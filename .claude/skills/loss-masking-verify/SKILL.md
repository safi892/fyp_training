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
