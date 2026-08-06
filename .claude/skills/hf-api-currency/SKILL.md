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

On Kaggle this is not theoretical: the notebook image preinstalls older torch,
transformers and accelerate that shadow the pinned versions until the kernel is
restarted, so the signature you get at runtime may not be the one you installed.
Inspect after the restart — see `kaggle-run` step 2.

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
