"""Label-only dataset profiling for DAHP policy selection.

The profiler computes class-frequency, scale, structural-confusion, and density
statistics without decoding images or running a detector.
"""

import math
import os
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

try:                      # torch is optional: only used for the legacy
    import torch          # class_weights tensor (v1 compatibility)
    torch.from_numpy(numpy.zeros(1))   # functional probe (numpy interop)
except Exception:         # pragma: no cover
    torch = None


@dataclass
class DatasetProfile:
    """Complete label-only dataset profile used by the DAHP policy."""

    # Basic counts
    num_classes: int = 0
    num_images: int = 0
    num_annotations: int = 0
    class_names: List[str] = field(default_factory=list)

    # Class imbalance
    class_counts: np.ndarray = None           # (nc,)
    class_frequencies: np.ndarray = None      # (nc,)
    imbalance_ratio: float = 0.0
    effective_number_weights: np.ndarray = None  # (nc,)
    tail_classes: List[int] = field(default_factory=list)

    # Scale imbalance
    per_class_areas: Dict[int, np.ndarray] = field(default_factory=dict)
    per_class_scale_bins: Dict[int, Dict] = field(default_factory=dict)
    small_object_ratio: float = 0.0
    tiny_object_ratio: float = 0.0
    per_class_median_area: np.ndarray = None  # (nc,)
    suggest_p2: bool = False
    suggest_resolution: int = 640
    resolution_ladder: List[int] = field(default_factory=lambda: [960, 1280, 1600, 1920])
    small_mass: float = 0.0            # sum_c f(c) * s_small(c)  (Eq. 2)
    tiny_mass: float = 0.0             # sum_c f(c) * s_tiny(c)
    confusion_axis: List[int] = field(default_factory=list)   # policy axis A = graph \ head (Eq. 3)
    kappa_threshold: float = 0.85      # confusion-graph edge threshold (reported)
    kappa_lambda: float = 0.6
    axis_threshold: float = 0.86        # oversampling-eligibility margin over head
    head_classes: List[int] = field(default_factory=list)      # N_c > mean(N)
    geo_overlap_matrix: np.ndarray = None                      # auxiliary: J_sigma
    kappa_matrix: np.ndarray = None                            # primary structural proxy

    # Structural-confusion proxy
    confusion_matrix: np.ndarray = None       # (nc, nc)
    high_confusion_pairs: List[Tuple] = field(default_factory=list)
    per_class_aspect_ratios: Dict[int, np.ndarray] = field(default_factory=dict)
    aspect_ratio_overlap_matrix: np.ndarray = None  # (nc, nc)
    size_overlap_matrix: np.ndarray = None          # (nc, nc)
    confusion_with_ar_signal: np.ndarray = None     # (nc, nc) bool
    confusion_with_size_signal: np.ndarray = None   # (nc, nc) bool

    # Auxiliary statistics
    co_occurrence_jaccard: np.ndarray = None  # (nc, nc)
    avg_objects_per_image: float = 0.0
    dense_scene_ratio: float = 0.0

    # Compatibility with the original profiler
    class_weights: Optional["torch.Tensor"] = None
    coarse_to_fine: Dict[int, List[int]] = field(default_factory=dict)
    fine_to_coarse: Dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, np.ndarray):
                d[k] = v.tolist()
            elif torch is not None and isinstance(v, torch.Tensor):
                d[k] = v.tolist()
            else:
                d[k] = v
        return d


class DatasetProfiler:
    """Profile a YOLO-format detection dataset from labels alone."""

    def __init__(self, data_yaml_path: str, img_size: int = 640):
        self.data_yaml_path = data_yaml_path
        self.img_size = img_size

    def profile(self) -> DatasetProfile:
        import yaml

        with open(self.data_yaml_path) as f:
            data = yaml.safe_load(f)

        names = data.get("names", [])
        if isinstance(names, dict):
            names = [names[i] for i in sorted(names, key=int)]
        nc = int(data.get("nc", len(names)))

        dataset_root = data.get("path", "")
        train_path = data.get("train", "")
        if isinstance(train_path, str):
            train_path = [train_path]
        label_dirs = []
        for p in train_path:
            if dataset_root and not os.path.isabs(p):
                p = str(Path(dataset_root) / p)
            p_path = Path(p)
            if p_path.name == "images":
                lp = str(p_path.with_name("labels"))
            else:  # compatibility with configs that embed /images/ in a longer path
                lp = p.replace("/images/", "/labels/").replace("\\images\\", "\\labels\\")
                if lp == p:
                    lp = p.replace("/images", "/labels").replace("\\images", "\\labels")
            label_dirs.append(lp)

        # First pass: instance-level statistics.
        class_counts = np.zeros(nc, dtype=np.float64)
        class_areas = {i: [] for i in range(nc)}
        class_ar = {i: [] for i in range(nc)}
        img_classes = []
        num_images = 0

        for label_dir in label_dirs:
            if not os.path.isdir(label_dir):
                continue
            for fname in sorted(os.listdir(label_dir)):
                if not fname.endswith(".txt"):
                    continue
                num_images += 1
                img_cls = set()
                with open(os.path.join(label_dir, fname)) as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) < 5:
                            continue
                        cls = int(parts[0])
                        w, h = float(parts[3]), float(parts[4])
                        w_px = w * self.img_size
                        h_px = h * self.img_size
                        area_px = w_px * h_px
                        if 0 <= cls < nc:
                            class_counts[cls] += 1
                            class_areas[cls].append(area_px)
                            if h_px > 0:
                                class_ar[cls].append(w_px / h_px)
                            img_cls.add(cls)
                if img_cls:
                    img_classes.append(img_cls)

        total = int(class_counts.sum())
        max_cnt = class_counts.max()
        min_cnt = class_counts[class_counts > 0].min() if (class_counts > 0).any() else 1

        # Convert accumulated values to NumPy arrays.
        per_class_areas = {i: np.array(areas) for i, areas in class_areas.items()}
        per_class_ar = {i: np.array(ar) for i, ar in class_ar.items()}

        # Class-frequency and tail-set statistics.
        class_freq = class_counts / max(total, 1)
        beta = 0.9999
        eff_num = (1 - beta ** class_counts) / (1 - beta)
        eff_weights = (1 - beta) / np.maximum(eff_num, 1e-8)
        eff_weights = eff_weights / eff_weights.mean()
        eff_weights = np.clip(eff_weights, 0.5, 4.0)

        mean_cnt = class_counts[class_counts > 0].mean() if (class_counts > 0).any() else 1
        tail_classes = [i for i in range(nc) if class_counts[i] < mean_cnt * 0.3 and class_counts[i] > 0]

        # Scale statistics and the resolution prior.
        tiny_th = 16 * 16
        small_th = 32 * 32
        med_th = 96 * 96
        non_empty_areas = [per_class_areas[i] for i in range(nc) if len(per_class_areas[i]) > 0]
        all_areas = np.concatenate(non_empty_areas) if non_empty_areas else np.array([1024.0])
        small_ratio = float((all_areas < small_th).sum() / max(len(all_areas), 1))
        tiny_ratio = float((all_areas < tiny_th).sum() / max(len(all_areas), 1))

        per_class_scale_bins = {}
        median_areas = np.zeros(nc)
        for i in range(nc):
            areas = per_class_areas[i]
            if len(areas) == 0:
                per_class_scale_bins[i] = {"tiny": 0, "small": 0, "medium": 0, "large": 0}
                continue
            median_areas[i] = np.median(areas)
            per_class_scale_bins[i] = {
                "tiny": float((areas < tiny_th).sum() / len(areas)),
                "small": float((areas < small_th).sum() / len(areas)),
                "medium": float(((areas >= small_th) & (areas < med_th)).sum() / len(areas)),
                "large": float((areas >= med_th).sum() / len(areas)),
            }

        # Eq. (2): frequency-weighted small-object mass drives the P2 decision
        small_mass = float(sum(class_freq[c] * per_class_scale_bins[c]["small"] for c in range(nc)))
        tiny_mass = float(sum(class_freq[c] * per_class_scale_bins[c]["tiny"] for c in range(nc)))
        suggest_p2 = small_mass > 0.3

        # Algorithm 1: resolution ladder {960..1920}; pick r* preferring the
        # intermediate regime. Label-only prior from the empirical regime curve:
        # larger tiny/small mass requires more exposure headroom (higher r*).
        ladder = [960, 1280, 1600, 1920]
        if tiny_mass > 0.55:
            suggest_resolution = 1920      # extreme exposure limitation
        elif tiny_mass > 0.35:
            suggest_resolution = 1600      # documented sweet spot
        elif tiny_mass > 0.15:
            suggest_resolution = 1280
        else:
            suggest_resolution = 960

        # Auxiliary co-occurrence Jaccard statistics.
        cooccur = np.zeros((nc, nc), dtype=int)
        for cls_set in img_classes:
            for a, b in combinations(cls_set, 2):
                cooccur[min(a, b), max(a, b)] += 1
        cooccur_jaccard = np.zeros((nc, nc))
        class_img_counts = np.zeros(nc)
        for cls_set in img_classes:
            for c in cls_set:
                class_img_counts[c] += 1
        for i in range(nc):
            for j in range(i + 1, nc):
                union = class_img_counts[i] + class_img_counts[j] - cooccur[i, j]
                cooccur_jaccard[i, j] = cooccur_jaccard[j, i] = cooccur[i, j] / max(union, 1)

        # Annotation-level structural-confusion proxy (Eq. 3).
        # kappa(a,b) = lam * J_ar(a,b) + (1-lam) * J_scale(a,b),  lam = 0.6
        #   J_ar    : aspect-ratio distribution histogram intersection
        #   J_scale : equivalent-side-length distribution histogram intersection
        # Co-occurrence Jaccard is reported as an auxiliary statistic only.
        confusion = self._compute_confusion(per_class_areas, per_class_ar, nc)
        ar_overlap = self._compute_overlap_matrix(per_class_ar, nc)
        size_overlap = self._compute_overlap_matrix(per_class_areas, nc)
        geo_overlap = self._compute_overlap_matrix(per_class_areas, nc)

        kappa_threshold = 0.85
        high_conf_pairs = []
        axis_classes = set()
        for i in range(nc):
            for j in range(i + 1, nc):
                if confusion[i, j] > kappa_threshold:
                    high_conf_pairs.append((confusion[i, j], i, j))
                    axis_classes.update((i, j))
                elif confusion[i, j] > 0.5:
                    high_conf_pairs.append((confusion[i, j], i, j))
        high_conf_pairs.sort(reverse=True)
        # head classes (N_c > mean over non-empty) anchor the confusion axis:
        # A = {c not in head, c not in T : kappa(c, h) > axis_threshold for some head h}
        # The margin tau_A = 0.86 over the graph threshold 0.85 excludes the
        # borderline semantic near-duplicate pair (people-pedestrian, 0.854).
        axis_threshold = 0.86
        head_classes = sorted(c for c in range(nc) if class_counts[c] > mean_cnt)
        tail_set = set(tail_classes)
        axis = set()
        for h in head_classes:
            for c in range(nc):
                if c in head_classes or c in tail_set:
                    continue
                if confusion[h, c] > axis_threshold:
                    axis.add(c)
        confusion_axis = sorted(axis)

        # Record whether aspect-ratio or scale separates a confusable pair.
        conf_with_ar = np.zeros((nc, nc), dtype=bool)
        conf_with_size = np.zeros((nc, nc), dtype=bool)
        for i in range(nc):
            for j in range(i + 1, nc):
                if confusion[i, j] > 0.5:
                    # Aspect-ratio overlap below the proxy indicates a useful cue.
                    if ar_overlap[i, j] < confusion[i, j] - 0.1:
                        conf_with_ar[i, j] = conf_with_ar[j, i] = True
                    if size_overlap[i, j] < confusion[i, j] - 0.1:
                        conf_with_size[i, j] = conf_with_size[j, i] = True

        avg_obj_per_img = total / max(num_images, 1)
        dense_ratio = sum(1 for s in img_classes if len(s) > 20) / max(len(img_classes), 1)

        # Compatibility weights from the original profiler.
        cfw = np.ones(nc, dtype=np.float32)
        for k in range(nc):
            if class_counts[k] > 0:
                freq_w = math.sqrt(max_cnt / class_counts[k])
                sr = (per_class_areas[k] < small_th).mean() if len(per_class_areas[k]) > 0 else 0
                cfw[k] = freq_w * (1.0 + sr)
        cfw = cfw / cfw.min()

        # Auxiliary hierarchical grouping.
        hierarchy = self._auto_grouping(confusion, class_counts, nc)
        fine_to_coarse = {}
        for c, fines in hierarchy.items():
            for f in fines:
                fine_to_coarse[f] = c

        # Diagnostic summary.
        self._print_diagnostic(names, nc, total, class_counts, small_ratio, tiny_ratio,
                               max_cnt / min_cnt, high_conf_pairs, suggest_resolution)

        return DatasetProfile(
            num_classes=nc, num_images=num_images, num_annotations=total,
            class_names=names,
            class_counts=class_counts, class_frequencies=class_freq,
            imbalance_ratio=float(max_cnt / min_cnt),
            effective_number_weights=eff_weights,
            tail_classes=tail_classes,
            per_class_areas=per_class_areas, per_class_scale_bins=per_class_scale_bins,
            small_object_ratio=small_ratio, tiny_object_ratio=tiny_ratio,
            per_class_median_area=median_areas,
            suggest_p2=suggest_p2, suggest_resolution=suggest_resolution,
            resolution_ladder=ladder, small_mass=small_mass, tiny_mass=tiny_mass,
            confusion_axis=confusion_axis, kappa_threshold=kappa_threshold, kappa_lambda=0.6,
            axis_threshold=axis_threshold,
            head_classes=head_classes, geo_overlap_matrix=geo_overlap, kappa_matrix=confusion,
            confusion_matrix=confusion, high_confusion_pairs=high_conf_pairs,
            per_class_aspect_ratios=per_class_ar,
            aspect_ratio_overlap_matrix=ar_overlap,
            size_overlap_matrix=size_overlap,
            confusion_with_ar_signal=conf_with_ar,
            confusion_with_size_signal=conf_with_size,
            co_occurrence_jaccard=cooccur_jaccard,
            avg_objects_per_image=avg_obj_per_img,
            dense_scene_ratio=dense_ratio,
            class_weights=(torch.from_numpy(cfw) if torch is not None else cfw),
            coarse_to_fine=hierarchy, fine_to_coarse=fine_to_coarse,
        )

    # Utility methods

    @staticmethod
    def _histogram_intersection(a: np.ndarray, b: np.ndarray, bins: int = 20) -> float:
        if len(a) == 0 or len(b) == 0:
            return 0.0
        lo = min(a.min(), b.min())
        hi = max(a.max(), b.max())
        if hi <= lo:
            return 1.0
        ha, _ = np.histogram(a, bins=bins, range=(lo, hi), density=True)
        hb, _ = np.histogram(b, bins=bins, range=(lo, hi), density=True)
        ha = ha / max(ha.sum(), 1e-8)
        hb = hb / max(hb.sum(), 1e-8)
        return float(np.minimum(ha, hb).sum())

    def _compute_confusion(self, areas, ars, nc, lam: float = 0.6):
        """Eq. (3): kappa(a,b) = lam * J_ar(a,b) + (1-lam) * J_scale(a,b).

        An annotation-level *structural confusion proxy*:
          J_ar    : histogram intersection of aspect-ratio distributions
          J_scale : histogram intersection of squared equivalent side length
                    (instance scale s = w*h at the reference resolution)
        Head-pruned graph edges with kappa > 0.85 form the policy axis A.
        Co-occurrence Jaccard and geo overlap are auxiliary statistics.
        """
        conf = np.zeros((nc, nc))
        for i in range(nc):
            for j in range(i + 1, nc):
                j_ar = self._histogram_intersection(ars[i], ars[j])
                j_sc = self._histogram_intersection(areas[i], areas[j])
                conf[i, j] = conf[j, i] = lam * j_ar + (1.0 - lam) * j_sc
        return conf

    def _compute_overlap_matrix(self, distributions, nc):
        mat = np.zeros((nc, nc))
        for i in range(nc):
            for j in range(i + 1, nc):
                v = self._histogram_intersection(distributions[i], distributions[j])
                mat[i, j] = mat[j, i] = v
        return mat

    def _auto_grouping(self, confusion, counts, nc):
        if nc <= 2:
            return {0: list(range(nc))}
        num_coarse = max(2, int(round(math.sqrt(nc))))
        groups = {i: [i] for i in range(nc)}
        active = set(range(nc))
        while len(active) > num_coarse:
            best_score, best_pair = -1, None
            for a in sorted(active):
                for b in sorted(active):
                    if a >= b:
                        continue
                    conf = sum(confusion[i, j] for i in groups[a] for j in groups[b])
                    conf /= len(groups[a]) * len(groups[b])
                    ca = sum(counts[c] for c in groups[a])
                    cb = sum(counts[c] for c in groups[b])
                    bal = min(ca, cb) / max(ca, cb, 1)
                    score = conf * (0.7 + 0.3 * bal)
                    if score > best_score:
                        best_score, best_pair = score, (a, b)
            if best_pair is None:
                break
            a, b = best_pair
            groups[a] = groups[a] + groups[b]
            del groups[b]
            active.remove(b)
        return {new: sorted(groups[old]) for new, old in enumerate(sorted(groups.keys()))}

    def _print_diagnostic(self, names, nc, total, counts, small_r, tiny_r,
                          imb_ratio, conf_pairs, suggest_res):
        print(f"\n{'='*60}")
        print("  DAHP profile complete")
        print(f"{'='*60}")
        print(f"  Classes: {nc}; instances: {total}; imbalance: {imb_ratio:.0f}:1")
        print(f"  Small: {small_r:.1%}; tiny: {tiny_r:.1%}")
        print(f"  Suggested resolution: {suggest_res}px")
        if conf_pairs:
            print("  High-similarity pairs (top 5):")
            for score, i, j in conf_pairs[:5]:
                print(f"    {names[i]} <-> {names[j]} = {score:.3f}")
        print(f"{'='*60}")


# Backward-compatible name for scripts written during early releases.
DatasetProfilerV2 = DatasetProfiler
