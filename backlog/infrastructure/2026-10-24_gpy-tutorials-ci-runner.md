---
id: "2026-10-24_gpy-tutorials-ci-runner"
title: "Add nbclient runner and GitHub Actions for GPy tutorials"
status: "Completed"
priority: "High"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "infrastructure"
related_cips: ["0003"]
owner: "Neil Lawrence"
dependencies:
- "2026-10-24_gpy-tutorials-python3"
- "2026-10-24_gpy-tutorials-numpy-matplotlib-config"
- "2026-10-24_gpy-tutorials-matplotlib-backend"
tags:
- backlog
- gpy
- ci
---

# Task: Execute GPy tutorials in CI

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Add `scripts/run_gpy_tutorials.sh` (nbclient, `MPLBACKEND=Agg`, per-notebook timeout, climin skip policy) and a GitHub Actions workflow: Python 3.11, install GPy pinned to `gpy[plotting]==1.15.0` plus Jupyter (`nbclient`, `ipykernel`). Upload executed notebooks on failure. Point the README GPy tutorial section at the workflow badge. A second `execute-latest` job installs unpinned `gpy[plotting]`.

Skip `SVI.ipynb` and `optimizer-implementation.ipynb` when climin is not installed, with the skip documented. `index.ipynb` has no required code. Fail the job if a required notebook raises.

## Acceptance Criteria

- [x] Runner script executes `GPy/*.ipynb` with documented climin skip
- [x] GitHub Actions workflow pins GPy and runs the script on this repository
- [x] README GPy tutorial section shows the workflow badge
- [x] Job does not use Plotly Cloud credentials
- [x] `execute` installs `gpy[plotting]==1.15.0` from PyPI
- [x] `execute-latest` installs current PyPI `gpy[plotting]`

## Implementation Notes

Run with cwd such that `import GPy` resolves the library, not this repo's `GPy/` tutorial folder. Pin must not float on GPy `devel`. Failures should block merges that touch `GPy/`.

## Related

- CIP: 0003
- PRs:
- Documentation: `README.md`

## Progress Updates

### 2026-10-24

Task created as Ready after CIP-0003 was accepted.

Added `scripts/run_gpy_tutorials.py` / `.sh` and `.github/workflows/gpy-tutorials.yml` (Python 3.11, climin required). PR #24 `execute` went green against the GPy 1.15.0 git candidate. After v1.15.0 on PyPI, pin `execute` to `gpy[plotting]==1.15.0` and restore `execute-latest`. Marked Completed.
