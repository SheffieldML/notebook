#!/usr/bin/env python3
"""Install packages from installs.yml profiles + the shared lamd catalog.

Catalog (defaults) lives in lawrennd/lamd ``lamd/installs/packages.yml``.
This repo only declares profiles, pins, and temporary overrides (CIP-0008).

Example::

    python scripts/install_from_yaml.py --profile gpy-tutorials
    python scripts/install_from_yaml.py --profile gpy-tutorials-latest --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping
from urllib.error import URLError
from urllib.request import urlopen

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML required: python -m pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "installs.yml"
DEFAULT_CATALOG_URL = (
    "https://raw.githubusercontent.com/lawrennd/lamd/main/lamd/installs/packages.yml"
)
DEFAULT_CATALOG_JSON_URL = (
    "https://raw.githubusercontent.com/lawrennd/lamd/main/lamd/installs/packages.json"
)


def _packages_from_data(data: Any) -> dict[str, str]:
    if not isinstance(data, dict):
        raise SystemExit("catalog root must be a mapping")
    packages = data.get("packages", data)
    if not isinstance(packages, dict) or not packages:
        raise SystemExit("catalog must contain a non-empty 'packages' mapping")
    out: dict[str, str] = {}
    for key, spec in packages.items():
        if not isinstance(key, str) or not isinstance(spec, str) or not spec.strip():
            raise SystemExit(f"invalid catalog entry: {key!r}: {spec!r}")
        out[key] = spec.strip()
    return out


def load_catalog(config: Mapping[str, Any]) -> dict[str, str]:
    """Load shared catalog: env → catalog.local → catalog.url → remote defaults."""
    errors: list[str] = []

    env_yml = os.environ.get("LAMD_PACKAGES_YML")
    if env_yml:
        path = Path(env_yml)
        try:
            return _packages_from_data(yaml.safe_load(path.read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"LAMD_PACKAGES_YML ({path}): {exc}")

    env_json = os.environ.get("LAMD_PACKAGES_JSON")
    if env_json:
        path = Path(env_json)
        try:
            return _packages_from_data(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"LAMD_PACKAGES_JSON ({path}): {exc}")

    catalog_cfg = config.get("catalog") or {}
    if not isinstance(catalog_cfg, dict):
        raise SystemExit("'catalog' must be a mapping when present")

    local = catalog_cfg.get("local")
    if local:
        path = Path(local)
        if not path.is_absolute():
            path = ROOT / path
        if path.is_file():
            if path.suffix.lower() == ".json":
                return _packages_from_data(json.loads(path.read_text(encoding="utf-8")))
            return _packages_from_data(yaml.safe_load(path.read_text(encoding="utf-8")))
        errors.append(f"catalog.local not found: {path}")

    url = catalog_cfg.get("url") or DEFAULT_CATALOG_URL
    try:
        with urlopen(url, timeout=10) as response:  # noqa: S310 — curated URL
            text = response.read().decode("utf-8")
        if url.endswith(".json"):
            return _packages_from_data(json.loads(text))
        return _packages_from_data(yaml.safe_load(text))
    except (URLError, TimeoutError, ValueError) as exc:
        errors.append(f"catalog.url ({url}): {exc}")

    try:
        with urlopen(DEFAULT_CATALOG_JSON_URL, timeout=10) as response:  # noqa: S310
            return _packages_from_data(json.loads(response.read().decode("utf-8")))
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"fallback JSON catalog: {exc}")

    detail = "; ".join(errors) if errors else "no sources"
    print(
        f"warning: shared package catalog unavailable ({detail}); "
        "resolving from pins/overrides/bare names only",
        file=sys.stderr,
        flush=True,
    )
    return {}


def load_config(config_path: Path) -> dict[str, Any]:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "profiles" not in data:
        raise SystemExit(f"{config_path}: expected top-level 'profiles' mapping")
    return data


def load_profile(config: Mapping[str, Any], profile: str | None) -> tuple[str, dict]:
    name = profile or config.get("default_profile")
    if not name:
        raise SystemExit("set default_profile or pass --profile")
    profiles = config["profiles"]
    if name not in profiles:
        known = ", ".join(sorted(profiles))
        raise SystemExit(f"Unknown profile {name!r}. Known: {known}")
    body = profiles[name]
    if not isinstance(body, dict):
        raise SystemExit(f"profile {name!r} must be a mapping")
    return name, body


def repo_overrides(config: Mapping[str, Any]) -> dict[str, str]:
    block = config.get("overrides") or {}
    if not isinstance(block, dict):
        raise SystemExit("'overrides' must be a mapping")
    packages = block.get("packages", block if block else {})
    if not packages:
        return {}
    if not isinstance(packages, dict):
        raise SystemExit("overrides.packages must be a mapping")
    out: dict[str, str] = {}
    for key, spec in packages.items():
        if not isinstance(spec, str) or not spec.strip():
            raise SystemExit(f"invalid override for {key!r}: {spec!r}")
        out[key] = spec.strip()
    return out


def resolve_specs(
    profile_body: Mapping[str, Any],
    catalog: Mapping[str, str],
    overrides: Mapping[str, str],
) -> list[str]:
    """Resolve profile package list/dict against catalog, overrides, and pins."""
    pins = profile_body.get("pins") or {}
    if pins and not isinstance(pins, dict):
        raise SystemExit("profile 'pins' must be a mapping")

    packages = profile_body.get("packages")
    if packages is None:
        raise SystemExit("Profile must contain 'packages'")

    # Legacy: full name→spec mapping in the profile (no catalog lookup).
    if isinstance(packages, dict):
        specs: list[str] = []
        for key, spec in packages.items():
            if not isinstance(spec, str) or not spec.strip():
                raise SystemExit(f"Invalid spec for package {key!r}: {spec!r}")
            specs.append(spec.strip())
        return specs

    if not isinstance(packages, list) or not packages:
        raise SystemExit("Profile 'packages' must be a non-empty list (or legacy mapping)")

    specs = []
    for name in packages:
        if not isinstance(name, str) or not name.strip():
            raise SystemExit(f"Invalid package name: {name!r}")
        name = name.strip()
        if name in pins:
            spec = pins[name]
        elif name in overrides:
            spec = overrides[name]
        elif name in catalog:
            spec = catalog[name]
        else:
            spec = name
        if not isinstance(spec, str) or not spec.strip():
            raise SystemExit(f"Invalid resolved spec for {name!r}: {spec!r}")
        specs.append(spec.strip())
    return specs


def installer_prefix() -> list[str]:
    if shutil.which("uv"):
        return ["uv", "pip", "install", "--python", sys.executable]
    return [sys.executable, "-m", "pip", "install"]


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

    config = load_config(args.config)
    name, body = load_profile(config, args.profile)
    catalog = load_catalog(config)
    overrides = repo_overrides(config)
    specs = resolve_specs(body, catalog, overrides)
    cmd = installer_prefix() + specs

    desc = (body.get("description") or "").strip()
    print(f"profile: {name}", flush=True)
    if desc:
        print(f"description: {desc}", flush=True)
    print(f"catalog packages: {len(catalog)}", flush=True)
    print("install:", " ".join(cmd), flush=True)

    if args.dry_run:
        return 0

    subprocess.check_call(cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
