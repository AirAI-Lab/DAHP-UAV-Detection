#!/usr/bin/env python3
"""Reject a latency JSON that is not eligible for paper evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_TAGS = {
    "baseline_v8mP2_1280",
    "vanilla_v8l_1600",
    "v8lP2_1600",
    "dahpL_1600",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", type=Path)
    args = parser.parse_args()

    raw = json.loads(args.json_path.read_text(encoding="utf-8"))
    protocol = raw.get("protocol", {})
    results = raw.get("results", [])
    tags = {item.get("tag") for item in results}
    errors = []

    if protocol.get("n_measure", 0) < 300:
        errors.append("fewer than 300 measured images")
    if tags != EXPECTED_TAGS:
        errors.append(f"unexpected tags: {sorted(tags)}")
    if len(results) != len(EXPECTED_TAGS):
        errors.append("missing result entries")
    for item in results:
        gpu = item.get("gpu", {})
        if item.get("n_measure", 0) < 300:
            errors.append(f"{item.get('tag')}: fewer than 300 measurements")
        if not gpu.get("exclusive_at_start"):
            errors.append(f"{item.get('tag')}: GPU was not exclusive at start")
        if not gpu.get("no_external_process_at_end"):
            errors.append(f"{item.get('tag')}: external process appeared")
        if not gpu.get("paper_eligible"):
            errors.append(f"{item.get('tag')}: not paper eligible")

    if errors:
        raise SystemExit("; ".join(errors))
    print("FPS_RESULT_PAPER_ELIGIBLE")


if __name__ == "__main__":
    main()
