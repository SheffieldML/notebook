#!/usr/bin/env python3
"""Install packages from a central installs.yml profile.

Mirrors the intent of lamd's ``install_command`` package map
(``talk-macros-code.gpp``): one place to switch PyPI vs git sources.

Example::

    python scripts/install_from_yaml.py --profile gpy-tutorials
    python scripts/install_from_yaml.py --profile gpy-tutorials-latest --dry-run
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML required: python -m pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "installs.yml"


def load_profile(config_path: Path, profile: str | None) -> tuple[str, dict]:
    data = yaml.safe_load(config_path.read_text())
    if not isinstance(data, dict) or "profiles" not in data:
        raise SystemExit(f"{config_path}: expected top-level 'profiles' mapping")
    name = profile or data.get("default_profile")
    if not name:
        raise SystemExit(f"{config_path}: set default_profile or pass --profile")
    profiles = data["profiles"]
    if name not in profiles:
        known = ", ".join(sorted(profiles))
        raise SystemExit(f"Unknown profile {name!r}. Known: {known}")
    return name, profiles[name]


def installer_prefix() -> list[str]:
    if shutil.which("uv"):
        return ["uv", "pip", "install", "--python", sys.executable]
    return [sys.executable, "-m", "pip", "install"]


def resolve_specs(profile_body: dict) -> list[str]:
    packages = profile_body.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise SystemExit("Profile must contain a non-empty 'packages' mapping")
    specs: list[str] = []
    for key, spec in packages.items():
        if not isinstance(spec, str) or not spec.strip():
            raise SystemExit(f"Invalid spec for package {key!r}: {spec!r}")
        specs.append(spec.strip())
    return specs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"YAML file (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Profile name (default: default_profile in YAML)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the install command without running it",
    )
    args = parser.parse_args()

    if not args.config.is_file():
        raise SystemExit(f"Config not found: {args.config}")

    name, body = load_profile(args.config, args.profile)
    specs = resolve_specs(body)
    cmd = installer_prefix() + specs

    desc = (body.get("description") or "").strip()
    print(f"profile: {name}", flush=True)
    if desc:
        print(f"description: {desc}", flush=True)
    print("install:", " ".join(cmd), flush=True)

    if args.dry_run:
        return 0

    subprocess.check_call(cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
