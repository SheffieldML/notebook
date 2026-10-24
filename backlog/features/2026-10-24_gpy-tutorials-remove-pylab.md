---
id: "2026-10-24_gpy-tutorials-remove-pylab"
title: "Replace pylab in GPy tutorials with matplotlib.pyplot"
status: "Completed"
priority: "Medium"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "features"
related_cips: ["0005"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- gpy
- plotting
---

# Task: Replace pylab in GPy tutorials

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Remove `pylab`, `%pylab inline`, and `%matplotlib inline` from `GPy/*.ipynb`. Use `matplotlib.pyplot as plt` and qualify star-imported names in `sampling_hmc.ipynb`.

## Acceptance Criteria

- [x] No `pylab` or `%matplotlib` in `GPy/*.ipynb`
- [x] `sampling_hmc.ipynb` uses `np` / `plt` instead of `from pylab import *`
- [x] CIP-0003 execute still passes

## Implementation Notes

Do not add `%matplotlib inline`. GPy `plotting_library().figure` / `show` calls stay.

## Related

- CIP: 0005
- PRs:
- Documentation: `cip/cip0005.md`

## Progress Updates

### 2026-10-24

Task created as In Progress after CIP-0005 was accepted.

Replaced pylab with pyplot, removed matplotlib inline magics, and added `import numpy as np` in the coregionalized tutorial (it previously came from `%pylab`). Local execute: 19 passed.
