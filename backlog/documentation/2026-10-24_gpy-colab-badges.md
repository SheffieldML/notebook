---
id: "2026-10-24_gpy-colab-badges"
title: "Add Open in Colab badges to GPy tutorials"
status: "Completed"
priority: "Medium"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "documentation"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- gpy
- colab
---

# Task: Add Open in Colab badges to GPy tutorials

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Add an Open in Colab badge at the top of each GPy tutorial in this repository
(`GPy/*.ipynb`), opening that file from SheffieldML/notebook on branch `main`.
Also place a badge next to each tutorial link in `GPy/index.ipynb`.

## Acceptance Criteria

- [x] Every `GPy/*.ipynb` contains a Colab badge
- [x] `GPy/index.ipynb` lists a Colab badge beside each tutorial link
- [x] Filenames with spaces use `%20` in the Colab URL

## Implementation Notes

Use the default branch `main`. Do not invent new titles for code-first
notebooks; insert a leading markdown cell with the badge only.

## Related

- CIP: 0004

## Progress Updates

### 2026-10-24
Task created with CIP-0004.
Badges added on each GPy tutorial and beside index links.
