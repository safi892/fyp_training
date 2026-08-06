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
