from __future__ import annotations

import shutil
from pathlib import Path

import torch
from peft import get_peft_model_state_dict
from safetensors.torch import load_file

from qwen_cpp_review.resume import MODE_ADAPTER
from qwen_cpp_review.resume import find_latest_checkpoint as _find_latest_checkpoint


def find_latest_checkpoint(output_dir: str | Path, tier: str = MODE_ADAPTER) -> str | None:
    """Newest checkpoint that is complete enough to be used for ``tier``.

    Skips directories left half-written by an interrupted save, which is how a
    preempted session normally ends.
    """
    return _find_latest_checkpoint(output_dir, tier=tier)


def save_current_adapter_pth(model, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    torch.save(get_peft_model_state_dict(model), target)


def convert_adapter_checkpoint_to_pth(checkpoint_dir: str | Path, path: str | Path) -> None:
    checkpoint = Path(checkpoint_dir)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    safetensors_path = checkpoint / "adapter_model.safetensors"
    bin_path = checkpoint / "adapter_model.bin"
    if safetensors_path.exists():
        state_dict = load_file(str(safetensors_path))
    elif bin_path.exists():
        state_dict = torch.load(bin_path, map_location="cpu")
    else:
        raise FileNotFoundError(f"No adapter weights found in {checkpoint}")
    torch.save(state_dict, target)


def copy_checkpoint_dir(source: str | Path, destination: str | Path) -> None:
    src = Path(source)
    dst = Path(destination)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
