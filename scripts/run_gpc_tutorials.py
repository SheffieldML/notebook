#!/usr/bin/env python3
"""Execute GPc tutorial notebooks (CIP-0007).

Runs every ``GPc/*.ipynb`` with nbclient and ``MPLBACKEND=Agg``. Cwd is the
notebook directory so ``GPc`` as a folder name does not shadow the ``gpc``
package (same pattern as CIP-0003 for GPy).

Skip policy: ``index.ipynb`` is markdown-only and is skipped.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import traceback
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL_DIR = ROOT / "GPc"
SKIP = frozenset({"index.ipynb"})
DEFAULT_TIMEOUT = 900

# Keep OpenBLAS single-threaded in CI / nbclient (GPc wheel docs).
BLAS_PREAMBLE = """\
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
"""


def execute_notebook(path: Path, timeout: int, output_dir: Path | None) -> None:
    nb = nbformat.read(path, as_version=4)
    nb.cells.insert(0, nbformat.v4.new_code_cell(BLAS_PREAMBLE))
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
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

    notebooks = sorted(TUTORIAL_DIR.glob("*.ipynb"))
    if not notebooks:
        print(f"No notebooks found in {TUTORIAL_DIR}", file=sys.stderr)
        return 1

    try:
        gpc_info = subprocess.check_output(
            [
                sys.executable,
                "-c",
                "import gpc; print(getattr(gpc, '__version__', '?'), gpc.__file__)",
            ],
            cwd=str(TUTORIAL_DIR),
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover - environment misconfigured
        gpc_info = f"unavailable ({exc})"

    print(f"python: {sys.executable}", flush=True)
    print(f"gpc: {gpc_info}", flush=True)
    print(f"executing {len(notebooks)} notebooks from {TUTORIAL_DIR}", flush=True)

    failed: list[str] = []
    skipped: list[str] = []
    passed: list[str] = []

    for path in notebooks:
        if path.name in SKIP:
            print(f"SKIP {path.name} (index / markdown only)", flush=True)
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
    if not passed:
        print("No executable GPc notebooks ran", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
