from __future__ import annotations

import logging
import os
from typing import Any

import torch
from peft import LoraConfig, TaskType, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, PreTrainedModel

from qwen_cpp_review.config import LoraConfigData, ModelConfig

LOGGER = logging.getLogger(__name__)


def create_bnb_config() -> BitsAndBytesConfig:
    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )


def create_lora_config(config: LoraConfigData) -> LoraConfig:
    return LoraConfig(
        r=config.r,
        lora_alpha=config.alpha,
        target_modules=config.target_modules,
        lora_dropout=config.dropout,
        bias=config.bias,
        task_type=getattr(TaskType, config.task_type),
    )


def load_model_for_qlora(config: ModelConfig, gradient_checkpointing: bool) -> PreTrainedModel:
    kwargs: dict[str, Any] = {
        "trust_remote_code": config.trust_remote_code,
        "quantization_config": create_bnb_config(),
    }
    if config.torch_dtype != "auto":
        kwargs["torch_dtype"] = getattr(torch, config.torch_dtype)
    else:
        kwargs["dtype"] = "auto"

    if config.flash_attention:
        kwargs["attn_implementation"] = "flash_attention_2"
    elif config.attn_implementation:
        kwargs["attn_implementation"] = config.attn_implementation

    local_rank = int(os.environ.get("LOCAL_RANK", "-1"))
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    if torch.cuda.is_available():
        kwargs["device_map"] = {"": local_rank} if world_size > 1 and local_rank >= 0 else "auto"

    model = AutoModelForCausalLM.from_pretrained(config.model_name_or_path, **kwargs)
    model.config.use_cache = config.use_cache
    model = prepare_model_for_kbit_training(
        model,
        use_gradient_checkpointing=gradient_checkpointing,
    )
    if gradient_checkpointing:
        model.gradient_checkpointing_enable()
    return model


def log_parameter_summary(model: PreTrainedModel) -> None:
    trainable = 0
    total = 0
    for parameter in model.parameters():
        count = parameter.numel()
        total += count
        if parameter.requires_grad:
            trainable += count
    frozen = total - trainable
    pct = 100 * trainable / total if total else 0.0
    LOGGER.info(
        "parameters: trainable=%s frozen=%s total=%s trainable_pct=%.4f",
        f"{trainable:,}",
        f"{frozen:,}",
        f"{total:,}",
        pct,
    )

