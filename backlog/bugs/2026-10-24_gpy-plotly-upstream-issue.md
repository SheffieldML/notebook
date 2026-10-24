---
id: "2026-10-24_gpy-plotly-upstream-issue"
title: "File GPy issue for Plotly online iplot and string marker sizes"
status: "Completed"
priority: "Medium"
created: "2026-10-24"
last_updated: "2026-10-24"
category: "bugs"
related_cips: ["0002"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- gpy
- plotly
---

# Task: File GPy Plotly backend issue

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Open an issue on SheffieldML/GPy listing the two blockers that remain even after notebooks stop calling `'plotly'`:

1. `GPy/plotting/plotly_dep/plot_definitions.py` — `PlotlyPlotsOnline` uses `plotly.plotly.iplot` / `.plot` (Chart Studio is a separate package).
2. `GPy/plotting/plotly_dep/defaults.py` — `size="5"` / `size="0"` strings; Plotly 7 rejects `marker.size` as a string.
3. `change_plotting_library('plotly')` aliases the online class.

Link the issue from CIP-0002. Do not patch GPy from this repository.

## Acceptance Criteria

- [x] GitHub issue exists on SheffieldML/GPy covering iplot and string marker sizes
- [x] CIP-0002 References section links to that issue

## Implementation Notes

Track as a GPy issue or CIP against SheffieldML/GPy. Notebook-side workaround is matplotlib (sibling task).

## Related

- CIP: 0002
- Issue: [SheffieldML/GPy#1243](https://github.com/SheffieldML/GPy/issues/1243)
- PRs:
- Documentation: SheffieldML/GPy plotting backends

## Progress Updates

### 2026-10-24

Task created as Ready after CIP-0002 was accepted.

Opened https://github.com/SheffieldML/GPy/issues/1243 and linked it from CIP-0002.
