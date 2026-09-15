#!/usr/bin/env python3
"""Two-arm ONLINE prediction test: does the early (epoch-10..40) gap of a
rebalanced arm over its matched base predict the FINAL gain? Revision must-do #2."""
import csv, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
PAIRS = {  # res -> (base run, treated run, label)
    640:  ("base_v8mp2_640", "dahpM_640", "union"),
    960:  ("s960_base", "s960_union", "union"),
    1280: ("base_v8mp2_1280", "tail_sampling_1280", "tail(freq proxy)"),
    1600: ("base_v8mp2_1600", "union_sampling_1600", "union"),
    1920: ("s1920_base", "s1920_union", "union"),
}
PROBE_EPOCHS = [10, 15, 20, 25, 30, 40, 50]

def load_map(run):
    f = BASE / "runs/detect" / run / "results.csv"
    rows = list(csv.DictReader(open(f)))
    col = next(c for c in rows[0] if "mAP50-95" in c)
    return np.array([float(r[col]) for r in rows]) * 100.0  # AP points

out = {}
for r, (b, t, lab) in PAIRS.items():
    mb, mt = load_map(b), load_map(t)
    n = min(len(mb), len(mt))
    # best-checkpoint semantics (matches the paper's best.pt protocol)
    bb = np.maximum.accumulate(mb[:n]); bt = np.maximum.accumulate(mt[:n])
    gap = bt - bb
    final = float(bt[-1] - bb[-1])
    out[r] = {"base": b, "treated": t, "treatment": lab,
              "epochs": n,
              "gap_at": {E: round(float(gap[E-1]), 3) for E in PROBE_EPOCHS if E <= n},
              "final_gap": round(final, 3),
              "gap_traj": [round(float(x), 3) for x in gap]}
    print(r, "final", round(final, 2), {E: out[r]["gap_at"].get(E) for E in (10, 20, 30, 40)})

# correlation per probe epoch
corr = {}
for E in PROBE_EPOCHS:
    xs, ys = [], []
    for r, d in out.items():
        if E in d["gap_at"]:
            xs.append(d["gap_at"][E]); ys.append(d["final_gap"])
    if len(xs) >= 3:
        rho = float(np.corrcoef(xs, ys)[0, 1])
        corr[E] = {"pearson_r": round(rho, 3), "n": len(xs),
                   "direction_accuracy": round(float(np.mean(np.sign(xs) == np.sign(ys))), 3)}
        print("E", E, corr[E])

json.dump({"pairs": out, "correlation": corr},
          open(BASE / "results/online_two_arm_prediction.json", "w"), indent=1)

# figure
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.2))
cols = {640: "#7F7F7F", 960: "#009E73", 1280: "#7F7F7F", 1600: "#0072B2", 1920: "#E69F00"}
ax = axes[0]
for r, d in out.items():
    ax.plot(range(1, len(d["gap_traj"]) + 1), d["gap_traj"], label=f"{r}px", color=cols[r], lw=1.8)
ax.axhline(0, color="k", lw=0.7)
ax.set_xlabel("epoch"); ax.set_ylabel("treated $-$ base (AP)")
ax.set_title("(a) Two-arm gap trajectories", fontsize=10)
ax.legend(fontsize=7, ncol=2)
ax = axes[1]
for E in (20, 30, 40):
    xs = [d["gap_at"][E] for d in out.values() if E in d["gap_at"]]
    ys = [d["final_gap"] for d in out.values() if E in d["gap_at"]]
    ax.scatter(xs, ys, s=26, label=f"probe@{E}ep (r={corr.get(E, {}).get('pearson_r', float('nan')):.2f})")
lim = max(abs(v) for d in out.values() for v in d["gap_traj"] + [d["final_gap"]]) * 1.1
ax.plot([-lim, lim], [-lim, lim], "k--", lw=0.7)
ax.axhline(0, color="k", lw=0.5); ax.axvline(0, color="k", lw=0.5)
ax.set_xlabel("early gap at probe epoch (AP)"); ax.set_ylabel("final gap (AP)")
ax.set_title("(b) Early gap predicts final gain", fontsize=10)
ax.legend(fontsize=7)
plt.tight_layout()
plt.savefig(BASE / "paper/figures_v2/fig9_online_regime.pdf")
plt.savefig(BASE / "paper/figures_v2/fig9_online_regime.png", dpi=300)
print("saved fig9")
