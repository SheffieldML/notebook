---
id: "2026-11-25_gpc-gpy-notebook-comparison"
title: "GPy ↔ GPc notebook comparison program (CIP-0007)"
status: "Ready"
priority: "High"
created: "2026-11-25"
last_updated: "2026-11-25"
category: "documentation"
related_cips: ["0007"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- gpc
- gpy
- parity
- tutorials
---

# Task: GPy ↔ GPc notebook comparison program

> Living review of each GPy tutorial against its GPc twin: missing explanation, API mismatches, intentional shortenings.

## Description

CIP-0007 makes `GPc/` a parallel teaching surface. Wave reviews are recorded in [`GPc/COMPARISON.md`](../../GPc/COMPARISON.md). Use `scripts/compare_gpc_gpy_notebooks.py` for outlines, then edit the twin and update the findings table.

## Acceptance Criteria

- [x] Rubric + pairing map in `GPc/COMPARISON.md`
- [x] Wave 1 reviewed (`basic_gp`, `basic_kernels`, `sparse`, `classification`, `poisson`)
- [x] Classification + Poisson narrative gaps patched
- [x] Wave 2: coregionalization, GPLVM, BGPLVM, MRD, DeepGP
- [x] Wave 3: olympics / MLP / ExpQuad / weight-space
- [x] CIP-0007 non-goals list updated (Poisson now in subset)

## Implementation Notes

Prefer restoring *why* paragraphs over cloning GPy plot helpers. Tag each finding `gap` / `api` / `ok-short` / `defer`.

## Related

- CIP: 0007
- PRs: #38 (a10 pin + Poisson notebook)
- Documentation: [`GPc/COMPARISON.md`](../../GPc/COMPARISON.md)

## Progress Updates

### 2026-11-25

Program started on branch `gpc-gpy-notebook-comparison`. Wave 1 findings filed; classification and Poisson teaching beats restored.

### 2026-11-25 (later)

Wave 2 reviewed and narrative-patched: coregionalization, GPLVM, BGPLVM, MRD, DeepGP.

### 2026-11-25 (Wave 3)

Wave 3 reviewed and narrative-patched: olympic_marathon, mlp_olympic, expquad_regression, weightspace_ridge_1d. Waves 1–3 complete.
