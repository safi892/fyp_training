from __future__ import annotations

from transformers import AutoTokenizer, PreTrainedTokenizerBase

from qwen_cpp_review.config import ModelConfig


def load_tokenizer(config: ModelConfig) -> PreTrainedTokenizerBase:
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_name_or_path,
        trust_remote_code=config.trust_remote_code,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return tokenizer

