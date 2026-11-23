#!/usr/bin/env python3
"""Curate 2011 F1 practice/qualifying CSVs for CIP-0005.

Offline generator for pods / datasets_mirror. Reads local Timing Data and
writes UTF-8 CSVs of **all laps** (not fastest-only).

Usage (from notebook repo root, with scipy available)::

    .venv-gpc-smoke/bin/python scripts/curate_f1_2011_practice_qualifying.py
"""

from __future__ import annotations

import csv
import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.io as sio

ROOT = Path(__file__).resolve().parents[1]
TIMING_ROOT = ROOT / "Timing Data"
OUT_ROOT = ROOT / "datasets" / "f1_2011_practice_qualifying"

# Pit-lane order teams for 2011 (matches darwinMatlab num2teamNum / teamNum2teamName).
TEAM_MAX_NUM = (2, 4, 6, 8, 10, 12, 15, 17, 19, 21, 23, 25)
TEAM_NAMES = {
    1: "Red Bull-Renault",
    2: "McLaren-Mercedes",
    3: "Ferrari",
    4: "Mercedes",
    5: "Lotus Renault",
    6: "Williams-Cosworth",
    7: "Force India-Mercedes",
    8: "Sauber-Ferrari",
    9: "Toro Rosso-Ferrari",
    10: "Team Lotus",
    11: "HRT-Cosworth",
    12: "Virgin Cosworth",
}

# Qualifying windows from darwinMatlab/sessionTimes.m (local clock of the event).
SESSION_TIMES: Dict[str, Dict[str, Tuple[str, str]]] = {
    "Australia": {
        "Q1": ("17:00:00", "17:25:00"),
        "Q2": ("17:30:00", "17:45:00"),
        "Q3": ("17:50:00", "18:05:00"),
    },
    "Malaysia": {
        "Q1": ("16:00:00", "16:26:00"),
        "Q2": ("16:30:00", "16:50:00"),
        "Q3": ("17:00:00", "17:10:00"),
    },
    "China": {
        "Q1": ("14:00:00", "14:25:00"),
        "Q2": ("14:26:00", "14:55:00"),
        "Q3": ("15:00:00", "15:15:00"),
    },
    "Turkey": {
        "Q1": ("14:00:00", "14:25:00"),
        "Q2": ("14:29:00", "14:50:00"),
        "Q3": ("14:51:00", "15:10:00"),
    },
    "Spain": {
        "Q1": ("14:00:00", "14:25:00"),
        "Q2": ("14:29:00", "14:45:00"),
        "Q3": ("14:50:00", "15:10:00"),
    },
    "Monaco": {
        "Q1": ("14:00:00", "14:25:00"),
        "Q2": ("14:29:00", "14:50:00"),
        "Q3": ("14:51:00", "16:00:00"),
    },
    "Canada": {
        "Q1": ("13:00:00", "13:25:00"),
        "Q2": ("13:29:00", "13:50:00"),
        "Q3": ("13:51:00", "14:05:00"),
    },
    "Europe": {
        "Q1": ("14:00:00", "14:25:00"),
        "Q2": ("14:29:00", "14:55:00"),
        "Q3": ("14:56:00", "15:10:00"),
    },
    "GreatBritain": {
        "Q1": ("13:00:00", "13:25:00"),
        "Q2": ("13:30:00", "13:45:00"),
        "Q3": ("13:50:00", "14:00:00"),
    },
}

SESSION_FILE = {
    "FP1": "First Practice Session Sector Analysis.mat",
    "FP2": "Second Practice Session Sector Analysis.mat",
    "FP3": "Third Practice Session Sector Analysis.mat",
    "Q": "Qualifying Session Sector Analysis.mat",
}

LAP_FIELDS = (
    "driver_number",
    "abbreviation",
    "driver_name",
    "team",
    "team_index",
    "lap",
    "lap_time_s",
    "lap_time_string",
    "pit_stop",
    "sector1_s",
    "sector2_s",
    "sector3_s",
    "speed1_kph",
    "speed2_kph",
    "speed3_kph",
    "tod_hour",
    "tod_minute",
    "tod_second",
    "tod_millisecond",
    "tod_s",
    "q_segment",
    "q_window_source",
)


def hms_to_days(hms: str) -> float:
    h, m, s = hms.split(":")
    return (int(h) * 3600 + int(m) * 60 + float(s)) / 86400.0


def _as_1d(value) -> np.ndarray:
    return np.atleast_1d(np.asarray(value))


def _cell_str(value, index: int) -> str:
    arr = _as_1d(value)
    if index >= arr.size:
        return ""
    item = arr[index]
    if item is None or (isinstance(item, float) and math.isnan(item)):
        return ""
    return str(item)


def _num_or_empty(value) -> str:
    if value is None:
        return ""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return ""
    if not np.isfinite(f) or f == 0.0:
        return ""
    return f"{f:.3f}".rstrip("0").rstrip(".") if "." in f"{f:.3f}" else str(int(f))


def lap_tod_seconds(driver) -> np.ndarray:
    return (
        _as_1d(driver.TimeHour).astype(float) * 3600.0
        + _as_1d(driver.TimeMinutes).astype(float) * 60.0
        + _as_1d(driver.TimeSeconds).astype(float)
        + _as_1d(driver.TimeMilliSeconds).astype(float) / 1000.0
    )


def driver_number_to_team(number: int) -> Tuple[int, str]:
    """Map FIA car number to 2011 pit-lane team index (darwinMatlab num2teamNum)."""
    if number == 13 or number < 1 or number > 25:
        raise ValueError(f"Unknown driver number {number}")
    for team_idx, max_num in enumerate(TEAM_MAX_NUM, start=1):
        if number <= max_num:
            return team_idx, TEAM_NAMES[team_idx]
    raise ValueError(f"Unknown driver number {number}")


def load_sector_analysis(path: Path):
    data = sio.loadmat(str(path), struct_as_record=False, squeeze_me=True)
    sa = data["SectorAnalysis"]
    if not isinstance(sa, np.ndarray):
        sa = np.array([sa])
    return sa


def infer_q_windows(sa) -> Optional[Dict[str, Tuple[float, float]]]:
    """Infer Q1/Q2/Q3 windows from gaps in clean-lap timestamps (seconds of day)."""
    stamps: List[float] = []
    for driver in sa:
        tod = lap_tod_seconds(driver)
        pit = _as_1d(driver.PitStop).astype(bool)
        lap_times = _as_1d(driver.LapTime).astype(float)
        for i, t in enumerate(tod):
            if pit[i] or not np.isfinite(lap_times[i]) or lap_times[i] <= 0:
                continue
            if lap_times[i] > 200:
                continue
            stamps.append(float(t))
    if len(stamps) < 10:
        return None
    stamps = sorted(stamps)
    gaps = [stamps[i + 1] - stamps[i] for i in range(len(stamps) - 1)]
    break_idxs = [i for i, g in enumerate(gaps) if g >= 180.0]
    if len(break_idxs) < 2:
        return None
    ranked = sorted(break_idxs, key=lambda i: gaps[i], reverse=True)[:2]
    ranked.sort()
    b1, b2 = ranked[0], ranked[1]
    return {
        "Q1": (stamps[0] - 30.0, stamps[b1] + 30.0),
        "Q2": (stamps[b1 + 1] - 30.0, stamps[b2] + 30.0),
        "Q3": (stamps[b2 + 1] - 30.0, stamps[-1] + 60.0),
    }


def q_windows_for_race(
    grand_prix: str, sa
) -> Tuple[Optional[Dict[str, Tuple[float, float]]], str]:
    if grand_prix in SESSION_TIMES:
        windows = {
            key: (hms_to_days(start) * 86400.0, hms_to_days(finish) * 86400.0)
            for key, (start, finish) in SESSION_TIMES[grand_prix].items()
        }
        return windows, "sessionTimes.m"
    inferred = infer_q_windows(sa)
    if inferred is not None:
        return inferred, "inferred_gaps"
    return None, "none"


def label_q_segment(
    tod_s: float, windows: Optional[Dict[str, Tuple[float, float]]]
) -> str:
    if windows is None or not np.isfinite(tod_s):
        return ""
    for key in ("Q1", "Q2", "Q3"):
        start, end = windows[key]
        if start < tod_s < end:
            return key
    return ""


def resolve_session_dir(race_dir: Path, session: str) -> Optional[Path]:
    direct = race_dir / session
    nested = race_dir / "Timing" / session
    for candidate in (direct, nested):
        mat = candidate / SESSION_FILE[session]
        if mat.is_file():
            return candidate
    return None


@dataclass
class RaceMeta:
    folder: str
    grand_prix: str
    date_code: str


def discover_races(timing_root: Path) -> List[RaceMeta]:
    races: List[RaceMeta] = []
    for path in sorted(timing_root.iterdir()):
        if not path.is_dir() or "_" not in path.name:
            continue
        date_code, gp = path.name.split("_", 1)
        races.append(RaceMeta(folder=path.name, grand_prix=gp, date_code=date_code))
    return races


def all_lap_rows(
    sa,
    windows: Optional[Dict[str, Tuple[float, float]]] = None,
    window_source: str = "",
) -> List[dict]:
    """One CSV row per recorded lap for every driver."""
    rows: List[dict] = []
    for driver in sa:
        number = int(driver.NumberFIA)
        team_index, team = driver_number_to_team(number)
        abbreviation = str(driver.NomeFIA)
        driver_name = str(driver.Nome)
        lap_times = _as_1d(driver.LapTime).astype(float)
        pit = _as_1d(driver.PitStop).astype(bool)
        tod = lap_tod_seconds(driver)
        hours = _as_1d(driver.TimeHour)
        minutes = _as_1d(driver.TimeMinutes)
        seconds = _as_1d(driver.TimeSeconds)
        millis = _as_1d(driver.TimeMilliSeconds)
        sectors = np.atleast_2d(np.asarray(driver.Sectors, dtype=float))
        speeds = np.atleast_2d(np.asarray(driver.Speed, dtype=float))
        if sectors.ndim == 1:
            sectors = sectors.reshape(1, -1)
        if speeds.ndim == 1:
            speeds = speeds.reshape(1, -1)
        n = lap_times.size
        for i in range(n):
            tod_s = float(tod[i]) if i < tod.size else float("nan")
            srow = sectors[i] if i < sectors.shape[0] else (np.nan, np.nan, np.nan)
            krow = speeds[i] if i < speeds.shape[0] else (np.nan, np.nan, np.nan)
            lt = float(lap_times[i])
            rows.append(
                {
                    "driver_number": number,
                    "abbreviation": abbreviation,
                    "driver_name": driver_name,
                    "team": team,
                    "team_index": team_index,
                    "lap": i + 1,
                    "lap_time_s": "" if (not np.isfinite(lt) or lt == 0.0) else round(lt, 3),
                    "lap_time_string": _cell_str(driver.LapTimeString, i),
                    "pit_stop": int(bool(pit[i])) if i < pit.size else 0,
                    "sector1_s": _num_or_empty(srow[0] if len(srow) > 0 else None),
                    "sector2_s": _num_or_empty(srow[1] if len(srow) > 1 else None),
                    "sector3_s": _num_or_empty(srow[2] if len(srow) > 2 else None),
                    "speed1_kph": _num_or_empty(krow[0] if len(krow) > 0 else None),
                    "speed2_kph": _num_or_empty(krow[1] if len(krow) > 1 else None),
                    "speed3_kph": _num_or_empty(krow[2] if len(krow) > 2 else None),
                    "tod_hour": int(hours[i]) if i < hours.size else "",
                    "tod_minute": int(minutes[i]) if i < minutes.size else "",
                    "tod_second": int(seconds[i]) if i < seconds.size else "",
                    "tod_millisecond": int(millis[i]) if i < millis.size else "",
                    "tod_s": "" if not np.isfinite(tod_s) else round(tod_s, 3),
                    "q_segment": label_q_segment(tod_s, windows),
                    "q_window_source": window_source if windows is not None else "",
                }
            )
    rows.sort(key=lambda r: (r["driver_number"], r["lap"]))
    return rows


def write_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def curate_race(meta: RaceMeta, out_root: Path) -> dict:
    race_dir = TIMING_ROOT / meta.folder
    out_dir = out_root / meta.grand_prix
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files: Dict[str, str] = {}
    n_laps: Dict[str, int] = {}
    q_window_source = ""

    # Qualifying windows from Q session (also stamped on Q lap rows).
    q_dir = resolve_session_dir(race_dir, "Q")
    windows = None
    if q_dir is not None:
        sa_q_for_windows = load_sector_analysis(q_dir / SESSION_FILE["Q"])
        windows, q_window_source = q_windows_for_race(meta.grand_prix, sa_q_for_windows)

    for session in ("FP1", "FP2", "FP3", "Q"):
        sess_dir = resolve_session_dir(race_dir, session)
        if sess_dir is None:
            continue
        sa = load_sector_analysis(sess_dir / SESSION_FILE[session])
        if session == "Q":
            rows = all_lap_rows(sa, windows=windows, window_source=q_window_source)
        else:
            rows = all_lap_rows(sa)
            for row in rows:
                row["q_segment"] = ""
                row["q_window_source"] = ""
        fname = f"{session}_laps.csv"
        write_csv(out_dir / fname, rows, LAP_FIELDS)
        files[session] = fname
        n_laps[session] = len(rows)

    return {
        "grand_prix": meta.grand_prix,
        "folder": meta.folder,
        "date_code": meta.date_code,
        "files": files,
        "n_laps": n_laps,
        "q_window_source": q_window_source,
    }


README = """# f1_2011_practice_qualifying

Full per-lap numeric tables for 2011 Formula 1 practice and qualifying,
curated for research and teaching demos of practice→qualifying prediction.

## Contents

Per grand prix directory (UTF-8 CSV):

- `FP1_laps.csv`, `FP2_laps.csv`, `FP3_laps.csv`, `Q_laps.csv` — **every**
  recorded lap for every driver in that session (including pit laps and
  incomplete times).

Columns include driver identity, team, lap index, `lap_time_s`, sector times,
sector speeds, time-of-day, and `pit_stop`. Qualifying rows also carry
`q_segment` (`Q1`/`Q2`/`Q3` when windows are known) and `q_window_source`.

Empty `lap_time_s` means no flying-lap time was recorded for that row (common
for the first out-lap marker). Downstream loaders can filter with
`pit_stop == 0` and a finite `lap_time_s` to recover fastest-lap summaries.

## Provenance

- Derived from 2011 Formula 1 weekend timing used in University of Sheffield
  research on qualifying cut-off prediction.
- This pack redistributes curated numeric summaries for research and teaching.
- Not an official FIA or Formula 1 product.

## Qualifying windows

Where historical session clocks are known for a race,
`q_window_source=sessionTimes.m`. For later 2011 rounds without those clocks,
windows are inferred from multi-minute gaps in flying-lap timestamps
(`inferred_gaps`). See `manifest.json`.

## Generation

Offline curation script (not shipped in pods):
`notebook/scripts/curate_f1_2011_practice_qualifying.py`.
"""


def main() -> None:
    if not TIMING_ROOT.is_dir():
        raise SystemExit(f"Missing timing root: {TIMING_ROOT}")

    if OUT_ROOT.exists():
        shutil.rmtree(OUT_ROOT)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    races = discover_races(TIMING_ROOT)
    if len(races) != 17:
        print(f"warning: expected 17 races, found {len(races)}")

    manifest = {
        "dataset": "f1_2011_practice_qualifying",
        "year": 2011,
        "grain": "all_laps",
        "description": (
            "All practice and qualifying laps for the 2011 Formula 1 season, "
            "curated for pods / datasets_mirror."
        ),
        "grands_prix": [],
    }

    for meta in races:
        entry = curate_race(meta, OUT_ROOT)
        manifest["grands_prix"].append(entry)
        counts = " ".join(f"{k}={v}" for k, v in entry["n_laps"].items())
        print(f"{meta.grand_prix:14s}  {counts}  windows={entry['q_window_source']}")

    (OUT_ROOT / "README.md").write_text(README, encoding="utf-8")
    (OUT_ROOT / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nWrote {len(races)} grands prix under {OUT_ROOT}")


if __name__ == "__main__":
    main()
