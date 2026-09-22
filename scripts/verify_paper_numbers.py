#!/usr/bin/env python3
"""Verify that headline manuscript numbers match the released result JSON.

JSON-backed values are recomputed from ``results/eval/paper_results_public.json``
and must equal the formatted string used in ``paper/DAHP_TGRS.tex``. A small
set of native-protocol reference values is pinned here because their per-class
evaluation dumps are intentionally omitted from the public artifact; the pinned
strings still guard against accidental manuscript edits.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
TEX_PATH = ROOT / "paper" / "DAHP_TGRS.tex"
RESULTS_PATH = ROOT / "results" / "eval" / "paper_results_public.json"


def _eval_row(data: dict[str, Any], run: str) -> dict[str, Any]:
    for row in data["evaluation_results"]:
        if row.get("run") == run:
            return row
    raise KeyError(f"evaluation run not found: {run}")


def _upstream_row(data: dict[str, Any], run: str) -> dict[str, Any]:
    for row in data["upstream_modern_baselines"]:
        if row.get("run") == run:
            return row
    raise KeyError(f"upstream baseline not found: {run}")


def _latency_row(data: dict[str, Any], tag: str) -> dict[str, Any]:
    for row in data["latency_memory"]["results"]:
        if row.get("tag") == tag:
            return row
    raise KeyError(f"latency entry not found: {tag}")


def _agglomerate(data: dict[str, Any], name: str) -> dict[str, Any]:
    for row in data["control_aggregates"]:
        if row.get("control") == name:
            return row
    raise KeyError(f"control aggregate not found: {name}")


def main() -> int:
    tex = TEX_PATH.read_text(encoding="utf-8")
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

    def ap(run: str) -> Callable[[], float]:
        return lambda: float(_eval_row(data, run)["AP50-95"])

    def upstream_ap(run: str) -> Callable[[], float]:
        return lambda: float(_upstream_row(data, run)["AP50-95"])

    def latency(tag: str, field: str) -> Callable[[], float]:
        return lambda: float(_latency_row(data, tag)[field])

    checks: list[tuple[str, str, Callable[[], float] | None, int]] = [
        # (description, exact manuscript string, JSON source or None for pinned, decimals)
        ("DAHP-L md100 AP", "38.16", ap("visdrone_dahpL_1600_union"), 2),
        ("DAHP-L native AP (pinned)", "40.06", None, 2),
        ("DAHP-L-E7 WBF md100 AP", "39.61", ap("visdrone_dahpL_E7_wbf"), 2),
        ("V_L+P2 md100 control", "37.59", ap("visdrone_v8lP2_1600_no_sampling"), 2),
        ("primary baseline md100 AP", "34.63", ap("visdrone_v8mP2_1280_base"), 2),
        ("primary baseline native AP (pinned)", "36.20", None, 2),
        ("V_L+P2 native AP (pinned)", "39.04", None, 2),
        ("exact 960 base", "28.10", ap("exact960_base_b2"), 2),
        ("exact 960 random-volume control", "31.77", ap("exact960_random_volume_b2"), 2),
        ("exact 960 targeted union", "31.92", ap("exact960_targeted_union_b2"), 2),
        ("exact 1280 random-volume control", "34.72", ap("exact1280_random_volume"), 2),
        ("exact 1280 targeted union", "35.12", ap("exact1280_targeted_union"), 2),
        ("exposure-matched 1920 base@120", "37.51", ap("exposure1920_base_120ep"), 2),
        ("exposure-matched 1920 union@60", "37.93", ap("exposure1920_union_60ep"), 2),
        ("same-input DAHP-M control", "26.11", ap("visdrone_dahpM_640_full_policy"), 2),
        ("D-FINE-M reproduced baseline", "31.67", upstream_ap("dfine_m_640"), 2),
        ("RT-DETRv2-L reproduced baseline", "29.47", upstream_ap("rtdetrv2_l_640"), 2),
        ("RemDet reproduced baseline", "29.90", upstream_ap("remdet_x_640_official_weights"), 2),
        ("RT-DETR base probe md100", "15.51", ap("rtdetr_l_b2_base"), 2),
        ("RT-DETR union probe md100", "7.61", ap("rtdetr_l_b2_union"), 2),
        ("DAHP-L end-to-end latency (ms)", "38.0", latency("dahpL_1600", "aggregate_end_to_end_ms_per_image"), 1),
        ("DAHP-L end-to-end FPS", "26.3", latency("dahpL_1600", "fps_end_to_end"), 1),
    ]

    failures: list[str] = []
    for desc, paper_string, source, decimals in checks:
        in_tex = paper_string in tex
        json_ok = True
        json_note = "pinned"
        if source is not None:
            value = source()
            expected = f"{value:.{decimals}f}"
            json_ok = expected == paper_string
            json_note = f"json={value:.6f}"
        status = "OK" if (in_tex and json_ok) else "FAIL"
        print(f"[{status}] {desc}: paper='{paper_string}' tex={in_tex} {json_note}")
        if status == "FAIL":
            failures.append(desc)

    # Aggregated decompositions that must stay internally consistent.
    exact960 = _agglomerate(data, "exact960_triplet")
    exact1280 = _agglomerate(data, "exact1280_triplet")
    exposure = _agglomerate(data, "exposure1920_matched")
    aggregate_checks = [
        ("960 volume delta", "+3.67", exact960["decomposition"]["volume"], 2),
        ("960 targeted residual", "+0.15", exact960["decomposition"]["targeted_residual"], 2),
        ("1280 volume delta", "+0.09", exact1280["decomposition"]["volume"], 2),
        ("1280 targeted residual", "+0.40", exact1280["decomposition"]["targeted_residual"], 2),
        ("1920 exposure-matched md100 residual", "+0.42", exposure["decomposition"]["matched_md100"], 2),
        ("1920 exposure-matched APs residual", "+0.92", exposure["decomposition"]["matched_APs"], 2),
    ]
    for desc, paper_string, value, decimals in aggregate_checks:
        expected = f"+{value:.{decimals}f}"
        in_tex = paper_string in tex
        ok = in_tex and expected == paper_string
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {desc}: paper='{paper_string}' json={value:.6f}")
        if not ok:
            failures.append(desc)

    if failures:
        print(f"\n{len(failures)} manuscript-number check(s) failed:")
        for item in failures:
            print(f"  - {item}")
        return 1
    print(f"\nAll {len(checks) + len(aggregate_checks)} manuscript-number checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
