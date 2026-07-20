#!/usr/bin/env bash
set -euo pipefail

uv run accelerate launch \
  --config_file configs/accelerate_single_gpu.yaml \
  train.py --config configs/train_qlora.yaml

