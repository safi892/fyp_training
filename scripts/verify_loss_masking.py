"""Prove that loss is computed on the target only.

Implements the `loss-masking-verify` procedure: build the dataset exactly as
training would, pull one batch through the real TRL collator, decode the
positions where ``labels != -100``, and assert in code that the supervised span
is the target and nothing else.

Wrong masking is silent. Loss falls, checkpoints save, and the model learns to
echo the instruction back. Run this before every real run.

    uv run python scripts/verify_loss_masking.py --config configs/train_qlora.yaml

A tiny randomly-initialised model stands in for the real one: the collator and
the dataset pipeline are what is under test, not the weights.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from datasets import DatasetDict
from transformers import AutoConfig, AutoModelForCausalLM
from trl import SFTTrainer

from qwen_cpp_review.config import AppConfig
from qwen_cpp_review.dataset import load_review_dataset, prepare_sft_dataset
from qwen_cpp_review.tokenizer import load_tokenizer
from qwen_cpp_review.trainer import build_sft_config, check_supervision_setup

IGNORE_INDEX = -100


def tiny_model(model_name: str, vocab_size: int):
    """A 1-layer model with the real vocabulary, so no 3 GB download is needed."""
    config = AutoConfig.from_pretrained(model_name)
    config.num_hidden_layers = 1
    config.hidden_size = 64
    config.intermediate_size = 128
    config.num_attention_heads = 4
    config.num_key_value_heads = 2
    config.vocab_size = vocab_size
    config.tie_word_embeddings = True
    # float32: the collator is what is under test, and MPS rejects bfloat16.
    config.torch_dtype = "float32"
    return AutoModelForCausalLM.from_config(config).to(torch.float32)


def take_sample(config: AppConfig, tokenizer, limit: int) -> DatasetDict:
    """Render `limit` real rows through the exact training pipeline."""
    raw = load_review_dataset(config.data)
    subset = raw["train"].select(range(min(limit, len(raw["train"]))))
    rendered = prepare_sft_dataset(DatasetDict({"train": subset}), config.data, tokenizer)
    check_supervision_setup(config, rendered["train"].column_names)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default="configs/train_qlora.yaml")
    parser.add_argument("--rows", type=int, default=8, help="Rows to render and check.")
    parser.add_argument("--show", type=int, default=1, help="Examples to print in full.")
    args = parser.parse_args()

    config = AppConfig.from_yaml(Path(args.config))
    tokenizer = load_tokenizer(config.model)
    rendered = take_sample(config, tokenizer, args.rows)
    print(f"columns: {rendered['train'].column_names}")
    print(f"train_on_inputs: {config.data.train_on_inputs}   packing: {config.training.packing}")

    sft_config = build_sft_config(config)
    sft_config.output_dir = "/tmp/verify-loss-masking"
    sft_config.report_to = []
    sft_config.per_device_train_batch_size = min(2, args.rows)
    # This harness only builds a batch; nothing is trained or evaluated.
    sft_config.eval_strategy = "no"
    sft_config.save_strategy = "no"
    sft_config.load_best_model_at_end = False
    # MPS/GPU adds nothing here and MPS rejects bfloat16.
    sft_config.use_cpu = True
    sft_config.bf16 = False
    sft_config.fp16 = False

    trainer = SFTTrainer(
        model=tiny_model(config.model.model_name_or_path, len(tokenizer)),
        args=sft_config,
        train_dataset=rendered["train"],
        processing_class=tokenizer,
    )

    batch = next(iter(trainer.get_train_dataloader()))
    input_ids = batch["input_ids"]
    labels = batch["labels"]
    print(f"\nbatch tensors: {sorted(batch.keys())}")
    print(f"batch shape: {tuple(input_ids.shape)}")

    failures: list[str] = []
    for index in range(input_ids.shape[0]):
        ids = input_ids[index]
        row_labels = labels[index]
        supervised_mask = row_labels != IGNORE_INDEX

        total = int(supervised_mask.numel())
        supervised = int(supervised_mask.sum())
        full_text = tokenizer.decode(ids, skip_special_tokens=False)
        supervised_text = tokenizer.decode(ids[supervised_mask], skip_special_tokens=False)

        ratio = supervised / total if total else 0.0
        print(
            f"\n[{index}] tokens={total} supervised={supervised} masked={total - supervised} "
            f"ratio={ratio:.1%}"
        )
        if index < args.show:
            print("--- full sequence ---")
            print(full_text)
            print("--- supervised span (labels != -100) ---")
            print(supervised_text)

        if supervised == 0:
            failures.append(f"[{index}] nothing is supervised; the target is fully masked")
            continue
        if supervised == total:
            failures.append(f"[{index}] everything is supervised; masking is not applied at all")

        if not config.data.train_on_inputs:
            # The instruction is near-identical on every row, so leakage is easy
            # to detect: none of these may appear in the supervised span.
            for marker in ("Analyze the following C++ code", "### Code", "senior C++ code review"):
                if marker in supervised_text:
                    failures.append(f"[{index}] prompt text leaked into the supervised span: {marker!r}")
            if not supervised_text.lstrip().startswith("{"):
                failures.append(
                    f"[{index}] supervised span does not start with the JSON target: "
                    f"{supervised_text[:60]!r}"
                )

        if tokenizer.eos_token and tokenizer.eos_token not in full_text:
            failures.append(f"[{index}] sequence does not contain EOS; generation will not stop")

        pad_id = tokenizer.pad_token_id
        if pad_id is not None:
            padded = ids == pad_id
            # A pad token that is also the EOS token legitimately carries a label.
            if pad_id != tokenizer.eos_token_id and bool((padded & supervised_mask).any()):
                failures.append(f"[{index}] padding positions are supervised")

    print("\n" + "=" * 72)
    if failures:
        print("LOSS MASKING IS WRONG\n")
        for failure in failures:
            print("  -", failure)
        print("\nDo not train on this. See the loss-masking-verify skill.")
        return 1
    print("LOSS MASKING VERIFIED")
    print("  supervised span is the target only, padding is masked, EOS present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
