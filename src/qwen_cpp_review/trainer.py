from __future__ import annotations

import logging
from pathlib import Path

import torch
from transformers import EarlyStoppingCallback, PreTrainedTokenizerBase
from trl import SFTConfig, SFTTrainer

from qwen_cpp_review.callbacks import ThroughputAndMemoryCallback
from qwen_cpp_review.checkpoint import (
    convert_adapter_checkpoint_to_pth,
    copy_checkpoint_dir,
    find_latest_checkpoint,
    save_current_adapter_pth,
)
from qwen_cpp_review.config import AppConfig
from qwen_cpp_review.dataset import load_review_dataset, prepare_sft_dataset
from qwen_cpp_review.model import create_lora_config, load_model_for_qlora, log_parameter_summary
from qwen_cpp_review.seed import seed_everything

LOGGER = logging.getLogger(__name__)


def resolve_precision_flags(bf16: bool | str, fp16: bool | str) -> tuple[bool, bool]:
    if bf16 == "auto" and fp16 == "auto":
        use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
        return use_bf16, torch.cuda.is_available() and not use_bf16
    if bf16 == "auto":
        return torch.cuda.is_available() and torch.cuda.is_bf16_supported(), bool(fp16)
    if fp16 == "auto":
        return bool(bf16), torch.cuda.is_available() and not bool(bf16)
    return bool(bf16), bool(fp16)


def build_sft_config(config: AppConfig) -> SFTConfig:
    bf16, fp16 = resolve_precision_flags(config.training.bf16, config.training.fp16)
    return SFTConfig(
        output_dir=config.training.output_dir,
        num_train_epochs=config.training.num_train_epochs,
        per_device_train_batch_size=config.training.per_device_train_batch_size,
        per_device_eval_batch_size=config.training.per_device_eval_batch_size,
        gradient_accumulation_steps=config.training.gradient_accumulation_steps,
        learning_rate=config.training.learning_rate,
        weight_decay=config.training.weight_decay,
        warmup_ratio=config.training.warmup_ratio,
        lr_scheduler_type=config.training.lr_scheduler_type,
        optim=config.training.optim,
        max_grad_norm=config.training.max_grad_norm,
        logging_steps=config.training.logging_steps,
        eval_steps=config.training.eval_steps,
        save_steps=config.training.save_steps,
        save_total_limit=config.training.save_total_limit,
        eval_strategy=config.training.eval_strategy,
        save_strategy=config.training.save_strategy,
        load_best_model_at_end=config.training.load_best_model_at_end,
        metric_for_best_model=config.training.metric_for_best_model,
        greater_is_better=config.training.greater_is_better,
        gradient_checkpointing=config.training.gradient_checkpointing,
        bf16=bf16,
        fp16=fp16,
        packing=config.training.packing,
        max_length=config.data.max_seq_length,
        report_to=config.training.report_to,
        seed=config.training.seed,
        dataset_text_field="text",
    )


def build_trainer(config: AppConfig, tokenizer: PreTrainedTokenizerBase) -> SFTTrainer:
    seed_everything(config.training.seed)
    raw_dataset = load_review_dataset(config.data)
    sft_dataset = prepare_sft_dataset(raw_dataset, config.data, tokenizer)
    model = load_model_for_qlora(config.model, config.training.gradient_checkpointing)
    peft_config = create_lora_config(config.lora)
    callbacks = [ThroughputAndMemoryCallback()]
    if config.training.early_stopping_patience and "validation" in sft_dataset:
        callbacks.append(EarlyStoppingCallback(config.training.early_stopping_patience))

    trainer = SFTTrainer(
        model=model,
        args=build_sft_config(config),
        train_dataset=sft_dataset["train"],
        eval_dataset=sft_dataset.get("validation"),
        processing_class=tokenizer,
        peft_config=peft_config,
        callbacks=callbacks,
    )
    log_parameter_summary(trainer.model)
    return trainer


def train(config: AppConfig, tokenizer: PreTrainedTokenizerBase) -> None:
    output_dir = Path(config.training.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config.save(output_dir / "training_config.yaml")

    trainer = build_trainer(config, tokenizer)
    resume = config.training.resume_from_checkpoint or find_latest_checkpoint(output_dir)
    if resume:
        LOGGER.info("resuming from checkpoint: %s", resume)
    trainer.train(resume_from_checkpoint=resume)

    latest_checkpoint = find_latest_checkpoint(output_dir)
    if latest_checkpoint:
        copy_checkpoint_dir(latest_checkpoint, output_dir / "last_adapter")
        convert_adapter_checkpoint_to_pth(latest_checkpoint, output_dir / "last_adapter.pth")
        LOGGER.info("saved last adapter checkpoint and pth from %s", latest_checkpoint)

    best_checkpoint = trainer.state.best_model_checkpoint
    if best_checkpoint:
        copy_checkpoint_dir(best_checkpoint, output_dir / "best_adapter")
        convert_adapter_checkpoint_to_pth(best_checkpoint, output_dir / "best_adapter.pth")
        LOGGER.info("saved best adapter checkpoint and pth from %s", best_checkpoint)

    trainer.save_model(output_dir / "final_adapter")
    tokenizer.save_pretrained(output_dir / "final_adapter")
    config.save(output_dir / "final_adapter" / "training_config.yaml")
    save_current_adapter_pth(trainer.model, output_dir / "final_adapter.pth")
    LOGGER.info("saved final adapter to %s", output_dir / "final_adapter")
