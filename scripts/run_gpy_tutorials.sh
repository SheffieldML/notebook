#!/usr/bin/env bash
# Execute GPy/*.ipynb (CIP-0003).
#
# Skip SVI.ipynb and optimizer-implementation.ipynb when climin is not
# installed. GPy version is pinned by the caller (CI workflow or local env).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export MPLBACKEND="${MPLBACKEND:-Agg}"
export PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}"

# Prefer the caller's interpreter so a conda/venv env is used locally.
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" "$ROOT/scripts/run_gpy_tutorials.py" "$@"
