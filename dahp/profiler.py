"""
DAHP v2 Profiler: 全维度数据集画像
===================================
扩展 v1 DatasetProfiler, 输出完整 DatasetProfile:
  - 挑战1: 类别不均衡 (频率、有效数权重、尾部类)
  - 挑战2: 尺度不一 (per-class 尺寸分布、分辨率建议)
  - 挑战3: 类别混淆 (混淆矩阵、长宽比/尺寸重叠、共现)
"""

import math
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch


@dataclass
class DatasetProfile:
    """DAHP v2 全维度数据集画像"""

    # 基础
    num_classes: int = 0
    num_images: int = 0
    num_annotations: int = 0
    class_names: List[str] = field(default_factory=list)

    # 挑战1: 类别不均衡
    class_counts: np.ndarray = None           # (nc,)
    class_frequencies: np.ndarray = None      # (nc,)
    imbalance_ratio: float = 0.0
    effective_number_weights: np.ndarray = None  # (nc,)
    tail_classes: List[int] = field(default_factory=list)

    # 挑战2: 尺度不一
    per_class_areas: Dict[int, np.ndarray] = field(default_factory=dict)
    per_class_scale_bins: Dict[int, Dict] = field(default_factory=dict)
    small_object_ratio: float = 0.0
    tiny_object_ratio: float = 0.0
    per_class_median_area: np.ndarray = None  # (nc,)
    suggest_p2: bool = False
    suggest_resolution: int = 640

    # 挑战3: 类别混淆
    confusion_matrix: np.ndarray = None       # (nc, nc)
    high_confusion_pairs: List[Tuple] = field(default_factory=list)
    per_class_aspect_ratios: Dict[int, np.ndarray] = field(default_factory=dict)
    aspect_ratio_overlap_matrix: np.ndarray = None  # (nc, nc)
    size_overlap_matrix: np.ndarray = None          # (nc, nc)
    confusion_with_ar_signal: np.ndarray = None     # (nc, nc) bool
    confusion_with_size_signal: np.ndarray = None   # (nc, nc) bool

    # 辅助统计
    co_occurrence_jaccard: np.ndarray = None  # (nc, nc)
    avg_objects_per_image: float = 0.0
    dense_scene_ratio: float = 0.0

    # v1 兼容
    class_weights: Optional[torch.Tensor] = None
    coarse_to_fine: Dict[int, List[int]] = field(default_factory=dict)
    fine_to_coarse: Dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, np.ndarray):
                d[k] = v.tolist()
            elif isinstance(v, torch.Tensor):
                d[k] = v.tolist()
            else:
                d[k] = v
        return d


class DatasetProfilerV2:
    """DAHP v2 全维度画像引擎"""

    def __init__(self, data_yaml_path: str, img_size: int = 640):
        self.data_yaml_path = data_yaml_path
        self.img_size = img_size

    def profile(self) -> DatasetProfile:
        import os, yaml

        with open(self.data_yaml_path) as f:
            data = yaml.safe_load(f)

        nc = data["nc"]
        names = data["names"]
        if isinstance(names, dict):
            names = [names[i] for i in range(nc)]

        train_path = data.get("train", "")
        if isinstance(train_path, str):
            train_path = [train_path]
        label_dirs = []
        for p in train_path:
            lp = p.replace("/images/", "/labels/")
            if lp == p:  # fallback: replace last occurrence
                lp = p.replace("/images", "/labels")
            label_dirs.append(lp)

        # ── 第一遍: 逐标注统计 ──
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

        # ── 转为 numpy ──
        per_class_areas = {i: np.array(areas) for i, areas in class_areas.items()}
        per_class_ar = {i: np.array(ar) for i, ar in class_ar.items()}

        # ── 挑战1: 类别不均衡 ──
        class_freq = class_counts / max(total, 1)
        beta = 0.9999
        eff_num = (1 - beta ** class_counts) / (1 - beta)
        eff_weights = (1 - beta) / np.maximum(eff_num, 1e-8)
        eff_weights = eff_weights / eff_weights.mean()
        eff_weights = np.clip(eff_weights, 0.5, 4.0)

        mean_cnt = class_counts[class_counts > 0].mean() if (class_counts > 0).any() else 1
        tail_classes = [i for i in range(nc) if class_counts[i] < mean_cnt * 0.3 and class_counts[i] > 0]

        # ── 挑战2: 尺度 ──
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

        suggest_p2 = small_ratio > 0.4
        suggest_resolution = 1280 if tiny_ratio > 0.4 else 640

        # ── 挑战3: 混淆 ──
        confusion = self._compute_confusion(per_class_areas, per_class_ar, nc)
        ar_overlap = self._compute_overlap_matrix(per_class_ar, nc)
        size_overlap = self._compute_overlap_matrix(per_class_areas, nc)

        high_conf_pairs = []
        for i in range(nc):
            for j in range(i + 1, nc):
                if confusion[i, j] > 0.5:
                    high_conf_pairs.append((confusion[i, j], i, j))
        high_conf_pairs.sort(reverse=True)

        # 混淆但有长宽比/尺寸区分信号
        conf_with_ar = np.zeros((nc, nc), dtype=bool)
        conf_with_size = np.zeros((nc, nc), dtype=bool)
        for i in range(nc):
            for j in range(i + 1, nc):
                if confusion[i, j] > 0.5:
                    # 长宽比分布重叠 < 混淆度 → 长宽比有区分力
                    if ar_overlap[i, j] < confusion[i, j] - 0.1:
                        conf_with_ar[i, j] = conf_with_ar[j, i] = True
                    if size_overlap[i, j] < confusion[i, j] - 0.1:
                        conf_with_size[i, j] = conf_with_size[j, i] = True

        # ── 共现 ──
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

        avg_obj_per_img = total / max(num_images, 1)
        dense_ratio = sum(1 for s in img_classes if len(s) > 20) / max(len(img_classes), 1)

        # ── v1 兼容权重 ──
        cfw = np.ones(nc, dtype=np.float32)
        for k in range(nc):
            if class_counts[k] > 0:
                freq_w = math.sqrt(max_cnt / class_counts[k])
                sr = (per_class_areas[k] < small_th).mean() if len(per_class_areas[k]) > 0 else 0
                cfw[k] = freq_w * (1.0 + sr)
        cfw = cfw / cfw.min()

        # ── 自动分组 (复用 v1 逻辑) ──
        hierarchy = self._auto_grouping(confusion, class_counts, nc)
        fine_to_coarse = {}
        for c, fines in hierarchy.items():
            for f in fines:
                fine_to_coarse[f] = c

        # ── 打印诊断 ──
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
            confusion_matrix=confusion, high_confusion_pairs=high_conf_pairs,
            per_class_aspect_ratios=per_class_ar,
            aspect_ratio_overlap_matrix=ar_overlap,
            size_overlap_matrix=size_overlap,
            confusion_with_ar_signal=conf_with_ar,
            confusion_with_size_signal=conf_with_size,
            co_occurrence_jaccard=cooccur_jaccard,
            avg_objects_per_image=avg_obj_per_img,
            dense_scene_ratio=dense_ratio,
            class_weights=torch.from_numpy(cfw),
            coarse_to_fine=hierarchy, fine_to_coarse=fine_to_coarse,
        )

    # ── 工具方法 ──

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
        return float(np.minimum(ha, hb).sum() / max(ha.sum(), hb.sum(), 1e-8))

    def _compute_confusion(self, areas, ars, nc):
        conf = np.zeros((nc, nc))
        for i in range(nc):
            for j in range(i + 1, nc):
                ar_ov = self._histogram_intersection(ars[i], ars[j])
                sz_ov = self._histogram_intersection(areas[i], areas[j])
                conf[i, j] = conf[j, i] = 0.6 * ar_ov + 0.4 * sz_ov
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
        print(f"  DAHP v2 画像完成")
        print(f"{'='*60}")
        print(f"  类别数: {nc}, 标注数: {total}, 不平衡比: {imb_ratio:.0f}:1")
        print(f"  小目标: {small_r:.1%}, 极小目标: {tiny_r:.1%}")
        print(f"  建议分辨率: {suggest_res}px")
        if conf_pairs:
            print(f"  高混淆类对 (top 5):")
            for score, i, j in conf_pairs[:5]:
                print(f"    {names[i]} <-> {names[j]} = {score:.3f}")
        print(f"{'='*60}")
