#!/usr/bin/env bash
# Execute GPy/*.ipynb (CIP-0003).
#
# Skip SVI.ipynb and optimizer-implementation.ipynb when climin is not
# installed. GPy version is pinned by the caller (CI workflow or local env).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export MPLBACKEND="${MPLBACKEND:-Agg}"
export PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}"

exec python3 "$ROOT/scripts/run_gpy_tutorials.py" "$@"
