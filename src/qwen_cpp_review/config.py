from __future__ import annotations

from dataclasses import MISSING, asdict, dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ModelConfig:
    model_name_or_path: str = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    trust_remote_code: bool = True
    torch_dtype: str = "auto"
    attn_implementation: str = "sdpa"
    flash_attention: bool = False
    use_cache: bool = False


@dataclass
class DataConfig:
    data_files: list[str] = field(default_factory=lambda: ["cleaned/*.jsonl"])
    dataset_name: str | None = None
    dataset_config_name: str | None = None
    train_split: str = "train"
    validation_split: str = "validation"
    test_split: str = "test"
    validation_split_ratio: float = 0.05
    test_split_ratio: float = 0.0
    max_seq_length: int = 2048
    preprocessing_num_proc: int = 2
    cache_dir: str | None = ".cache/hf-datasets"
    train_on_inputs: bool = True
    prompt_style: str = "chat"
    identifier_augmentation: bool = False
    identifier_augmentation_copies: int = 1
    output_fields: list[str] = field(
        default_factory=lambda: ["comments", "explanation", "improved_code", "complexity_analysis"]
    )


@dataclass
class TrainingConfig:
    output_dir: str = "outputs/qwen2.5-coder-1.5b-cpp-review-qlora"
    num_train_epochs: float = 3.0
    per_device_train_batch_size: int = 1
    per_device_eval_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    learning_rate: float = 2e-4
    weight_decay: float = 0.0
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    #: Must stay fixed for the lifetime of a run: the optimizer state saved in a
    #: checkpoint is only loadable by the same optimizer. paged_adamw_8bit is
    #: the memory-lean alternative, at the cost of a bitsandbytes state that
    #: does not reliably survive a reload.
    optim: str = "adamw_torch"
    max_grad_norm: float = 0.3
    logging_steps: int = 10
    eval_steps: int = 100
    save_steps: int = 100
    save_total_limit: int = 3
    eval_strategy: str = "steps"
    save_strategy: str = "steps"
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_loss"
    greater_is_better: bool = False
    gradient_checkpointing: bool = True
    bf16: bool | str = "auto"
    fp16: bool | str = "auto"
    packing: bool = False
    gradient_checkpointing_use_reentrant: bool = False
    ddp_find_unused_parameters: bool = False
    report_to: list[str] = field(default_factory=lambda: ["tensorboard"])
    seed: int = 42
    early_stopping_patience: int | None = 5

    # --- resume ---------------------------------------------------------- #
    # "auto"    pick the strongest mode the checkpoint supports (default)
    # "exact"   require optimizer + scheduler + trainer state, else fail loudly
    # "state"   keep step/epoch/LR position, start the optimizer fresh
    # "adapter" load adapter weights only, restart the step counter at 0
    # "scratch" ignore checkpoints entirely and train from step 0
    resume_mode: str = "auto"
    #: Checkpoint to continue from. Empty means "newest under output_dir".
    resume_from_checkpoint: str | None = None
    #: Deprecated alias for resume_from_checkpoint, kept for old configs.
    initial_adapter_path: str | None = None
    #: Retry with a weaker resume mode if resuming fails before the first step.
    resume_auto_fallback: bool = True
    #: Archive an existing run instead of refusing to start a scratch run.
    overwrite_output_dir: bool = False


@dataclass
class LoraConfigData:
    r: int = 64
    alpha: int = 16
    dropout: float = 0.05
    target_modules: list[str] | str = field(
        default_factory=lambda: [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
    )
    bias: str = "none"
    task_type: str = "CAUSAL_LM"


@dataclass
class GenerationConfigData:
    max_new_tokens: int = 1024
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.05


@dataclass
class AppConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    lora: LoraConfigData = field(default_factory=LoraConfigData)
    generation: GenerationConfigData = field(default_factory=GenerationConfigData)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "AppConfig":
        payload = yaml.safe_load(Path(path).read_text()) or {}
        return _from_mapping(cls, payload)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(self.to_dict(), sort_keys=False))


def _from_mapping(cls: type[Any], payload: dict[str, Any]) -> Any:
    kwargs: dict[str, Any] = {}
    for item in fields(cls):
        raw = payload.get(item.name)
        if raw is None:
            continue
        default = item.default
        if default is MISSING and item.default_factory is not MISSING:
            default = item.default_factory()
        target_type = type(default) if default is not None else None
        if target_type and is_dataclass(target_type):
            kwargs[item.name] = _from_mapping(target_type, raw)
        elif is_dataclass(item.type):
            kwargs[item.name] = _from_mapping(item.type, raw)
        else:
            kwargs[item.name] = raw
    return cls(**kwargs)
