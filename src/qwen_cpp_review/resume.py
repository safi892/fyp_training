"""Checkpoint resume planning.

Training on preemptible hardware (Kaggle sessions, spot instances) is
interrupted routinely, so resuming has to be a first-class, self-diagnosing
operation instead of a boolean flag. This module resolves *how* a run should
continue from a checkpoint and repairs the things that make the naive
``trainer.train(resume_from_checkpoint=...)`` call blow up.

Four modes, strongest first:

``exact``
    Adapter weights + optimizer moments + LR scheduler + trainer state
    (global step, epoch, data position, RNG). Training continues as if it was
    never interrupted. This is the only mode that is mathematically a
    continuation of the previous run.
``state``
    Adapter weights + trainer state + LR scheduler position. The optimizer
    moments are dropped. Used when the saved optimizer state cannot be
    restored - most commonly because ``optim`` changed between runs, or
    because a bitsandbytes paged optimizer state fails to load. The step
    counter, the data position and the learning rate are all still correct,
    so this costs only the Adam moment estimates (a few dozen steps of
    warm-up), not 750 steps of progress.
``adapter``
    Adapter weights only. Step counter, LR schedule and optimizer all restart
    at zero. Last resort, and the mode this project used to fall back to
    unconditionally.
``scratch``
    Fresh run, no checkpoint.

``auto`` picks the strongest mode the checkpoint on disk actually supports.

Nothing here imports torch at module scope: checkpoint inspection has to work
on a laptop without a CUDA build installed.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

ADAPTER_WEIGHT_FILES = ("adapter_model.safetensors", "adapter_model.bin")
ADAPTER_CONFIG_FILE = "adapter_config.json"
TRAINER_STATE_FILE = "trainer_state.json"
OPTIMIZER_STATE_FILE = "optimizer.pt"
SCHEDULER_STATE_FILE = "scheduler.pt"
TRAINING_ARGS_FILE = "training_args.bin"
MANIFEST_FILE = "resume_manifest.json"
DISABLED_SUFFIX = ".unusable"
STAGING_MARKER = ".resume_staged"

MODE_AUTO = "auto"
MODE_EXACT = "exact"
MODE_STATE = "state"
MODE_ADAPTER = "adapter"
MODE_SCRATCH = "scratch"

#: Resume modes ordered strongest first. ``auto`` is not a tier, it selects one.
TIER_ORDER = (MODE_EXACT, MODE_STATE, MODE_ADAPTER, MODE_SCRATCH)
VALID_MODES = (MODE_AUTO,) + TIER_ORDER

MODE_SUMMARY = {
    MODE_EXACT: "adapter + optimizer + scheduler + trainer state (true continuation)",
    MODE_STATE: "adapter + scheduler + trainer state, fresh optimizer moments",
    MODE_ADAPTER: "adapter weights only, step counter and LR schedule restart",
    MODE_SCRATCH: "fresh run from step 0",
}


class ResumeError(RuntimeError):
    """Raised when a resume mode was requested explicitly but cannot be honoured."""


# --------------------------------------------------------------------------- #
# Checkpoint inspection
# --------------------------------------------------------------------------- #


@dataclass
class CheckpointInfo:
    """Everything we can learn about a checkpoint directory without CUDA."""

    path: Path
    step: int = 0
    has_adapter: bool = False
    has_adapter_config: bool = False
    has_trainer_state: bool = False
    has_optimizer: bool = False
    has_scheduler: bool = False
    writable: bool = False
    global_step: int | None = None
    epoch: float | None = None
    max_steps: int | None = None
    num_train_epochs: float | None = None
    train_batch_size: int | None = None
    best_metric: float | None = None
    best_model_checkpoint: str | None = None
    optim: str | None = None
    gradient_accumulation_steps: int | None = None
    world_size: int | None = None
    lora_r: int | None = None
    lora_alpha: int | None = None
    lora_target_modules: list[str] | None = None
    manifest: dict[str, Any] = field(default_factory=dict)

    @property
    def supports_exact(self) -> bool:
        return self.has_adapter and self.has_trainer_state and self.has_optimizer and self.has_scheduler

    @property
    def supports_state(self) -> bool:
        return self.has_adapter and self.has_trainer_state

    @property
    def supports_adapter(self) -> bool:
        return self.has_adapter

    @property
    def resume_step(self) -> int:
        return self.global_step if self.global_step is not None else self.step

    @property
    def steps_per_epoch(self) -> float | None:
        """Optimizer steps per epoch as recorded by the run that wrote this checkpoint."""
        if not self.max_steps or not self.num_train_epochs:
            return None
        return self.max_steps / self.num_train_epochs

    def effective_batch_size(self, world_size: int | None = None) -> int | None:
        """Samples consumed per optimizer step when this checkpoint was written."""
        if not self.train_batch_size or not self.gradient_accumulation_steps:
            return None
        world = world_size or self.world_size or 1
        return self.train_batch_size * self.gradient_accumulation_steps * world

    def estimated_train_rows(self, world_size: int | None = None) -> int | None:
        """Training rows the previous run saw, derived from its step accounting."""
        steps = self.steps_per_epoch
        batch = self.effective_batch_size(world_size)
        if steps is None or batch is None:
            return None
        return int(round(steps * batch))

    def missing_for(self, tier: str) -> list[str]:
        """Files that are absent and block ``tier``."""
        missing: list[str] = []
        if tier in (MODE_EXACT, MODE_STATE, MODE_ADAPTER) and not self.has_adapter:
            missing.append(" or ".join(ADAPTER_WEIGHT_FILES))
        if tier in (MODE_EXACT, MODE_STATE) and not self.has_trainer_state:
            missing.append(TRAINER_STATE_FILE)
        if tier == MODE_EXACT and not self.has_optimizer:
            missing.append(OPTIMIZER_STATE_FILE)
        if tier == MODE_EXACT and not self.has_scheduler:
            missing.append(SCHEDULER_STATE_FILE)
        return missing


def checkpoint_step(path: str | Path) -> int | None:
    """Step number encoded in a ``checkpoint-<n>`` directory name."""
    name = Path(path).name
    if not name.startswith("checkpoint-"):
        return None
    try:
        return int(name.split("-")[-1])
    except ValueError:
        return None


def list_checkpoints(output_dir: str | Path) -> list[Path]:
    """All ``checkpoint-*`` directories under ``output_dir``, oldest first."""
    root = Path(output_dir)
    if not root.is_dir():
        return []
    found = [
        (step, path)
        for path in root.glob("checkpoint-*")
        if path.is_dir() and (step := checkpoint_step(path)) is not None
    ]
    return [path for _, path in sorted(found, key=lambda item: item[0])]


def inspect_checkpoint(path: str | Path) -> CheckpointInfo:
    """Read every metadata file a checkpoint directory may contain.

    Never raises for a malformed checkpoint: an unreadable file simply leaves
    the corresponding field unset so the caller can degrade instead of crash.
    """
    target = Path(path)
    info = CheckpointInfo(path=target, step=checkpoint_step(target) or 0)
    if not target.is_dir():
        return info

    info.has_adapter = any((target / name).is_file() for name in ADAPTER_WEIGHT_FILES)
    info.has_adapter_config = (target / ADAPTER_CONFIG_FILE).is_file()
    info.has_trainer_state = (target / TRAINER_STATE_FILE).is_file()
    info.has_optimizer = (target / OPTIMIZER_STATE_FILE).is_file()
    info.has_scheduler = (target / SCHEDULER_STATE_FILE).is_file()
    info.writable = os.access(target, os.W_OK)

    state = _read_json(target / TRAINER_STATE_FILE)
    if state:
        info.global_step = state.get("global_step")
        info.epoch = state.get("epoch")
        info.max_steps = state.get("max_steps")
        info.num_train_epochs = state.get("num_train_epochs")
        info.train_batch_size = state.get("train_batch_size")
        info.best_metric = state.get("best_metric")
        info.best_model_checkpoint = state.get("best_model_checkpoint")

    adapter_config = _read_json(target / ADAPTER_CONFIG_FILE)
    if adapter_config:
        info.lora_r = adapter_config.get("r")
        info.lora_alpha = adapter_config.get("lora_alpha")
        modules = adapter_config.get("target_modules")
        info.lora_target_modules = sorted(modules) if isinstance(modules, (list, set)) else modules

    manifest = _read_json(target / MANIFEST_FILE) or {}
    info.manifest = manifest
    if manifest:
        info.optim = manifest.get("optim", info.optim)
        info.gradient_accumulation_steps = manifest.get("gradient_accumulation_steps")
        info.world_size = manifest.get("world_size")

    # Checkpoints written before this project grew a manifest still carry the
    # serialized TrainingArguments, which is where `optim` really lives.
    if info.optim is None or info.gradient_accumulation_steps is None:
        args = _read_training_args(target / TRAINING_ARGS_FILE)
        if args:
            info.optim = info.optim or args.get("optim")
            info.gradient_accumulation_steps = (
                info.gradient_accumulation_steps or args.get("gradient_accumulation_steps")
            )
            info.world_size = info.world_size or args.get("world_size")
            info.train_batch_size = info.train_batch_size or args.get("per_device_train_batch_size")
    return info


def find_latest_checkpoint(output_dir: str | Path, tier: str = MODE_ADAPTER) -> str | None:
    """Newest checkpoint under ``output_dir`` that can actually serve ``tier``.

    A crash mid-save (the normal way a Kaggle session ends) leaves a
    ``checkpoint-N`` directory with no ``trainer_state.json``. Picking it
    blindly is what turns "resume" into
    ``ValueError: Can't find a valid checkpoint at ...``, so incomplete
    directories are skipped and the previous good one is used instead.
    """
    for path in reversed(list_checkpoints(output_dir)):
        info = inspect_checkpoint(path)
        if _supports(info, tier):
            return str(path)
        LOGGER.warning(
            "skipping unusable checkpoint %s for %s resume (missing: %s)",
            path,
            tier,
            ", ".join(info.missing_for(tier)) or "unknown",
        )
    return None


def _supports(info: CheckpointInfo, tier: str) -> bool:
    if tier == MODE_EXACT:
        return info.supports_exact
    if tier == MODE_STATE:
        return info.supports_state
    if tier == MODE_ADAPTER:
        return info.supports_adapter
    return True


def available_tier(info: CheckpointInfo) -> str:
    """Strongest tier the files on disk support."""
    for tier in TIER_ORDER:
        if _supports(info, tier):
            return tier
    return MODE_SCRATCH


# --------------------------------------------------------------------------- #
# Resume plan
# --------------------------------------------------------------------------- #


@dataclass
class ResumePlan:
    """The decision of how this run continues, plus everything needed to do it."""

    mode: str
    requested_mode: str = MODE_AUTO
    source: Path | None = None
    checkpoint: Path | None = None
    resume_from_checkpoint: str | None = None
    adapter_path: str | None = None
    scheduler_state_path: str | None = None
    info: CheckpointInfo | None = None
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def start_step(self) -> int:
        if self.mode in (MODE_EXACT, MODE_STATE) and self.info is not None:
            return self.info.resume_step
        return 0

    @property
    def is_fresh(self) -> bool:
        return self.mode == MODE_SCRATCH

    def banner(self) -> str:
        """Multi-line, unambiguous description of what this run is doing.

        The old pipeline printed ``resume_from_checkpoint: None`` while it was
        in fact continuing from trained weights, which read as "not resumed".
        Every mode now states the step it starts from explicitly.
        """
        width = 78
        lines = [
            "=" * width,
            f"RESUME MODE: {self.mode.upper()}  ({MODE_SUMMARY[self.mode]})",
        ]
        if self.requested_mode != self.mode:
            verb = "resolved to" if self.requested_mode == MODE_AUTO else "degraded to"
            lines.append(f"  requested       : {self.requested_mode} -> {verb} {self.mode}")
        if self.source is not None:
            lines.append(f"  checkpoint      : {self.source}")
        if self.checkpoint is not None and self.checkpoint != self.source:
            lines.append(f"  staged copy     : {self.checkpoint}")
        if self.mode == MODE_SCRATCH:
            lines.append("  starting step   : 0 (no checkpoint)")
        else:
            lines.append(f"  starting step   : {self.start_step}")
            if self.info is not None and self.info.epoch is not None:
                lines.append(f"  starting epoch  : {self.info.epoch:.4f}")
        lines.append(f"  optimizer state : {'restored' if self.mode == MODE_EXACT else 'fresh'}")
        lines.append(
            "  lr schedule     : "
            + ("restored" if self.mode in (MODE_EXACT, MODE_STATE) else "restarts from warmup")
        )
        lines.append(
            "  step counter    : "
            + ("restored" if self.mode in (MODE_EXACT, MODE_STATE) else "restarts at 0")
        )
        for note in self.notes:
            lines.append(f"  note            : {note}")
        for warning in self.warnings:
            lines.append(f"  WARNING         : {warning}")
        lines.append("=" * width)
        return "\n".join(lines)

    def log(self) -> None:
        for line in self.banner().splitlines():
            LOGGER.info(line)


def resolve_resume_plan(config: Any, dry_run: bool = False) -> ResumePlan:
    """Decide how this run continues and prepare the checkpoint on disk.

    ``config`` is an :class:`~qwen_cpp_review.config.AppConfig`. Side effects
    are confined to the output directory: staging a read-only checkpoint into
    it, repairing a dangling ``best_model_checkpoint`` path, and disabling an
    unusable optimizer state file. ``dry_run`` resolves the same decision
    without touching disk, for status output.
    """
    training = config.training
    requested = (training.resume_mode or MODE_AUTO).lower()
    if requested not in VALID_MODES:
        raise ResumeError(
            f"Unknown resume_mode {requested!r}. Valid values: {', '.join(VALID_MODES)}"
        )

    output_dir = Path(training.output_dir)
    plan = ResumePlan(mode=MODE_SCRATCH, requested_mode=requested)

    if requested == MODE_SCRATCH:
        existing = list_checkpoints(output_dir)
        if existing:
            plan.warnings.append(
                f"resume_mode=scratch with {len(existing)} existing checkpoint(s) in {output_dir}; "
                "training restarts at step 0 and they will be rotated away"
            )
        return plan

    source = _resolve_source(training, output_dir, plan)
    if source is None:
        plan.notes.append("no checkpoint found, starting from step 0")
        return plan

    info = inspect_checkpoint(source)
    plan.source = source
    plan.info = info

    if not info.supports_adapter:
        plan.warnings.append(
            f"{source} has no adapter weights ({' or '.join(ADAPTER_WEIGHT_FILES)}); "
            "starting from step 0"
        )
        plan.info = None
        plan.source = None
        return plan

    target_mode = requested if requested != MODE_AUTO else available_tier(info)
    target_mode = _downgrade_for_files(target_mode, info, plan, requested)
    target_mode = _downgrade_for_compatibility(target_mode, info, training, plan, requested)

    if target_mode == MODE_ADAPTER:
        plan.mode = MODE_ADAPTER
        plan.adapter_path = str(source)
        plan.checkpoint = source
        return plan

    # exact / state both hand the checkpoint to the Trainer, which needs a
    # writable directory inside output_dir so it can keep saving from there.
    staged = _stage_checkpoint(source, output_dir, plan, dry_run=dry_run)
    plan.checkpoint = staged
    plan.resume_from_checkpoint = str(staged)
    plan.mode = target_mode

    if target_mode == MODE_STATE:
        scheduler_state = (staged if staged.is_dir() else source) / SCHEDULER_STATE_FILE
        plan.scheduler_state_path = str(scheduler_state) if scheduler_state.is_file() else None

    if dry_run:
        return plan

    if target_mode == MODE_STATE:
        _on_main(lambda: _disable_optimizer_state(staged), staged)
    else:
        _on_main(lambda: _enable_optimizer_state(staged), staged)

    _on_main(lambda: _repair_trainer_state(staged, output_dir, plan), staged)
    plan.info = inspect_checkpoint(staged)
    return plan


def _resolve_source(training: Any, output_dir: Path, plan: ResumePlan) -> Path | None:
    """Where the weights come from: explicit path, legacy path, or auto-discovery."""
    explicit = training.resume_from_checkpoint
    if explicit:
        path = Path(explicit)
        if not path.is_dir():
            raise ResumeError(f"resume_from_checkpoint does not exist: {path}")
        return path

    legacy = getattr(training, "initial_adapter_path", None)
    if legacy:
        path = Path(legacy)
        if not path.is_dir():
            raise ResumeError(f"initial_adapter_path does not exist: {path}")
        plan.notes.append(
            "initial_adapter_path is deprecated; use resume_from_checkpoint plus "
            "resume_mode (auto/exact/state/adapter)"
        )
        return path

    latest = find_latest_checkpoint(output_dir, tier=MODE_ADAPTER)
    return Path(latest) if latest else None


def _downgrade_for_files(mode: str, info: CheckpointInfo, plan: ResumePlan, requested: str) -> str:
    """Drop to a weaker tier when the checkpoint is missing state files."""
    if _supports(info, mode):
        return mode
    missing = ", ".join(info.missing_for(mode)) or "unknown files"
    if requested != MODE_AUTO:
        raise ResumeError(f"resume_mode={requested} needs {missing} in {info.path}")
    fallback = available_tier(info)
    plan.warnings.append(f"{info.path} is missing {missing}; using {fallback} resume instead")
    return fallback


def _downgrade_for_compatibility(
    mode: str,
    info: CheckpointInfo,
    training: Any,
    plan: ResumePlan,
    requested: str,
) -> str:
    """Reject an optimizer state that provably cannot be loaded.

    The failure this catches: a checkpoint written with ``paged_adamw_8bit``
    holds bitsandbytes 8-bit moment tensors (``state1``/``state2``/``qmap*``).
    Loading them into a ``torch.optim.AdamW`` succeeds silently and then dies
    on the first step with ``KeyError: 'exp_avg'``. Detecting it here turns an
    exploding run into a one-line warning and a ``state`` resume.
    """
    if mode != MODE_EXACT:
        return mode

    checkpoint_optim = info.optim
    current_optim = training.optim
    if checkpoint_optim and current_optim and checkpoint_optim != current_optim:
        message = (
            f"checkpoint was written with optim={checkpoint_optim} but this run uses "
            f"optim={current_optim}; the saved optimizer moments are not loadable"
        )
        if requested == MODE_EXACT:
            raise ResumeError(
                message + ". Set training.optim back to "
                f"{checkpoint_optim!r} for an exact resume, or use resume_mode=state."
            )
        plan.warnings.append(message + "; falling back to state resume")
        return MODE_STATE

    if checkpoint_optim is None:
        plan.notes.append(
            "checkpoint does not record its optimizer type; attempting exact resume with "
            "automatic fallback if the optimizer state fails to load"
        )
    return MODE_EXACT


def check_lora_compatibility(plan: ResumePlan, lora: Any) -> None:
    """Warn when the YAML LoRA block disagrees with the checkpoint's adapter.

    The adapter's own ``adapter_config.json`` always wins on load, so a
    mismatch means the configured values are silently ignored - worth saying
    out loud rather than debugging later.
    """
    info = plan.info
    if info is None or plan.mode == MODE_SCRATCH or not info.has_adapter_config:
        return
    configured_modules = (
        sorted(lora.target_modules) if isinstance(lora.target_modules, list) else lora.target_modules
    )
    mismatches = [
        (name, checkpoint_value, configured)
        for name, checkpoint_value, configured in (
            ("r", info.lora_r, lora.r),
            ("lora_alpha", info.lora_alpha, lora.alpha),
            ("target_modules", info.lora_target_modules, configured_modules),
        )
        if checkpoint_value is not None and checkpoint_value != configured
    ]
    for name, checkpoint_value, configured in mismatches:
        LOGGER.warning(
            "LoRA %s differs: checkpoint=%s config=%s. The checkpoint value is used.",
            name,
            checkpoint_value,
            configured,
        )


def check_dataset_drift(plan: ResumePlan, train_rows: int, effective_batch: int) -> None:
    """Warn when the training set changed size since the checkpoint was written.

    Step 750 of a 6072-step run means something different if the dataset grew;
    the resumed run silently trains on a different schedule. Detected from the
    checkpoint's own ``max_steps``/``num_train_epochs`` accounting, so it also
    works for checkpoints written before the manifest existed.
    """
    info = plan.info
    if info is None or plan.mode not in (MODE_EXACT, MODE_STATE):
        return

    recorded = info.manifest.get("train_dataset_rows")
    estimated = info.estimated_train_rows()
    previous = recorded or estimated
    if not previous:
        return
    drift = abs(previous - train_rows) / max(previous, 1)
    if drift <= 0.02:
        return
    LOGGER.warning(
        "training set changed size since the checkpoint: %s -> %s rows (%.1f%%). "
        "Step %s no longer refers to the same position in the schedule; the run "
        "continues but is not a strict continuation.",
        previous,
        train_rows,
        drift * 100,
        info.resume_step,
    )
    recorded_batch = info.effective_batch_size()
    if recorded_batch and recorded_batch != effective_batch:
        LOGGER.warning(
            "effective batch size changed since the checkpoint: %s -> %s samples per step",
            recorded_batch,
            effective_batch,
        )


def degraded_plan(plan: ResumePlan, config: Any) -> ResumePlan | None:
    """Next weaker plan to try after ``plan`` failed at runtime.

    Only used as a safety net; the checks above catch the predictable
    incompatibilities before a single batch is loaded.
    """
    if plan.mode == MODE_EXACT:
        weaker = MODE_STATE
    elif plan.mode == MODE_STATE:
        weaker = MODE_ADAPTER
    else:
        return None
    if plan.source is None:
        return None

    training = config.training
    fallback = ResumePlan(
        mode=weaker,
        requested_mode=plan.requested_mode,
        source=plan.source,
        info=plan.info,
        notes=list(plan.notes) + [f"automatic fallback after {plan.mode} resume failed"],
        warnings=list(plan.warnings),
    )
    if weaker == MODE_ADAPTER:
        fallback.adapter_path = str(plan.source)
        fallback.checkpoint = plan.checkpoint or plan.source
        return fallback

    staged = _stage_checkpoint(plan.source, Path(training.output_dir), fallback)
    scheduler_state = staged / SCHEDULER_STATE_FILE
    fallback.checkpoint = staged
    fallback.resume_from_checkpoint = str(staged)
    fallback.scheduler_state_path = str(scheduler_state) if scheduler_state.is_file() else None
    _on_main(lambda: _disable_optimizer_state(staged), staged)
    fallback.info = inspect_checkpoint(staged)
    return fallback


# --------------------------------------------------------------------------- #
# Fresh starts
# --------------------------------------------------------------------------- #


def archive_existing_checkpoints(output_dir: str | Path) -> Path | None:
    """Move an existing run out of the way so a fresh run cannot mix with it.

    Returns the archive directory, or ``None`` when there was nothing to move.
    Renaming rather than deleting means a mistaken fresh start is recoverable.
    """
    root = Path(output_dir)
    if not root.is_dir():
        return None

    archived: list[Path] = []

    def move() -> None:
        movable = [path for path in root.iterdir() if path.name != "archive"]
        if not movable:
            return
        archive = root / "archive" / f"run-{time.strftime('%Y%m%d-%H%M%S')}"
        archive.mkdir(parents=True, exist_ok=True)
        for path in movable:
            shutil.move(str(path), str(archive / path.name))
        LOGGER.warning("archived previous run contents to %s", archive)
        archived.append(archive)

    # Under `accelerate launch` this runs once per GPU; only one may move files.
    _on_main(move, root)
    return archived[0] if archived else None


# --------------------------------------------------------------------------- #
# On-disk repairs
# --------------------------------------------------------------------------- #


def _stage_checkpoint(
    source: Path, output_dir: Path, plan: ResumePlan, dry_run: bool = False
) -> Path:
    """Ensure the checkpoint lives in a writable directory inside ``output_dir``.

    Kaggle mounts ``/kaggle/input`` read-only, so a checkpoint attached as a
    dataset cannot be repaired in place and cannot participate in checkpoint
    rotation. Copying it to ``output_dir/checkpoint-<step>`` makes the resumed
    run indistinguishable from one that never stopped.
    """
    info = inspect_checkpoint(source)
    step = info.resume_step
    target = output_dir / f"checkpoint-{step}"

    if source.resolve() == target.resolve():
        if not info.writable:
            raise ResumeError(f"checkpoint {source} is not writable")
        return target
    if source.parent.resolve() == output_dir.resolve() and info.writable:
        return source
    if dry_run:
        plan.notes.append(f"would stage the checkpoint into {target}")
        return target

    def copy() -> None:
        if target.exists() and _supports(inspect_checkpoint(target), MODE_STATE):
            LOGGER.info("reusing already staged checkpoint %s", target)
            return
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.info("staging checkpoint %s -> %s", source, target)
        shutil.copytree(source, target)

    _on_main(copy, target)
    plan.notes.append(f"staged read-only checkpoint into {target}")
    return target


def _disable_optimizer_state(checkpoint: Path) -> None:
    """Hide ``optimizer.pt`` so the Trainer skips loading it.

    Renamed, not deleted: the bytes stay available for a later exact resume
    with a matching ``optim``.
    """
    optimizer = checkpoint / OPTIMIZER_STATE_FILE
    if not optimizer.is_file():
        return
    disabled = checkpoint / (OPTIMIZER_STATE_FILE + DISABLED_SUFFIX)
    disabled.unlink(missing_ok=True)
    optimizer.rename(disabled)
    LOGGER.info("optimizer state set aside as %s (state resume)", disabled.name)


def _enable_optimizer_state(checkpoint: Path) -> None:
    """Undo :func:`_disable_optimizer_state` for an exact resume."""
    optimizer = checkpoint / OPTIMIZER_STATE_FILE
    disabled = checkpoint / (OPTIMIZER_STATE_FILE + DISABLED_SUFFIX)
    if optimizer.is_file() or not disabled.is_file():
        return
    disabled.rename(optimizer)
    LOGGER.info("restored previously disabled optimizer state in %s", checkpoint)


def _repair_trainer_state(checkpoint: Path, output_dir: Path, plan: ResumePlan) -> None:
    """Clear a ``best_model_checkpoint`` that points outside this session.

    ``trainer_state.json`` stores an absolute path. After a Kaggle session
    ends, or after ``save_total_limit`` rotated that directory away, the path
    dangles - ``load_best_model_at_end`` then finds nothing and the run ends
    holding the last weights while claiming to hold the best. If the same
    checkpoint name exists in this ``output_dir`` the path is remapped;
    otherwise the stale best metric is cleared so the next evaluation
    establishes a reachable best.
    """
    state_file = checkpoint / TRAINER_STATE_FILE
    state = _read_json(state_file)
    if not state:
        return
    best = state.get("best_model_checkpoint")
    if not best or Path(best).is_dir():
        return

    remapped = output_dir / Path(best).name
    if remapped.is_dir():
        state["best_model_checkpoint"] = str(remapped)
        plan.notes.append(f"remapped best_model_checkpoint to {remapped}")
    else:
        state["best_model_checkpoint"] = None
        state["best_metric"] = None
        state["best_global_step"] = None
        plan.warnings.append(
            f"best checkpoint {best} no longer exists; cleared the stale best metric so "
            "load_best_model_at_end tracks a reachable checkpoint"
        )
    state_file.write_text(json.dumps(state, indent=2))


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("could not read %s: %s", path, exc)
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_training_args(path: Path) -> dict[str, Any]:
    """Pull the fields we care about out of a pickled ``TrainingArguments``."""
    if not path.is_file():
        return {}
    try:
        import torch

        args = torch.load(path, map_location="cpu", weights_only=False)
    except Exception as exc:  # unpicklable across versions, missing torch, ...
        LOGGER.debug("could not read %s: %s", path, exc)
        return {}
    return {
        key: getattr(args, key)
        for key in (
            "optim",
            "gradient_accumulation_steps",
            "per_device_train_batch_size",
            "world_size",
            "lr_scheduler_type",
            "learning_rate",
            "warmup_ratio",
        )
        if hasattr(args, key)
    }


def _world_size() -> int:
    try:
        return int(os.environ.get("WORLD_SIZE", "1"))
    except ValueError:
        return 1


def _is_main_process() -> bool:
    return int(os.environ.get("RANK", "0")) == 0


def _on_main(action, sync_dir: Path, timeout: float = 1800.0) -> None:
    """Run a filesystem mutation on rank 0 while other ranks wait for it.

    ``accelerate launch`` runs this module once per GPU. Two processes copying
    or rewriting the same checkpoint concurrently is how a resume directory
    gets half-written, so the work is serialized behind a marker file keyed on
    a token every rank in the launch agrees on.
    """
    if _world_size() <= 1:
        action()
        return

    token = (
        os.environ.get("TORCHELASTIC_RUN_ID")
        or os.environ.get("MASTER_PORT")
        or str(os.getppid())
    )
    marker = sync_dir.parent / f"{sync_dir.name}{STAGING_MARKER}"
    if _is_main_process():
        marker.unlink(missing_ok=True)
        action()
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(token)
        return

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if marker.is_file() and marker.read_text().strip() == token:
            return
        time.sleep(1.0)
    raise ResumeError(f"timed out waiting for rank 0 to prepare {sync_dir}")
