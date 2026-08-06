from __future__ import annotations

import importlib.metadata
import json
import logging
import time
from pathlib import Path
from typing import Any

import torch
from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

from qwen_cpp_review.resume import MANIFEST_FILE

LOGGER = logging.getLogger(__name__)

_VERSIONED_PACKAGES = (
    "torch",
    "transformers",
    "trl",
    "peft",
    "accelerate",
    "bitsandbytes",
    "datasets",
)


class ThroughputAndMemoryCallback(TrainerCallback):
    def __init__(self) -> None:
        self._last_time = time.perf_counter()
        self._last_step = 0

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict[str, float] | None = None,
        **kwargs: object,
    ) -> None:
        if not logs:
            return
        now = time.perf_counter()
        step_delta = max(state.global_step - self._last_step, 1)
        elapsed = max(now - self._last_time, 1e-6)
        steps_per_second = step_delta / elapsed
        memory_gb = 0.0
        if torch.cuda.is_available():
            memory_gb = torch.cuda.max_memory_allocated() / 1024**3
        LOGGER.info(
            "step=%s/%s loss=%s lr=%s grad_norm=%s steps/sec=%.3f gpu_mem=%.2fGB",
            state.global_step,
            state.max_steps,
            logs.get("loss"),
            logs.get("learning_rate"),
            logs.get("grad_norm"),
            steps_per_second,
            memory_gb,
        )
        self._last_time = now
        self._last_step = state.global_step


class LrSchedulerRestoreCallback(TrainerCallback):
    """Put the LR schedule back where the checkpoint left it during a state resume.

    ``Trainer._load_optimizer_and_scheduler`` loads ``scheduler.pt`` only when
    ``optimizer.pt`` is present, so a resume that deliberately drops the
    optimizer moments also loses the schedule position and silently restarts
    the cosine decay from warm-up - at step 750 that means jumping the learning
    rate back to the peak, which throws away real training progress.

    Loading the scheduler state here restores ``last_epoch``, and writing the
    resulting rate into the parameter groups makes it effective on the next
    step rather than one step later.
    """

    def __init__(self, scheduler_state_path: str | Path | None, target_step: int) -> None:
        self._path = Path(scheduler_state_path) if scheduler_state_path else None
        self._target_step = target_step
        self._restored = False

    def on_train_begin(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        lr_scheduler: Any = None,
        optimizer: Any = None,
        **kwargs: object,
    ) -> None:
        if self._restored or lr_scheduler is None or self._target_step <= 0:
            return
        self._restored = True

        if not self._load_state(lr_scheduler) and not self._replay_steps(lr_scheduler):
            LOGGER.error(
                "could not restore the LR schedule to step %s; training continues with a "
                "fresh warm-up",
                self._target_step,
            )
            return

        rates = lr_scheduler.get_last_lr()
        if optimizer is not None:
            for group, rate in zip(optimizer.param_groups, rates):
                group["lr"] = rate
        LOGGER.info(
            "restored LR schedule to step %s (learning_rate=%s)",
            self._target_step,
            rates[0] if rates else None,
        )

    def _load_state(self, lr_scheduler: Any) -> bool:
        if self._path is None or not self._path.is_file():
            return False
        try:
            state_dict = torch.load(self._path, map_location="cpu", weights_only=True)
            lr_scheduler.load_state_dict(state_dict)
        except Exception as exc:
            LOGGER.warning("could not load %s (%s); replaying scheduler steps", self._path, exc)
            return False
        return True

    def _replay_steps(self, lr_scheduler: Any) -> bool:
        """Fast-forward by stepping, for checkpoints with no ``scheduler.pt``."""
        try:
            for _ in range(self._target_step):
                lr_scheduler.step()
        except Exception as exc:
            LOGGER.warning("could not replay scheduler steps: %s", exc)
            return False
        return True


class ResumeManifestCallback(TrainerCallback):
    """Write ``resume_manifest.json`` into every checkpoint.

    A checkpoint that describes the run which produced it can be validated
    before a resume is attempted instead of after it crashes. Recorded here and
    read back by :mod:`qwen_cpp_review.resume`: the optimizer type, the step
    accounting, the dataset identity and the library versions.
    """

    def __init__(self, dataset_info: dict[str, Any] | None = None) -> None:
        self._dataset_info = dataset_info or {}

    def on_save(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs: object,
    ) -> None:
        if not state.is_world_process_zero:
            return
        checkpoint = Path(args.output_dir) / f"checkpoint-{state.global_step}"
        if not checkpoint.is_dir():
            return
        manifest = {
            "schema": 1,
            "global_step": state.global_step,
            "epoch": state.epoch,
            "max_steps": state.max_steps,
            "num_train_epochs": state.num_train_epochs,
            "optim": str(args.optim),
            "lr_scheduler_type": str(args.lr_scheduler_type),
            "learning_rate": args.learning_rate,
            "warmup_ratio": args.warmup_ratio,
            "per_device_train_batch_size": args.per_device_train_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "world_size": args.world_size,
            "seed": args.seed,
            "bf16": args.bf16,
            "fp16": args.fp16,
            "max_length": getattr(args, "max_length", None),
            "packing": getattr(args, "packing", None),
            **self._dataset_info,
            "versions": _package_versions(),
        }
        try:
            (checkpoint / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2))
        except OSError as exc:
            LOGGER.warning("could not write %s: %s", checkpoint / MANIFEST_FILE, exc)


class TrainingProgressGuard(TrainerCallback):
    """Records whether training advanced past the resume point.

    Distinguishes "the resume failed" from "training failed", so the automatic
    fallback to a weaker resume mode never masks a real training error such as
    an out-of-memory crash three hours in.
    """

    def __init__(self) -> None:
        self.progressed = False

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs: object,
    ) -> None:
        self.progressed = True


def _package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in _VERSIONED_PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return versions
