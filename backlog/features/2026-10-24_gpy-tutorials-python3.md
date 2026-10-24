---
id: "2026-10-24_gpy-tutorials-python3"
title: "Port GPy tutorial cells to Python 3 print/xrange and python3 kernelspec"
status: "Ready"
priority: "High"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "features"
related_cips: ["0001"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- gpy
- python3
---

# Task: Port GPy tutorials to Python 3 syntax

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Update `GPy/*.ipynb` source cells so they are valid Python 3: convert `print` statements and `xrange` to `print()` / `range`, and set every tutorial `kernelspec` to `python3`. Do not rewrite the teaching narrative.

Notebooks with Python 2 `print` / `xrange` (CIP-0001 inventory): `GPyCrashCourse`, `basic_classification`, `basic_kernels`, `coregionalized_regression_tutorial`, `models_basic`, `multiple outputs`, `sparse_gp_regression`, `sampling_hmc`, `heteroscedastic_regression`. Apply kernelspec `python3` to every file in `GPy/`.

## Acceptance Criteria

- [ ] No code cell in `GPy/*.ipynb` uses Python 2 `print` or `xrange`
- [ ] Every `GPy/*.ipynb` kernelspec name is `python3`
- [ ] Teaching markdown is unchanged except where it quotes the old `print` syntax as a command to type

## Implementation Notes

Mechanical port only. IPython magics (`%matplotlib`, `%pylab`, `?` help) must be left intact. Prefer lib2to3 print/xrange fixers on cell source with magics stripped and restored.

## Related

- CIP: 0001
- PRs:
- Documentation: `GPy/index.ipynb`

## Progress Updates

### 2026-10-24

Task created as Ready after CIP-0001 was accepted.
