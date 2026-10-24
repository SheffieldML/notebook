---
id: "2026-10-24_gpy-tutorials-colab-gpy-install"
title: "Install GPy from tutorial notebooks when it is missing"
status: "Completed"
priority: "Medium"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "features"
related_cips: ["0006"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- gpy
- colab
---

# Task: Colab GPy install check

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Insert a first code cell in each executable `GPy/*.ipynb` that imports GPy if present, otherwise `pip install gpy[plotting]>=1.15.0`. Add the same pattern for `pods`, `seaborn`, and `ipywidgets` only where those notebooks already import them. Skip `index.ipynb` and `config.ipynb`. Do not auto-install climin.

## Acceptance Criteria

- [x] Canonical ensure-GPy cell is the first code cell in each executable GPy tutorial
- [x] Extra ensure lines for pods / seaborn / ipywidgets where needed
- [x] CIP-0003 execute stays green (import-hit path; no pip in CI)

## Implementation Notes

Use `subprocess` + `sys.executable`, not `%pip`. Do not upgrade an already-importable GPy.

## Related

- CIP: 0006
- PRs:
- Documentation: `cip/cip0006.md`

## Progress Updates

### 2026-10-24

Task created as In Progress after CIP-0006 was accepted.

Inserted the ensure-GPy cell (plus pods/seaborn/ipywidgets where needed). Local execute: 19 passed (import-hit path).
