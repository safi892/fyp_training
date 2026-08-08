from __future__ import annotations

import gc
import logging
from pathlib import Path

import torch
from peft import PeftModel
from transformers import EarlyStoppingCallback, PreTrainedTokenizerBase
from trl import SFTConfig, SFTTrainer

from qwen_cpp_review.callbacks import (
    LrSchedulerRestoreCallback,
    ResumeManifestCallback,
    ThroughputAndMemoryCallback,
    TrainingProgressGuard,
)
from qwen_cpp_review.checkpoint import (
    convert_adapter_checkpoint_to_pth,
    copy_checkpoint_dir,
    find_latest_checkpoint,
    save_current_adapter_pth,
)
from qwen_cpp_review.config import AppConfig
from qwen_cpp_review.dataset import load_review_dataset, prepare_sft_dataset
from qwen_cpp_review.model import create_lora_config, load_model_for_qlora, log_parameter_summary
from qwen_cpp_review.resume import (
    MODE_SCRATCH,
    ResumePlan,
    archive_existing_checkpoints,
    check_dataset_drift,
    check_lora_compatibility,
    degraded_plan,
    resolve_resume_plan,
)
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
        gradient_checkpointing_kwargs={
            "use_reentrant": config.training.gradient_checkpointing_use_reentrant
        },
        ddp_find_unused_parameters=config.training.ddp_find_unused_parameters,
        bf16=bf16,
        fp16=fp16,
        packing=config.training.packing,
        max_length=config.data.max_seq_length,
        report_to=config.training.report_to,
        seed=config.training.seed,
        # Verified against the installed TRL 0.25.0: completion_only_loss is
        # "supported only for prompt-completion datasets", and a language
        # modeling dataset (one text column) is supervised over the whole
        # sequence. So the dataset shape and this flag have to agree, and
        # dataset.py picks the shape from the same train_on_inputs setting.
        **(
            {"dataset_text_field": "text"}
            if config.data.train_on_inputs
            else {"completion_only_loss": True}
        ),
        # Populates state.num_input_tokens_seen, which ThroughputAndMemoryCallback
        # turns into a real tokens/sec rather than one inferred from batch shape.
        include_num_input_tokens_seen=True,
        # Kaggle pipes the training cell through tee, where a redrawing bar
        # becomes thousands of near-identical lines. The callback prints one
        # complete line per logging step instead.
        disable_tqdm=config.training.disable_tqdm,
    )


def check_supervision_setup(config: AppConfig, columns: list[str]) -> None:
    """Refuse to train when the loss would not cover what we think it covers.

    Both failures below are silent at runtime: the loss curve falls either way,
    and the model quietly learns to reproduce prompts or attends across packed
    document boundaries. See the `loss-masking-verify` skill.
    """
    if config.data.train_on_inputs:
        if "text" not in columns:
            raise ValueError(
                f"train_on_inputs is true, which needs a 'text' column; got {sorted(columns)}"
            )
        LOGGER.warning(
            "train_on_inputs is TRUE: loss covers the instruction and the input code, not just "
            "the target. Metrics will look better than the model is. Set data.train_on_inputs "
            "to false for completion-only loss."
        )
    else:
        missing = [name for name in ("prompt", "completion") if name not in columns]
        if missing:
            raise ValueError(
                f"completion-only loss needs prompt-completion columns; missing {missing} "
                f"in {sorted(columns)}"
            )

    if config.training.packing:
        # TRL 0.25.0: packing_strategy 'bfd' force-enables padding_free, which
        # it documents as supported only with FlashAttention 2/3. The T4 is
        # Turing and has neither, and 'wrapped' concatenates across documents.
        # Rather than accept cross-contamination, refuse.
        if not config.model.flash_attention:
            raise ValueError(
                "training.packing requires model.flash_attention; TRL's default 'bfd' strategy "
                "enables padding-free batching, which needs FlashAttention 2/3. On a T4 keep "
                "packing false and recover throughput by turning gradient_checkpointing off."
            )


def build_trainer(
    config: AppConfig,
    tokenizer: PreTrainedTokenizerBase,
    plan: ResumePlan | None = None,
) -> SFTTrainer:
    """Assemble the trainer for ``plan``.

    Only ``adapter`` mode preloads weights here. ``exact`` and ``state`` hand
    the checkpoint to ``Trainer.train(resume_from_checkpoint=...)``, which
    loads the adapter itself alongside the rest of the run state.
    """
    seed_everything(config.training.seed)
    raw_dataset = load_review_dataset(config.data)
    sft_dataset = prepare_sft_dataset(raw_dataset, config.data, tokenizer)
    check_supervision_setup(config, sft_dataset["train"].column_names)
    model = load_model_for_qlora(config.model, config.training.gradient_checkpointing)

    adapter_path = plan.adapter_path if plan else config.training.initial_adapter_path
    peft_config = None if adapter_path else create_lora_config(config.lora)
    if adapter_path:
        LOGGER.info("loading adapter weights into the base model: %s", adapter_path)
        model = PeftModel.from_pretrained(model, adapter_path, is_trainable=True)

    sft_config = build_sft_config(config)
    if plan is not None:
        _report_resume_context(plan, config, sft_config, sft_dataset["train"])

    callbacks = [ThroughputAndMemoryCallback(), ResumeManifestCallback(_dataset_info(sft_dataset))]
    if plan is not None and plan.scheduler_state_path is not None:
        callbacks.append(LrSchedulerRestoreCallback(plan.scheduler_state_path, plan.start_step))
    if config.training.early_stopping_patience and "validation" in sft_dataset:
        callbacks.append(EarlyStoppingCallback(config.training.early_stopping_patience))

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
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

    if config.training.resume_mode == MODE_SCRATCH and config.training.overwrite_output_dir:
        archive_existing_checkpoints(output_dir)

    config.save(output_dir / "training_config.yaml")

    plan = resolve_resume_plan(config)
    check_lora_compatibility(plan, config.lora)
    plan.log()

    trainer = _run_with_fallback(config, tokenizer, plan)
    _save_artifacts(config, tokenizer, trainer, output_dir)


def _run_with_fallback(
    config: AppConfig,
    tokenizer: PreTrainedTokenizerBase,
    plan: ResumePlan,
) -> SFTTrainer:
    """Train, degrading the resume mode if resuming fails before the first step.

    The predictable incompatibilities are already rejected while planning, so
    this only covers the rest: a truncated optimizer file, a bitsandbytes state
    that fails to deserialize, a PEFT version that cannot read the adapter. A
    failure after any optimizer step is a training failure and propagates
    untouched - retrying it would just burn hours and hide the real error.
    """
    attempt = plan
    while True:
        trainer = build_trainer(config, tokenizer, attempt)
        guard = TrainingProgressGuard()
        trainer.add_callback(guard)
        try:
            trainer.train(resume_from_checkpoint=attempt.resume_from_checkpoint)
            return trainer
        except Exception as exc:
            retryable = not guard.progressed and _is_resume_failure(exc)
            fallback = degraded_plan(attempt, config) if retryable else None
            if fallback is None or not config.training.resume_auto_fallback:
                raise
            LOGGER.error("%s resume failed before the first step: %s", attempt.mode, exc)
            LOGGER.error("retrying with %s resume", fallback.mode)
            _release(trainer)
            attempt = fallback
            attempt.log()


def _is_resume_failure(exc: BaseException) -> bool:
    """Whether ``exc`` is worth retrying with a weaker resume mode.

    Running out of memory is a capacity problem, not a resume problem: a retry
    would reload the base model and fail identically, so it propagates.
    """
    oom = getattr(torch, "OutOfMemoryError", None) or getattr(torch.cuda, "OutOfMemoryError", None)
    if oom is not None and isinstance(exc, oom):
        return False
    return not isinstance(exc, (MemoryError, KeyboardInterrupt))


def _save_artifacts(
    config: AppConfig,
    tokenizer: PreTrainedTokenizerBase,
    trainer: SFTTrainer,
    output_dir: Path,
) -> None:
    latest_checkpoint = find_latest_checkpoint(output_dir)
    if latest_checkpoint:
        copy_checkpoint_dir(latest_checkpoint, output_dir / "last_adapter")
        convert_adapter_checkpoint_to_pth(latest_checkpoint, output_dir / "last_adapter.pth")
        LOGGER.info("saved last adapter checkpoint and pth from %s", latest_checkpoint)

    best_checkpoint = trainer.state.best_model_checkpoint
    if best_checkpoint and Path(best_checkpoint).is_dir():
        copy_checkpoint_dir(best_checkpoint, output_dir / "best_adapter")
        convert_adapter_checkpoint_to_pth(best_checkpoint, output_dir / "best_adapter.pth")
        LOGGER.info("saved best adapter checkpoint and pth from %s", best_checkpoint)
    elif best_checkpoint:
        LOGGER.warning(
            "best checkpoint %s was rotated away before it could be copied; "
            "raise save_total_limit to keep it",
            best_checkpoint,
        )

    trainer.save_model(output_dir / "final_adapter")
    tokenizer.save_pretrained(output_dir / "final_adapter")
    config.save(output_dir / "final_adapter" / "training_config.yaml")
    save_current_adapter_pth(trainer.model, output_dir / "final_adapter.pth")
    LOGGER.info("saved final adapter to %s", output_dir / "final_adapter")


def _report_resume_context(
    plan: ResumePlan,
    config: AppConfig,
    sft_config: SFTConfig,
    train_dataset,
) -> None:
    """Log what this run will do in step terms, and flag dataset drift."""
    effective_batch = (
        sft_config.per_device_train_batch_size
        * sft_config.gradient_accumulation_steps
        * max(sft_config.world_size, 1)
    )
    rows = len(train_dataset)
    steps_per_epoch = max(rows // effective_batch, 1)
    total_steps = int(steps_per_epoch * config.training.num_train_epochs)
    LOGGER.info(
        "training plan: %s rows, effective batch %s, ~%s steps/epoch, ~%s total steps, "
        "starting at step %s",
        rows,
        effective_batch,
        steps_per_epoch,
        total_steps,
        plan.start_step,
    )
    check_dataset_drift(plan, rows, effective_batch)


def _dataset_info(sft_dataset) -> dict[str, object]:
    train_split = sft_dataset["train"]
    validation = sft_dataset.get("validation")
    return {
        "train_dataset_rows": len(train_split),
        "eval_dataset_rows": len(validation) if validation is not None else 0,
        "train_dataset_fingerprint": getattr(train_split, "_fingerprint", None),
    }


def _release(trainer: SFTTrainer) -> None:
    """Drop a failed trainer's GPU memory before rebuilding one.

    The retry loads a second copy of the quantized base model, so the first
    one has to let go of its VRAM first.
    """
    for attribute in ("model", "model_wrapped", "optimizer", "lr_scheduler"):
        if hasattr(trainer, attribute):
            setattr(trainer, attribute, None)
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
