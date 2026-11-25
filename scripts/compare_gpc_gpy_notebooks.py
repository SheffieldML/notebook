#!/usr/bin/env python3
"""Outline a GPy / GPc notebook pair for CIP-0007 comparison reviews.

Prints cell-type outlines, markdown-char counts, and crude API-token diffs.
Does not execute notebooks. See ``GPc/COMPARISON.md`` for the rubric.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

API_RE = re.compile(
    r"\b(?:GPy|gpc|m)\.[\w\.]+|\.plot\w*|\.optimize\w*|\.predict\w*"
    r"|likelihoods?\.\w+|kern\.\w+|models\.\w+"
)


def cell_src(cell: dict) -> str:
    src = cell.get("source", "")
    return src if isinstance(src, str) else "".join(src)


def outline(path: Path) -> tuple[list[tuple[int, str, int, str]], set[str], int]:
    nb = json.loads(path.read_text())
    rows: list[tuple[int, str, int, str]] = []
    apis: set[str] = set()
    md_chars = 0
    for i, cell in enumerate(nb["cells"]):
        text = cell_src(cell)
        first = text.strip().split("\n", 1)[0][:88] if text.strip() else ""
        rows.append((i, cell["cell_type"], len(text), first))
        if cell["cell_type"] == "markdown":
            md_chars += len(text)
        else:
            apis.update(API_RE.findall(text))
    return rows, apis, md_chars


def print_side(label: str, path: Path) -> tuple[set[str], int]:
    rows, apis, md_chars = outline(path)
    md = sum(1 for r in rows if r[1] == "markdown")
    code = sum(1 for r in rows if r[1] == "code")
    print(f"## {label}: {path}")
    print(f"cells={len(rows)} markdown={md} code={code} md_chars={md_chars}")
    for i, kind, n, first in rows:
        if kind == "markdown" and n > 40:
            print(f"  [{i:02d} md] {first}")
        elif kind == "code" and n > 0:
            print(f"  [{i:02d} code] ({n} chars) {first}")
    print()
    return apis, md_chars


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpy", type=Path, required=True)
    parser.add_argument("--gpc", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.gpy, args.gpc):
        if not path.is_file():
            print(f"missing: {path}", file=sys.stderr)
            return 1

    print("=" * 72)
    apis_gpy, md_gpy = print_side("GPy", args.gpy)
    apis_gpc, md_gpc = print_side("GPc", args.gpc)
    ratio = md_gpc / md_gpy if md_gpy else 0.0
    print(f"markdown char ratio GPc/GPy = {ratio:.2f}")
    only_gpy = sorted(apis_gpy - apis_gpc)
    only_gpc = sorted(apis_gpc - apis_gpy)
    print("API-ish tokens only in GPy:", only_gpy[:50])
    print("API-ish tokens only in GPc:", only_gpc[:50])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
