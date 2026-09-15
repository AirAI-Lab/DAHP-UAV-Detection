#!/usr/bin/env python3
"""期刊级图表 v2: Okabe-Ito 配色, IEEE 栏宽 (单栏3.5in/双栏7.16in), 8pt字."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path("paper/figures_v2")
OUT.mkdir(parents=True, exist_ok=True)

C = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
     "red": "#D55E00", "purple": "#CC79A7", "sky": "#56B4E9",
     "yellow": "#F0E442", "black": "#000000", "grey": "#7F7F7F"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 8, "axes.titlesize": 8.5,
    "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5, "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.4,
    "axes.spines.top": False, "axes.spines.right": False,
})
W1, W2 = 3.5, 7.16

NAMES = ["pedestrian", "people", "bicycle", "car", "van", "truck",
         "tricycle", "awning-tricycle", "bus", "motor"]
SHORT = ["ped", "peo", "bic", "car", "van", "tru", "tri", "awn", "bus", "mot"]
VAL_LBL = Path("data/VisDrone2019/VisDrone2019-DET-val/labels")


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)
    print(f"saved {name}")


def fig1():
    counts = np.zeros(10)
    sizes = []
    co = np.zeros((10, 10))
    for lp in VAL_LBL.glob("*.txt"):
        cls = set()
        for l in open(lp):
            p = l.split()
            if len(p) < 5:
                continue
            c = int(p[0])
            w, h = float(p[3]), float(p[4])
            counts[c] += 1
            sizes.append(np.sqrt(w * h) * 1280)
            cls.add(c)
        for a in cls:
            for b in cls:
                if a != b:
                    co[a, b] += 1
    for a in range(10):
        for b in range(10):
            if a != b:
                co[a, b] /= (counts[a] + counts[b] - co[a, b])
    fig, axes = plt.subplots(1, 3, figsize=(W2, 2.1))
    ax = axes[0]
    order = np.argsort(counts)[::-1]
    cols = [C["red"] if NAMES[i] in ("awning-tricycle", "tricycle", "bus") else C["blue"] for i in order]
    ax.bar(np.arange(10), counts[order], color=cols, width=0.72, zorder=3)
    ax.set_yscale("log")
    ax.set_xticks(np.arange(10))
    ax.set_xticklabels([SHORT[i] for i in order], rotation=52, ha="right")
    ax.set_ylabel("Instance count (log)")
    ax.set_title("(a) Long-tail: 56:1 head-tail ratio", loc="left", fontweight="bold")
    ax.annotate("tail", xy=(8.4, counts[order[8]]), xytext=(7.0, counts[order[0]] * 0.08),
                fontsize=7, color=C["red"],
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=0.7))
    ax = axes[1]
    sizes = np.array(sizes)
    ax.hist(np.clip(sizes, 0, 72), bins=36, color=C["sky"], edgecolor="white", linewidth=0.2, zorder=3)
    for xv, lab in ((16, "tiny\n30.8%"), (32, "small\n37.8%")):
        ax.axvline(xv, color=C["black"], ls="--", lw=0.7, zorder=4)
        ax.text(xv + 1.2, ax.get_ylim()[1] * 0.72, lab, fontsize=6.5, va="top")
    ax.set_xlabel("Equivalent side length (px @1280)")
    ax.set_ylabel("Instances")
    ax.set_title("(b) Scale: 68.6% below 32px", loc="left", fontweight="bold")
    ax = axes[2]
    pairs = sorted([(co[a, b], SHORT[a], SHORT[b]) for a in range(10) for b in range(a + 1, 10)], reverse=True)[:7]
    y = np.arange(len(pairs))[::-1]
    ax.barh(y, [p[0] for p in pairs], color=C["orange"], height=0.62, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{p[1]}-{p[2]}" for p in pairs])
    ax.set_xlabel("Co-occurrence similarity")
    ax.set_title("(c) Confusion-prone pairs", loc="left", fontweight="bold")
    fig.tight_layout(w_pad=1.6)
    save(fig, "fig1_factor_stats")


def fig2():
    labels = ["v8m-P2\n@1280\n(baseline)", "+resol.\n1280-1600", "+union\nsampling",
              "+backbone\nv8m-v8l", "+union\n@v8l", "DAHP-L\n(final)"]
    vals = [0.3634, 0.3813, 0.3882, 0.3904, 0.4006, 0.4006]
    kinds = ["base", "res", "data", "arch", "data", "final"]
    cmap = {"base": C["grey"], "res": C["blue"], "data": C["green"], "arch": C["orange"], "final": C["black"]}
    fig, ax = plt.subplots(figsize=(W1, 2.5))
    ax.bar(0, vals[0], color=cmap["base"], width=0.62, zorder=3)
    ax.text(0, vals[0] + 0.0009, f"{vals[0]:.4f}", ha="center", fontsize=7, fontweight="bold")
    for i in range(1, len(vals)):
        d = vals[i] - vals[i - 1]
        ax.bar(i, d, bottom=vals[i - 1], color=cmap[kinds[i]], width=0.62, zorder=3)
        ax.plot([i - 0.69, i - 0.31], [vals[i - 1]] * 2, color=C["grey"], lw=0.6, ls=":", zorder=2)
        ax.text(i, vals[i] + 0.0009, f"+{d:.3f}", ha="center", fontsize=7)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=6.8)
    ax.set_ylim(0.357, 0.4045)
    ax.set_ylabel("mAP50-95 (native)")
    ax.set_title("Factor-decomposed gains: +3.86 AP total", fontsize=8.5)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=cmap[k], label=l) for k, l in
               [("res", "resolution"), ("data", "data policy"), ("arch", "backbone")]],
              loc="upper left", frameon=False, fontsize=6.8)
    save(fig, "fig2_waterfall")


def fig4():
    res = [960, 1280, 1600, 1920]
    ap = [0.3009, 0.3561, 0.3768, 0.3491]
    fig, ax = plt.subplots(figsize=(W1, 2.4))
    ax.plot(res, ap, "o-", color=C["blue"], lw=1.6, ms=5.5, zorder=4)
    for r, a in zip(res, ap):
        ax.annotate(f"{a:.4f}", (r, a), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=7)
    for x0, x1, c, t in ((880, 1150, C["green"], "REGIME I\nunder-fit"),
                          (1150, 1480, C["orange"], "REGIME II\nsaturated"),
                          (1480, 1740, C["red"], "REGIME III\nsweet spot")):
        ax.axvspan(x0, x1, alpha=0.07, color=c)
        ax.text((x0 + x1) / 2, 0.2975, t, fontsize=6.2, ha="center", color=c, fontweight="bold")
    ax.annotate("-2.8 AP", xy=(1920, 0.3491), xytext=(1760, 0.365),
                fontsize=7, color=C["red"],
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=0.8))
    ax.set_xlabel("Input resolution (px)")
    ax.set_ylabel("mAP50-95 @ep60")
    ax.set_xticks(res)
    ax.set_ylim(0.293, 0.388)
    ax.set_title("Non-monotonic resolution-regime curve", fontsize=8.5)
    save(fig, "fig4_resolution_regime")


def fig5():
    base = json.load(open("results/eval/perclass_m0_mp2.json"))
    ours = json.load(open("results/eval/perclass_h9_v8l_1600_union.json"))
    b = [base[c]["AP"] for c in NAMES]
    o = [ours[c]["AP"] for c in NAMES]
    ang = np.linspace(0, 2 * np.pi, 10, endpoint=False).tolist()
    ang += ang[:1]
    fig, ax = plt.subplots(figsize=(W1, 3.0), subplot_kw=dict(polar=True))
    ax.grid(alpha=0.3, lw=0.4)
    for vals, lab, col, ls in ((b, "Baseline v8m-P2@1280", C["grey"], "--"),
                               (o, "DAHP-L (ours)", C["red"], "-")):
        v = vals + vals[:1]
        ax.plot(ang, v, ls, ms=3.2, lw=1.3, label=lab, color=col, zorder=4)
        ax.fill(ang, v, alpha=0.10, color=col, zorder=2)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(SHORT, fontsize=7)
    ax.set_ylim(0, 0.75)
    ax.set_yticks([0.2, 0.4, 0.6])
    ax.set_yticklabels(["0.2", "0.4", "0.6"], fontsize=6)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), frameon=False)
    save(fig, "fig5_radar")


def fig7():
    fig, axes = plt.subplots(1, 3, figsize=(W2, 1.95))
    ax = axes[0]
    names = ["base", "+volume\n(control)", "+freq\nsampling"]
    vals = [0.3026, 0.3156, 0.3195]
    cols = [C["grey"], C["sky"], C["green"]]
    ax.bar(names, vals, color=cols, width=0.58, zorder=3)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.0006, f"{v:.4f}", ha="center", fontsize=6.8)
    ax.annotate("", xy=(1, 0.3156), xytext=(0, 0.3026),
                arrowprops=dict(arrowstyle="->", color=C["blue"], lw=1.0))
    ax.text(0.5, 0.309, "volume\n77%", fontsize=6.2, color=C["blue"], ha="center")
    ax.set_ylim(0.298, 0.3235)
    ax.set_ylabel("mAP50-95")
    ax.set_title("(a) 960px under-fit:\nvolume-driven tail rescue", loc="left", fontsize=7.5)
    ax = axes[1]
    ax.bar(["bus", "awning-tri"], [-2.4, 1.9], color=[C["red"], C["green"]], width=0.45, zorder=3)
    ax.axhline(0, color=C["black"], lw=0.7)
    ax.text(0, -2.4 - 0.35, "-2.4", ha="center", fontsize=7)
    ax.text(1, 1.9 + 0.25, "+1.9", ha="center", fontsize=7)
    ax.set_ylabel("Delta class AP (pt)")
    ax.set_ylim(-3.4, 2.9)
    ax.set_title("(b) 1280px saturated:\nzero-sum reallocation", loc="left", fontsize=7.5)
    ax = axes[2]
    ax.bar(["$V_L$+P2\n(no sampling)", "DAHP-L\n(+union)"], [0.3904, 0.4006],
           color=[C["grey"], C["red"]], width=0.5, zorder=3)
    ax.text(0, 0.3904 + 0.0007, "0.3904", ha="center", fontsize=6.8)
    ax.text(1, 0.4006 + 0.0007, "0.4006", ha="center", fontsize=6.8, fontweight="bold")
    ax.annotate("", xy=(1, 0.4006), xytext=(1, 0.3904),
                arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.2))
    ax.set_ylim(0.386, 0.4055)
    ax.set_ylabel("mAP50-95")
    ax.set_title("(c) 1600px intermediate:\npositive-sum window", loc="left", fontsize=7.5)
    fig.tight_layout(w_pad=1.8)
    save(fig, "fig7_regime_mechanism")


if __name__ == "__main__":
    fig1(); fig2(); fig4(); fig5(); fig7()
    print("V2_ALL_DONE")
