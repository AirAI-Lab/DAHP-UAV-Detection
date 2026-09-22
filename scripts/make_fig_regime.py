#!/usr/bin/env python3
"""Generate the exposure-aware resolution/rebalancing matrix figure."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


OUT = Path("paper/figures")
OUT.mkdir(parents=True, exist_ok=True)
C = {
    "blue": "#0072B2",
    "green": "#009E73",
    "red": "#D55E00",
    "orange": "#E69F00",
    "grey": "#7F7F7F",
    "black": "#000000",
    "sky": "#56B4E9",
}
plt.rcParams.update(
    {
        "font.size": 8,
        "axes.titlesize": 8.3,
        "axes.labelsize": 8,
        "xtick.labelsize": 7.4,
        "ytick.labelsize": 7.4,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.grid": True,
        "grid.alpha": 0.22,
        "grid.linewidth": 0.4,
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

res = [640, 960, 1280, 1600, 1920]
base = [27.27, 28.17, 36.20, 38.07, 35.67]
union = [27.48, 31.98, 36.25, 38.85, 39.50]
matched = [None, None, None, None, 39.01]
delta = [u - b for u, b in zip(union, base)]
regime = ["unlearn.", "under-fit", "volume-sat.", "sweet", "expos.-lim."]

# Exact 960/1280-px controls use one external COCO md100 evaluator within each triplet.
exact_labels = [
    "base", "random\nvolume", "targeted\nunion",
    "base", "random\nvolume", "targeted\nunion",
]
exact_ap = [28.1009, 31.7702, 31.9239, 34.6296, 34.7233, 35.1223]

fig, (ax1, ax2, ax3) = plt.subplots(
    1,
    3,
    figsize=(7.16, 2.45),
    gridspec_kw={"width_ratios": [1.18, 0.86, 0.88]},
)

# (a) Legacy native resolution-sampling matrix.
ax1.plot(res, base, "s--", color=C["grey"], ms=4.8, lw=1.3, label="base", zorder=3)
ax1.plot(
    res,
    union,
    "o-",
    color=C["red"],
    ms=5.1,
    lw=1.5,
    label="+union @ same epoch",
    zorder=4,
)
matched_res = [r for r, m in zip(res, matched) if m is not None]
matched_ap = [m for m in matched if m is not None]
ax1.plot(
    matched_res,
    matched_ap,
    "X",
    color=C["black"],
    ms=6.7,
    mec="white",
    mew=0.8,
    label="base@120 (exposure-matched)",
    zorder=5,
)
ax1.annotate(
    "matched residual\n+0.49 AP",
    xy=(1920, 39.01),
    xytext=(1510, 40.35),
    fontsize=6.5,
    ha="center",
    arrowprops={"arrowstyle": "->", "lw": 0.7, "color": C["black"]},
)
for r, b, u, d in zip(res, base, union, delta):
    color = C["green"] if d > 0.5 else (C["grey"] if abs(d) < 0.5 else C["red"])
    ax1.annotate(f"+{d:.2f}", (r, (b + u) / 2 + 0.8), fontsize=6.2, ha="center", color=color)
ax1.set_xlabel("Input resolution (px)")
ax1.set_ylabel("mAP50-95 (native)")
ax1.set_xticks(res)
ax1.legend(frameon=False, loc="lower right", fontsize=6.5)
ax1.set_title("(a) Resolution-sampling matrix", loc="left", fontweight="bold")

# (b) Same-epoch union effect and regime labels.
colors = [C["grey"], C["green"], C["grey"], C["blue"], C["orange"]]
ax2.bar(range(5), delta, color=colors, width=0.62, zorder=3)
for i, (d, rg) in enumerate(zip(delta, regime)):
    ax2.text(i, d + 0.10 if d >= 0 else d - 0.32, f"{d:+.2f}", ha="center", fontsize=6.8)
    ax2.text(i, -0.88, rg, ha="center", fontsize=5.5, rotation=38, color="#444444")
ax2.axhline(0, color=C["black"], lw=0.7)
ax2.set_xticks(range(5))
ax2.set_xticklabels([str(r) for r in res])
ax2.set_ylabel("ΔAP of union sampling")
ax2.set_ylim(-1.05, 4.55)
ax2.set_title("(b) Same-epoch effect", loc="left", fontweight="bold")

# (c) Exact md100 triplets: volume-dominated 960 vs volume-saturated 1280.
bar_colors = [C["grey"], C["sky"], C["red"]]
bar_colors = bar_colors * 2
ax3.bar(range(6), exact_ap, color=bar_colors, width=0.62, zorder=3)
for idx, value in enumerate(exact_ap):
    ax3.text(idx, value + 0.16, f"{value:.2f}", ha="center", fontsize=6.5)

for x0 in (0, 3):
    ax3.annotate(
        "",
        xy=(x0 + 1, exact_ap[x0 + 1]),
        xytext=(x0 + 1, exact_ap[x0] + 0.04),
        arrowprops={"arrowstyle": "-", "lw": 0.8},
    )
    ax3.annotate(
        "",
        xy=(x0 + 2, exact_ap[x0 + 2]),
        xytext=(x0 + 2, exact_ap[x0 + 1] + 0.04),
        arrowprops={"arrowstyle": "-", "lw": 0.8},
    )

ax3.text(1.18, (exact_ap[0] + exact_ap[1]) / 2, "+3.67 volume", fontsize=6.0, va="center", color=C["blue"])
ax3.text(2.18, (exact_ap[1] + exact_ap[2]) / 2, "+0.15\n targeted", fontsize=6.0, va="center", color=C["red"])
ax3.text(4.18, (exact_ap[3] + exact_ap[4]) / 2, "+0.09 volume", fontsize=6.0, va="center", color=C["blue"])
ax3.text(5.18, (exact_ap[4] + exact_ap[5]) / 2, "+0.40\n targeted", fontsize=6.0, va="center", color=C["red"])
ax3.axvline(2.62, color="#BBBBBB", lw=0.7, ls="--")
ax3.text(1.0, 34.90, "960: volume-dominated", ha="center", fontsize=6.4, fontweight="bold")
ax3.text(4.3, 34.90, "1280: volume-saturated", ha="center", fontsize=6.4, fontweight="bold")
ax3.set_xticks(range(6))
ax3.set_xticklabels(exact_labels)
ax3.set_ylabel("AP (md100; axis truncated)")
ax3.set_ylim(27.30, 35.75)
ax3.set_xlim(-0.58, 5.72)
ax3.tick_params(axis="x", labelsize=6.2)
ax3.set_title("(c) Exact 960 / 1280 controls", loc="left", fontweight="bold")

fig.tight_layout(w_pad=1.35)
fig.savefig(OUT / "fig8_regime_matrix.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig8_regime_matrix.png", bbox_inches="tight")
print("fig8_regime_matrix saved")
