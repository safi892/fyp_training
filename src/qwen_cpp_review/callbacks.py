from __future__ import annotations

import logging
import time

import torch
from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

LOGGER = logging.getLogger(__name__)


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
            "step=%s loss=%s lr=%s grad_norm=%s steps/sec=%.3f gpu_mem=%.2fGB",
            state.global_step,
            logs.get("loss"),
            logs.get("learning_rate"),
            logs.get("grad_norm"),
            steps_per_second,
            memory_gb,
        )
        self._last_time = now
        self._last_step = state.global_step

