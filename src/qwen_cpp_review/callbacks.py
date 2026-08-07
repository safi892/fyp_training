from __future__ import annotations

import importlib.metadata
import json
import logging
import math
import time
from pathlib import Path
from typing import Any

from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

try:  # torch ships with the `gpu` extra, absent in a CPU-only checkout
    import torch
except ImportError:  # pragma: no cover - exercised by the CPU test environment
    torch = None

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


def _format_duration(seconds: float) -> str:
    if seconds < 0 or seconds != seconds or seconds == float("inf"):
        return "--:--:--"
    seconds = int(seconds)
    return f"{seconds // 3600:d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


class ThroughputAndMemoryCallback(TrainerCallback):
    """Print a self-contained progress line on every logging step.

    Kaggle streams the training cell through a pipe, where a redrawing progress
    bar becomes thousands of near-identical lines. One complete line per log
    step stays readable there and in the saved log, and carries everything the
    `vram-profiles` skill requires reported: peak allocated memory, peak
    reserved memory, and tokens/sec.
    """

    def __init__(self) -> None:
        self._last_time = time.perf_counter()
        self._last_step = 0
        self._last_tokens = 0
        self._start_time = time.perf_counter()

    def on_train_begin(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs: object,
    ) -> None:
        self._start_time = time.perf_counter()
        self._last_time = self._start_time
        self._last_step = state.global_step
        self._last_tokens = getattr(state, "num_input_tokens_seen", 0) or 0
        if torch is not None and torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict[str, float] | None = None,
        **kwargs: object,
    ) -> None:
        if not logs or "loss" not in logs:
            return

        now = time.perf_counter()
        step_delta = max(state.global_step - self._last_step, 1)
        elapsed = max(now - self._last_time, 1e-6)
        steps_per_second = step_delta / elapsed

        tokens_seen = getattr(state, "num_input_tokens_seen", 0) or 0
        tokens_per_second = max(tokens_seen - self._last_tokens, 0) / elapsed

        allocated_gb = reserved_gb = 0.0
        if torch is not None and torch.cuda.is_available():
            allocated_gb = torch.cuda.max_memory_allocated() / 1024**3
            reserved_gb = torch.cuda.max_memory_reserved() / 1024**3

        remaining = state.max_steps - state.global_step
        eta = remaining / steps_per_second if steps_per_second > 0 else float("inf")
        percent = 100.0 * state.global_step / state.max_steps if state.max_steps else 0.0
        filled = int(percent / 100 * 24)

        line = (
            f"[{'=' * filled}{'.' * (24 - filled)}] {percent:5.1f}% "
            f"step {state.global_step}/{state.max_steps} "
            f"ep {state.epoch or 0:.2f} "
            f"loss {logs['loss']:.4f} "
            f"lr {logs.get('learning_rate', 0):.2e} "
            f"grad {logs.get('grad_norm', 0) or 0:.2f} "
            f"| {steps_per_second:.2f} it/s"
        )
        if tokens_per_second > 0:
            line += f" {tokens_per_second:,.0f} tok/s"
        if allocated_gb:
            line += f" | mem {allocated_gb:.2f}/{reserved_gb:.2f} GB"
        line += f" | elapsed {_format_duration(now - self._start_time)} eta {_format_duration(eta)}"

        # print, not just log: the Kaggle training cell shows stdout, and the
        # logger's handlers are not guaranteed to reach it.
        print(line, flush=True)
        LOGGER.info(line)

        self._last_time = now
        self._last_step = state.global_step
        self._last_tokens = tokens_seen

    def on_evaluate(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        metrics: dict[str, float] | None = None,
        **kwargs: object,
    ) -> None:
        if not metrics:
            return
        loss = metrics.get("eval_loss")
        parts = [f"EVAL step {state.global_step}"]
        if loss is not None:
            parts.append(f"eval_loss {loss:.4f}")
            try:
                parts.append(f"perplexity {math.exp(min(loss, 700)):.2f}")
            except (OverflowError, ValueError):
                pass
        best = state.best_metric
        if best is not None:
            parts.append(f"best {best:.4f}")
        runtime = metrics.get("eval_runtime")
        if runtime:
            parts.append(f"took {runtime:.0f}s")
        line = "  ".join(parts)
        print(line, flush=True)
        LOGGER.info(line)


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
