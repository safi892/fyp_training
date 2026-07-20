#!/usr/bin/env bash
set -euo pipefail

NUM_PROCESSES="${NUM_PROCESSES:-2}"

uv run accelerate launch \
  --config_file configs/accelerate_multi_gpu.yaml \
  --num_processes "${NUM_PROCESSES}" \
  train.py --config configs/train_qlora.yaml

