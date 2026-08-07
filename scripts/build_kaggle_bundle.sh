#!/usr/bin/env bash
# Build the two archives that get uploaded to Kaggle as Datasets.
#
#   dist/kaggle-project-files.zip  -> the code (no venv, no git, no data)
#   dist/kaggle-dataset.zip        -> the training JSONL
#
# Kaggle unzips a dataset archive on mount, so the notebook sees the files
# directly under /kaggle/input/<dataset-slug>/.
set -euo pipefail

cd "$(dirname "$0")/.."
DIST=dist
# The task-tagged mixture the training config points at. Rebuild it with
# scripts/build_line_anchored.py then scripts/build_task_mixture.py before
# bundling, or Kaggle trains on a stale copy.
DATASET=${DATASET:-cleaned/task_mixture.jsonl}

rm -rf "$DIST"
mkdir -p "$DIST"

# --- code ----------------------------------------------------------------- #
# uv.lock is required: `uv sync` needs it to resolve the pinned versions.
zip -qr "$DIST/kaggle-project-files.zip" \
  pyproject.toml uv.lock README.md \
  train.py evaluate.py merge_lora.py inference.py export_onnx.py \
  src configs scripts tests \
  -x '*/__pycache__/*' '*.pyc' '*/.DS_Store' '*/.pytest_cache/*'

# --- data ----------------------------------------------------------------- #
test -f "$DATASET" || { echo "missing $DATASET" >&2; exit 1; }
zip -qj "$DIST/kaggle-dataset.zip" "$DATASET"

echo "Upload these two as separate Kaggle Datasets:"
ls -lh "$DIST"
echo
echo "Code archive contents (top level):"
unzip -l "$DIST/kaggle-project-files.zip" | awk '{print $4}' | grep -oE '^[^/]+/?' | sort -u | grep -v '^$'
