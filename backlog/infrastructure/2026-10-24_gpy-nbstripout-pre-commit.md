---
id: "2026-10-24_gpy-nbstripout-pre-commit"
title: "Strip GPy tutorial outputs with pre-commit nbstripout"
status: "Completed"
priority: "High"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "infrastructure"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- gpy
- pre-commit
---

# Task: Strip GPy tutorial outputs with pre-commit nbstripout

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Add `.pre-commit-config.yaml` running nbstripout 0.9.1 on `GPy/*.ipynb` in
this repository (the GPy tutorials), and strip outputs already present in
those files.

## Acceptance Criteria

- [x] `.pre-commit-config.yaml` exists and targets `^GPy/.*\.ipynb$`
- [x] `GPy/*.ipynb` code cells have empty outputs and null execution_count
- [x] README GPy tutorials section mentions `pre-commit install`

## Implementation Notes

Does not strip `lab_classes/`, `compbio/`, or `GPy-phil/`.

## Related

- CIP: 0004

## Progress Updates

### 2026-10-24
Task created with CIP-0004.
nbstripout 0.9.1 hook targets `GPy/*.ipynb`; tutorial outputs stripped.
