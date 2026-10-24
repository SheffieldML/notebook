---
id: "2026-10-24_gpy-tutorials-numpy-matplotlib-config"
title: "Fix NumPy 2, matplotlib fmt, config.ipynb, and climin guards"
status: "Completed"
priority: "High"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "features"
related_cips: ["0001"]
owner: "Neil Lawrence"
dependencies:
- "2026-10-24_gpy-tutorials-python3"
tags:
- backlog
- gpy
- numpy2
---

# Task: NumPy 2, matplotlib, config, and climin guards

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Finish the CIP-0001 cell-content port beyond print/xrange:

1. `Integral_kernel.ipynb`: `"%0.2f" % speed` must use `.item()` (NumPy 2 ndarray is not a float).
2. `Poisson regression tutorial.ipynb`: `float(rates[r])` must use `.item()` or `float(np.asarray(x).reshape(-1)[0])`.
3. `heteroscedastic_regression.ipynb`: `fmt=None` → `fmt="none"`.
4. `config.ipynb`: move `defaults.cfg` / `installation.cfg` INI samples from code cells to markdown (or raw) so the notebook is not executed as Python.
5. `SVI.ipynb` and `optimizer-implementation.ipynb`: short markdown plus an early cell so `import climin` fails with a readable message that climin is an optional extra, not a GPy dependency.

## Acceptance Criteria

- [x] Integral and Poisson notebooks format/cast scalars via `.item()` (or equivalent)
- [x] Heteroscedastic `errorbar` uses `fmt="none"`
- [x] `config.ipynb` has no INI in code cells
- [x] Missing `climin` raises a clear ImportError naming the extra in both climin notebooks

## Implementation Notes

Do not add climin as a hard dependency. Skip policy for CI is CIP-0003.

## Related

- CIP: 0001
- PRs:
- Documentation: `GPy/config.ipynb`

## Progress Updates

### 2026-10-24

Task created as Ready after CIP-0001 was accepted.

Applied `.item()` in Integral and Poisson tutorials, `fmt="none"` in heteroscedastic errorbars, moved `config.ipynb` INI samples to markdown, and guarded `import climin` in SVI and optimizer notebooks. Also dropped a leftover indented fragment in `SVI.ipynb` so that plotting cell parses.
