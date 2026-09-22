#!/usr/bin/env python3
"""Measure label-only stability of the DAHP structural-policy thresholds.

This script does not train detectors and does not estimate AP.  It answers a
narrower methodological question: do nearby choices of the structural-proxy
weight and graph threshold change the classes selected for rebalancing?
Inputs are YOLO-format training labels only.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

import numpy as np


DEFAULT_NAMES = (
    "pedestrian,people,bicycle,car,van,truck,tricycle,awning-tricycle,bus,motor"
)


def parse_floats(text: str) -> List[float]:
    return [float(x) for x in text.split(",") if x.strip()]


def read_labels(
    label_dirs: Sequence[Path], num_classes: int, reference_size: int
) -> Tuple[np.ndarray, Dict[int, np.ndarray], Dict[int, np.ndarray], List[Set[int]]]:
    counts = np.zeros(num_classes, dtype=np.float64)
    areas: Dict[int, List[float]] = {c: [] for c in range(num_classes)}
    aspect_ratios: Dict[int, List[float]] = {c: [] for c in range(num_classes)}
    image_classes: List[Set[int]] = []

    for label_dir in label_dirs:
        if not label_dir.is_dir():
            raise FileNotFoundError(f"Label directory not found: {label_dir}")
        for label_path in sorted(label_dir.glob("*.txt")):
            classes_in_image: Set[int] = set()
            with label_path.open(encoding="utf-8") as handle:
                for line in handle:
                    fields = line.strip().split()
                    if len(fields) < 5:
                        continue
                    cls = int(fields[0])
                    if not 0 <= cls < num_classes:
                        continue
                    width = float(fields[3]) * reference_size
                    height = float(fields[4]) * reference_size
                    if width <= 0 or height <= 0:
                        continue
                    counts[cls] += 1
                    areas[cls].append(width * height)
                    aspect_ratios[cls].append(width / height)
                    classes_in_image.add(cls)
            if classes_in_image:
                image_classes.append(classes_in_image)

    area_arrays = {c: np.asarray(values, dtype=np.float64) for c, values in areas.items()}
    ar_arrays = {
        c: np.asarray(values, dtype=np.float64) for c, values in aspect_ratios.items()
    }
    return counts, area_arrays, ar_arrays, image_classes


def histogram_intersection(left: np.ndarray, right: np.ndarray, bins: int = 20) -> float:
    """Match dahp.profiler.DatasetProfiler._histogram_intersection."""
    if len(left) == 0 or len(right) == 0:
        return 0.0
    low = min(float(left.min()), float(right.min()))
    high = max(float(left.max()), float(right.max()))
    if high <= low:
        return 1.0
    left_hist, _ = np.histogram(left, bins=bins, range=(low, high), density=True)
    right_hist, _ = np.histogram(right, bins=bins, range=(low, high), density=True)
    left_hist = left_hist / max(left_hist.sum(), 1e-8)
    right_hist = right_hist / max(right_hist.sum(), 1e-8)
    return float(np.minimum(left_hist, right_hist).sum())


def structural_matrix(
    areas: Dict[int, np.ndarray],
    aspect_ratios: Dict[int, np.ndarray],
    num_classes: int,
    lambda_weight: float,
) -> np.ndarray:
    matrix = np.zeros((num_classes, num_classes), dtype=np.float64)
    for i in range(num_classes):
        for j in range(i + 1, num_classes):
            ar_overlap = histogram_intersection(aspect_ratios[i], aspect_ratios[j])
            scale_overlap = histogram_intersection(areas[i], areas[j])
            value = lambda_weight * ar_overlap + (1.0 - lambda_weight) * scale_overlap
            matrix[i, j] = matrix[j, i] = value
    return matrix


def policy_sets(
    counts: np.ndarray,
    matrix: np.ndarray,
    names: Sequence[str],
    threshold: float,
    axis_margin: float,
) -> Dict[str, object]:
    nonempty = counts[counts > 0]
    mean_count = float(nonempty.mean()) if len(nonempty) else 1.0
    tail = {c for c in range(len(names)) if 0 < counts[c] < 0.3 * mean_count}
    head = {c for c in range(len(names)) if counts[c] > mean_count}
    axis_threshold = min(1.0, threshold + axis_margin)
    axis = {
        c
        for c in range(len(names))
        if c not in head and c not in tail
        and any(matrix[h, c] > axis_threshold for h in head)
    }
    policy = sorted(tail | axis)
    high_pairs = [
        (i, j)
        for i in range(len(names))
        for j in range(i + 1, len(names))
        if matrix[i, j] > threshold
    ]
    return {
        "threshold": threshold,
        "tail_classes": [names[c] for c in sorted(tail)],
        "confusion_axis": [names[c] for c in sorted(axis)],
        "rebalanced_classes": [names[c] for c in policy],
        "num_edges_above_threshold": len(high_pairs),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--label-dir",
        type=Path,
        action="append",
        required=True,
        help="YOLO label directory; repeat the option for multiple training shards",
    )
    parser.add_argument("--names", type=str, default=DEFAULT_NAMES)
    parser.add_argument("--reference-size", type=int, default=1280)
    parser.add_argument("--lambdas", type=str, default="0.4,0.5,0.6,0.7")
    parser.add_argument("--thresholds", type=str, default="0.80,0.85,0.90")
    parser.add_argument("--axis-margin", type=float, default=0.01)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    names = [name.strip() for name in args.names.split(",") if name.strip()]
    if not names:
        raise ValueError("At least one class name is required")
    lambda_values = parse_floats(args.lambdas)
    thresholds = parse_floats(args.thresholds)
    if not lambda_values or not thresholds:
        raise ValueError("At least one lambda and threshold are required")

    counts, areas, aspect_ratios, _ = read_labels(
        args.label_dir, len(names), args.reference_size
    )
    rows = []
    for lambda_weight in lambda_values:
        matrix = structural_matrix(areas, aspect_ratios, len(names), lambda_weight)
        for threshold in thresholds:
            row = {
                "lambda": lambda_weight,
                **policy_sets(counts, matrix, names, threshold, args.axis_margin),
            }
            rows.append(row)

    output = {
        "protocol": "label-only decision stability; no detector training or AP estimate",
        "reference_size": args.reference_size,
        "axis_margin": args.axis_margin,
        "num_labels": int(counts.sum()),
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    markdown = args.output.with_suffix(".md")
    lines = [
        "# DAHP threshold decision-stability audit",
        "",
        f"Reference size: {args.reference_size} px; axis margin: {args.axis_margin:.2f}.",
        "This is a label-only policy audit, not an AP sweep.",
        "",
        "| lambda | threshold | edges | tail classes | confusion axis | rebalanced classes |",
        "|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['lambda']:.1f} | {row['threshold']:.2f} | "
            f"{row['num_edges_above_threshold']} | "
            f"{', '.join(row['tail_classes']) or '--'} | "
            f"{', '.join(row['confusion_axis']) or '--'} | "
            f"{', '.join(row['rebalanced_classes']) or '--'} |"
        )
    markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Wrote {markdown}")


if __name__ == "__main__":
    main()
