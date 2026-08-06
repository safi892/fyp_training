from __future__ import annotations

import json
from pathlib import Path

import pytest

from qwen_cpp_review.config import AppConfig
from qwen_cpp_review.resume import (
    MODE_ADAPTER,
    MODE_EXACT,
    MODE_SCRATCH,
    MODE_STATE,
    ResumeError,
    archive_existing_checkpoints,
    available_tier,
    find_latest_checkpoint,
    inspect_checkpoint,
    list_checkpoints,
    resolve_resume_plan,
)


def make_checkpoint(
    root: Path,
    step: int,
    *,
    adapter: bool = True,
    trainer_state: bool = True,
    optimizer: bool = True,
    scheduler: bool = True,
    optim: str | None = "adamw_torch",
    max_steps: int = 6072,
    num_train_epochs: int = 3,
    best_model_checkpoint: str | None = None,
    train_batch_size: int = 1,
    gradient_accumulation_steps: int = 8,
) -> Path:
    """Write a checkpoint directory shaped like the ones Trainer produces."""
    path = root / f"checkpoint-{step}"
    path.mkdir(parents=True, exist_ok=True)
    if adapter:
        (path / "adapter_model.safetensors").write_bytes(b"weights")
        (path / "adapter_config.json").write_text(
            json.dumps({"r": 64, "lora_alpha": 16, "target_modules": ["q_proj", "v_proj"]})
        )
    if trainer_state:
        (path / "trainer_state.json").write_text(
            json.dumps(
                {
                    "global_step": step,
                    "epoch": step / (max_steps / num_train_epochs),
                    "max_steps": max_steps,
                    "num_train_epochs": num_train_epochs,
                    "train_batch_size": train_batch_size,
                    "best_metric": 0.5,
                    "best_model_checkpoint": best_model_checkpoint,
                }
            )
        )
    if optimizer:
        (path / "optimizer.pt").write_bytes(b"optimizer")
    if scheduler:
        (path / "scheduler.pt").write_bytes(b"scheduler")
    if optim is not None:
        (path / "resume_manifest.json").write_text(
            json.dumps(
                {
                    "schema": 1,
                    "optim": optim,
                    "gradient_accumulation_steps": gradient_accumulation_steps,
                    "world_size": 1,
                }
            )
        )
    return path


def make_config(tmp_path: Path, **training: object) -> AppConfig:
    config = AppConfig()
    config.training.output_dir = str(tmp_path / "outputs")
    Path(config.training.output_dir).mkdir(parents=True, exist_ok=True)
    for key, value in training.items():
        setattr(config.training, key, value)
    return config


def test_list_checkpoints_orders_numerically(tmp_path: Path):
    for step in (50, 750, 100):
        make_checkpoint(tmp_path, step)

    assert [path.name for path in list_checkpoints(tmp_path)] == [
        "checkpoint-50",
        "checkpoint-100",
        "checkpoint-750",
    ]


def test_inspect_reads_step_accounting_and_optimizer_type(tmp_path: Path):
    path = make_checkpoint(tmp_path, 750, optim="paged_adamw_8bit")

    info = inspect_checkpoint(path)

    assert info.resume_step == 750
    assert info.optim == "paged_adamw_8bit"
    assert info.supports_exact
    assert available_tier(info) == MODE_EXACT
    assert info.steps_per_epoch == pytest.approx(2024.0)
    assert info.estimated_train_rows() == 16192


def test_incomplete_checkpoint_is_skipped(tmp_path: Path):
    make_checkpoint(tmp_path, 700)
    # A session killed mid-save leaves the directory without its state files.
    make_checkpoint(tmp_path, 750, trainer_state=False, optimizer=False, scheduler=False)

    assert find_latest_checkpoint(tmp_path, tier=MODE_EXACT).endswith("checkpoint-700")
    # Adapter weights alone are still enough for an adapter-only continue.
    assert find_latest_checkpoint(tmp_path, tier=MODE_ADAPTER).endswith("checkpoint-750")


def test_auto_picks_exact_resume_for_a_complete_checkpoint(tmp_path: Path):
    config = make_config(tmp_path)
    make_checkpoint(Path(config.training.output_dir), 750)

    plan = resolve_resume_plan(config)

    assert plan.mode == MODE_EXACT
    assert plan.start_step == 750
    assert plan.resume_from_checkpoint.endswith("checkpoint-750")
    assert plan.adapter_path is None


def test_optimizer_mismatch_degrades_to_state_resume(tmp_path: Path):
    """The failure that made exact resume crash: optim changed between runs."""
    config = make_config(tmp_path, optim="adamw_torch")
    checkpoint = make_checkpoint(Path(config.training.output_dir), 750, optim="paged_adamw_8bit")

    plan = resolve_resume_plan(config)

    assert plan.mode == MODE_STATE
    assert plan.start_step == 750, "the step counter must survive the optimizer mismatch"
    assert plan.scheduler_state_path is not None, "the LR schedule must survive too"
    assert not (checkpoint / "optimizer.pt").exists()
    assert (checkpoint / "optimizer.pt.unusable").exists(), "state is set aside, not deleted"
    assert any("optim=paged_adamw_8bit" in warning for warning in plan.warnings)


def test_explicit_exact_mode_refuses_to_degrade_silently(tmp_path: Path):
    config = make_config(tmp_path, optim="adamw_torch", resume_mode=MODE_EXACT)
    make_checkpoint(Path(config.training.output_dir), 750, optim="paged_adamw_8bit")

    with pytest.raises(ResumeError, match="paged_adamw_8bit"):
        resolve_resume_plan(config)


def test_missing_optimizer_falls_back_to_state_not_scratch(tmp_path: Path):
    config = make_config(tmp_path)
    make_checkpoint(Path(config.training.output_dir), 750, optimizer=False)

    plan = resolve_resume_plan(config)

    assert plan.mode == MODE_STATE
    assert plan.start_step == 750


def test_adapter_only_checkpoint_restarts_the_counter(tmp_path: Path):
    config = make_config(tmp_path)
    make_checkpoint(
        Path(config.training.output_dir),
        750,
        trainer_state=False,
        optimizer=False,
        scheduler=False,
        optim=None,
    )

    plan = resolve_resume_plan(config)

    assert plan.mode == MODE_ADAPTER
    assert plan.start_step == 0
    assert plan.adapter_path.endswith("checkpoint-750")
    assert plan.resume_from_checkpoint is None


def test_read_only_checkpoint_is_staged_into_the_output_dir(tmp_path: Path):
    external = make_checkpoint(tmp_path / "kaggle-input", 750)
    config = make_config(tmp_path, resume_from_checkpoint=str(external))

    plan = resolve_resume_plan(config)

    staged = Path(config.training.output_dir) / "checkpoint-750"
    assert plan.checkpoint == staged
    assert staged.is_dir()
    assert (staged / "adapter_model.safetensors").is_file()
    assert (staged / "optimizer.pt").is_file()


def test_dangling_best_model_checkpoint_is_cleared(tmp_path: Path):
    config = make_config(tmp_path)
    checkpoint = make_checkpoint(
        Path(config.training.output_dir),
        750,
        best_model_checkpoint="/kaggle/working/gone/checkpoint-500",
    )

    plan = resolve_resume_plan(config)

    state = json.loads((checkpoint / "trainer_state.json").read_text())
    assert state["best_model_checkpoint"] is None
    assert state["best_metric"] is None
    assert any("no longer exists" in warning for warning in plan.warnings)


def test_best_model_checkpoint_is_remapped_when_present(tmp_path: Path):
    config = make_config(tmp_path)
    output_dir = Path(config.training.output_dir)
    make_checkpoint(output_dir, 500)
    checkpoint = make_checkpoint(
        output_dir, 750, best_model_checkpoint="/some/dead/session/checkpoint-500"
    )

    resolve_resume_plan(config)

    state = json.loads((checkpoint / "trainer_state.json").read_text())
    assert state["best_model_checkpoint"] == str(output_dir / "checkpoint-500")


def test_scratch_mode_ignores_checkpoints(tmp_path: Path):
    config = make_config(tmp_path, resume_mode=MODE_SCRATCH)
    make_checkpoint(Path(config.training.output_dir), 750)

    plan = resolve_resume_plan(config)

    assert plan.mode == MODE_SCRATCH
    assert plan.start_step == 0
    assert plan.resume_from_checkpoint is None
    assert plan.warnings, "restarting on top of existing checkpoints must be flagged"


def test_no_checkpoint_starts_from_scratch(tmp_path: Path):
    plan = resolve_resume_plan(make_config(tmp_path))

    assert plan.mode == MODE_SCRATCH
    assert plan.start_step == 0


def test_legacy_initial_adapter_path_is_upgraded_to_the_best_tier(tmp_path: Path):
    external = make_checkpoint(tmp_path / "kaggle-input", 750)
    config = make_config(tmp_path, initial_adapter_path=str(external))

    plan = resolve_resume_plan(config)

    assert plan.mode == MODE_EXACT
    assert plan.start_step == 750
    assert any("deprecated" in note for note in plan.notes)


def test_dry_run_does_not_touch_disk(tmp_path: Path):
    config = make_config(tmp_path, optim="adamw_torch")
    checkpoint = make_checkpoint(Path(config.training.output_dir), 750, optim="paged_adamw_8bit")

    plan = resolve_resume_plan(config, dry_run=True)

    assert plan.mode == MODE_STATE
    assert (checkpoint / "optimizer.pt").exists()


def test_missing_explicit_checkpoint_fails_fast(tmp_path: Path):
    config = make_config(tmp_path, resume_from_checkpoint=str(tmp_path / "nope"))

    with pytest.raises(ResumeError, match="does not exist"):
        resolve_resume_plan(config)


def test_archive_moves_a_previous_run_aside(tmp_path: Path):
    output_dir = tmp_path / "outputs"
    make_checkpoint(output_dir, 750)

    archive = archive_existing_checkpoints(output_dir)

    assert archive is not None
    assert (archive / "checkpoint-750" / "adapter_model.safetensors").is_file()
    assert list_checkpoints(output_dir) == []


def test_banner_states_the_step_and_optimizer_status(tmp_path: Path):
    config = make_config(tmp_path, optim="adamw_torch")
    make_checkpoint(Path(config.training.output_dir), 750, optim="paged_adamw_8bit")

    banner = resolve_resume_plan(config).banner()

    assert "RESUME MODE: STATE" in banner
    assert "starting step   : 750" in banner
    assert "optimizer state : fresh" in banner
    assert "lr schedule     : restored" in banner
