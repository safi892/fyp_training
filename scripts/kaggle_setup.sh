#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade uv
uv sync --extra gpu --extra export --extra dev
