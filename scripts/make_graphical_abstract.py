#!/usr/bin/env python3
"""Graphical Abstract: 单栏宽幅, 三块叙事 (病理->定律->结果)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path("paper")
C = {"blue": "#0072B2", "green": "#009E73", "red": "#D55E00",
     "orange": "#E69F00", "grey": "#7F7F7F", "black": "#111111", "sky": "#56B4E9"}
plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11, "figure.dpi": 300,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.06,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 1.0,
})

fig = plt.figure(figsize=(12.0, 3.1))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.5, 1.1], wspace=0.30)

# ── 块1: 三病理 ──
ax0 = fig.add_subplot(gs[0]); ax0.axis("off")
ax0.set_xlim(0, 10); ax0.set_ylim(0, 10)
ax0.text(5, 9.3, "UAV imagery: 3 coupled pathologies", ha="center", fontsize=12, fontweight="bold")
items = [("Scale", "85.3% < 32px*", C["blue"]),
         ("Long-tail", "45:1 head:tail", C["orange"]),
         ("Confusion", "23 pairs > 0.85", C["red"])]
for i, (t, s, col) in enumerate(items):
    y = 6.8 - i * 2.6
    ax0.add_patch(FancyBboxPatch((0.7, y - 0.9), 8.6, 1.9, boxstyle="round,pad=0.25",
                                 fc="white", ec=col, lw=1.8))
    ax0.text(2.6, y, t, fontsize=12, fontweight="bold", color=col, va="center")
    ax0.text(7.2, y, s, fontsize=11, color="#333", va="center")

# ── 块2: 定律 (fig8b 精简) ──
ax1 = fig.add_subplot(gs[1])
res = [640, 960, 1280, 1600, 1920]
delta = [0.21, 3.81, 0.05, 0.78, 3.83]
residual = [0, 0, 0, 0, 0.49]
colors = [C["grey"], C["green"], C["grey"], C["blue"], C["orange"]]
ax1.bar(range(5), delta, color=colors, width=0.62, zorder=3, alpha=0.48)
ax1.bar(range(5), residual, color="#8B0000", width=0.62, zorder=4)
for i, d in enumerate(delta):
    ax1.text(i, d + 0.12, f"{d:+.1f}", ha="center", fontsize=11, fontweight="bold")
ax1.axhline(0, color=C["black"], lw=0.9)
ax1.set_xticks(range(5)); ax1.set_xticklabels([str(r) for r in res], fontsize=11)
ax1.set_ylabel("ΔAP of union sampling", fontsize=11)
ax1.set_ylim(-0.7, 4.7)
ax1.set_title("Exposure-aware rebalancing principle", fontsize=12.5, fontweight="bold", pad=8)
ax1.text(1, -0.58, "under-fit", ha="center", fontsize=9, color=C["green"])
ax1.text(2, -0.58, "saturated", ha="center", fontsize=9, color=C["grey"])
ax1.text(4, -0.58, "exposure-lim.", ha="center", fontsize=9, color=C["orange"])
ax1.grid(axis="y", alpha=0.25, lw=0.5)

# ── 块3: 结果 ──
ax2 = fig.add_subplot(gs[2])
names = ["RemDet-X\n@640 (repro)", "RemDet-X\n@1600 (retrain)", "DAHP-L\n(ours)"]
vals = [29.90, 29.7, 38.16]
cols = [C["grey"], C["grey"], C["red"]]
ax2.bar(range(3), vals, color=cols, width=0.58, zorder=3)
for i, v in enumerate(vals):
    ax2.text(i, v + 0.5, f"{v:.1f}", ha="center", fontsize=11.5,
             fontweight="bold" if i == 2 else "normal")
ax2.set_xticks(range(3)); ax2.set_xticklabels(names, fontsize=9.5)
ax2.set_ylabel("AP (COCO md100)", fontsize=11)
ax2.set_ylim(0, 44)
ax2.set_title("+8.3 AP; 58% params; policy adds no arch change", fontsize=11.7, fontweight="bold", pad=8)
ax2.grid(axis="y", alpha=0.25, lw=0.5)

# 块间箭头
for x0, x1 in ((0.325, 0.355), (0.685, 0.715)):
    fig.patches.append(FancyArrowPatch((x0, 0.52), (x1, 0.52), transform=fig.transFigure,
                       arrowstyle="-|>", mutation_scale=26, lw=2.2, color="#666"))

fig.savefig(OUT / "graphical_abstract.png", facecolor="white")
fig.savefig(OUT / "graphical_abstract.pdf", facecolor="white")
print("graphical_abstract saved")
