from __future__ import annotations

import os
from pathlib import Path

import torch


def is_main_process() -> bool:
    return int(os.environ.get("RANK", "0")) == 0


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def gpu_summary() -> list[dict[str, str | int | float]]:
    if not torch.cuda.is_available():
        return []
    devices = []
    for index in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(index)
        devices.append(
            {
                "index": index,
                "name": props.name,
                "total_memory_gb": round(props.total_memory / 1024**3, 2),
                "capability": f"{props.major}.{props.minor}",
            }
        )
    return devices

