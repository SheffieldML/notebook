#!/usr/bin/env bash
# Execute GPc/*.ipynb (CIP-0007).
#
# gpc version is pinned by the caller (CI workflow or local env).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export MPLBACKEND="${MPLBACKEND:-Agg}"
export PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"

PYTHON="${PYTHON:-python3}"
exec "$PYTHON" "$ROOT/scripts/run_gpc_tutorials.py" "$@"
