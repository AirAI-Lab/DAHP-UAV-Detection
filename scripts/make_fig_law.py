#!/usr/bin/env python3
"""终极图: 定律五点矩阵图 (论文核心理论图)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path("paper/figures_v2")
OUT.mkdir(parents=True, exist_ok=True)
C = {"blue": "#0072B2", "green": "#009E73", "red": "#D55E00",
     "orange": "#E69F00", "grey": "#7F7F7F", "black": "#000000", "sky": "#56B4E9"}
plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "figure.dpi": 300,
    "savefig.dpi": 300, "savefig.bbox": "tight", "axes.grid": True,
    "grid.alpha": 0.25, "grid.linewidth": 0.4, "axes.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
})

res = [640, 960, 1280, 1600, 1920]
base = [27.27, 30.26, 36.20, 38.07, 35.67]
union = [27.48, 33.41, 36.25, 38.85, 39.50]
matched = [None, None, None, None, 39.01]
delta = [u - b for u, b in zip(union, base)]
regime = ["unlearnable", "under-fit", "saturated", "sweet spot", "exposure-lim."]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.16, 2.6), gridspec_kw={"width_ratios": [1.2, 1]})

# (a) 双线 + 增益标注
ax1.plot(res, base, "s--", color=C["grey"], ms=5, lw=1.4, label="base", zorder=3)
ax1.plot(res, union, "o-", color=C["red"], ms=5.5, lw=1.6, label="+union @ same epoch", zorder=4)
ax1.plot([r for r,m in zip(res,matched) if m is not None], [m for m in matched if m is not None], "X", color=C["black"], ms=7, mec="white", mew=0.8, label="base@120 (exposure-matched)", zorder=5)
ax1.annotate("matched residual\n+0.49 AP", xy=(1920,39.01), xytext=(1500,40.35), fontsize=6.8, ha="center", arrowprops=dict(arrowstyle="->", lw=0.7, color=C["black"]))
for r, b, u, d in zip(res, base, union, delta):
    ax1.annotate(f"+{d:.2f}", ((r), (b + u) / 2 + 0.8), fontsize=6.5, ha="center",
                 color=C["green"] if d > 0.5 else (C["grey"] if abs(d) < 0.5 else C["red"]))
ax1.set_xlabel("Input resolution (px)")
ax1.set_ylabel("mAP50-95 (native)")
ax1.set_xticks(res)
ax1.legend(frameon=False, loc="lower right", fontsize=7)
ax1.set_title("(a) Resolution-sampling matrix", loc="left", fontweight="bold")

# (b) 增益柱状 + regime 着色
colors = [C["grey"], C["green"], C["grey"], C["blue"], C["orange"]]
bars = ax2.bar(range(5), delta, color=colors, width=0.6, zorder=3)
for i, (d, rg) in enumerate(zip(delta, regime)):
    ax2.text(i, d + 0.12 if d >= 0 else d - 0.35, f"{d:+.2f}", ha="center", fontsize=7)
    ax2.text(i, -0.85, rg, ha="center", fontsize=5.8, rotation=38, color="#444")
ax2.axhline(0, color=C["black"], lw=0.7)
ax2.set_xticks(range(5))
ax2.set_xticklabels([str(r) for r in res])
ax2.set_ylabel("ΔAP of union sampling")
ax2.set_ylim(-1.1, 4.6)
ax2.set_title("(b) Same-epoch effect; 1920 requires exposure matching", loc="left", fontweight="bold")

fig.tight_layout(w_pad=1.8)
fig.savefig(OUT / "fig8_law_matrix.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig8_law_matrix.png", bbox_inches="tight")
print("fig8_law_matrix saved")
