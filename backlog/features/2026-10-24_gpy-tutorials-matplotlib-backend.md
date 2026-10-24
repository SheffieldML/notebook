---
id: "2026-10-24_gpy-tutorials-matplotlib-backend"
title: "Switch GPy tutorial plotting from Plotly online to matplotlib"
status: "Completed"
priority: "High"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "features"
related_cips: ["0002"]
owner: "Neil Lawrence"
dependencies:
- "2026-10-24_gpy-tutorials-python3"
tags:
- backlog
- gpy
- plotting
---

# Task: Switch tutorial plotting to matplotlib

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

In `basic_gp.ipynb`, `models_basic.ipynb`, and `MagnificationFactor.ipynb`, replace `GPy.plotting.change_plotting_library('plotly')` with `'matplotlib'`. CIP-0002's default is matplotlib for all three so CI does not need Chart Studio or Plotly widgets. Remove nearby Chart Studio / `plotly.plotly` instructions if present.

## Acceptance Criteria

- [x] No `GPy/*.ipynb` cell calls `change_plotting_library('plotly')`
- [x] The three named notebooks select matplotlib
- [x] Nearby markdown does not tell readers to use Plotly Cloud / Chart Studio

## Implementation Notes

Do not patch GPy from this repository. GPy-side `plotly.plotly.iplot` and string marker sizes are a separate upstream issue.

## Related

- CIP: 0002
- PRs:
- Documentation: `GPy/basic_gp.ipynb`

## Progress Updates

### 2026-10-24

Task created as Ready after CIP-0002 was accepted.

Switched `basic_gp.ipynb`, `models_basic.ipynb`, and `MagnificationFactor.ipynb` from `'plotly'` to `'matplotlib'`. No tutorial markdown required Chart Studio.
