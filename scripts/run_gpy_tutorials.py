#!/usr/bin/env python3
"""Execute GPy tutorial notebooks (CIP-0003).

Runs every ``GPy/*.ipynb`` with nbclient, ``MPLBACKEND=Agg``, and the notebook
directory as cwd so ``import GPy`` resolves the library, not this folder.

Skip policy: ``SVI.ipynb`` and ``optimizer-implementation.ipynb`` are skipped
when climin is not installed (optional extra, not a GPy dependency).
"""
from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL_DIR = ROOT / "GPy"
CLIMIN_OPTIONAL = frozenset({"SVI.ipynb", "optimizer-implementation.ipynb"})
DEFAULT_TIMEOUT = 900


def climin_available() -> bool:
    try:
        import climin  # noqa: F401
    except ImportError:
        return False
    return True


def execute_notebook(path: Path, timeout: int, output_dir: Path | None) -> None:
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    )
    try:
        client.execute()
    except CellExecutionError:
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            failed = output_dir / path.name
            nbformat.write(nb, failed)
            print(f"  wrote executed notebook to {failed}", file=sys.stderr)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="Per-notebook timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write executed notebooks here on failure (CI artifact dir)",
    )
    args = parser.parse_args()

    os.environ.setdefault("MPLBACKEND", "Agg")

    notebooks = sorted(TUTORIAL_DIR.glob("*.ipynb"))
    if not notebooks:
        print(f"No notebooks found in {TUTORIAL_DIR}", file=sys.stderr)
        return 1

    have_climin = climin_available()
    print(f"climin installed: {have_climin}", flush=True)
    print(
        f"GPy pin check happens in the environment; executing {len(notebooks)} notebooks",
        flush=True,
    )

    failed: list[str] = []
    skipped: list[str] = []
    passed: list[str] = []

    for path in notebooks:
        if path.name in CLIMIN_OPTIONAL and not have_climin:
            print(f"SKIP {path.name} (climin not installed; optional extra)", flush=True)
            skipped.append(path.name)
            continue
        print(f"RUN  {path.name}", flush=True)
        try:
            execute_notebook(path, timeout=args.timeout, output_dir=args.output_dir)
        except Exception as exc:
            print(f"FAIL {path.name}: {exc}", file=sys.stderr, flush=True)
            traceback.print_exc()
            failed.append(path.name)
        else:
            print(f"PASS {path.name}", flush=True)
            passed.append(path.name)

    print(flush=True)
    print(f"passed={len(passed)} skipped={len(skipped)} failed={len(failed)}", flush=True)
    if skipped:
        print("skipped:", ", ".join(skipped), flush=True)
    if failed:
        print("failed:", ", ".join(failed), file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
