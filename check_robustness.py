"""Steps 7-8: transient rule and solver agreement, from saved run folders.

Run after: simulate_jr.py for baseline, strict and lsoda.
Writes results/transient_check.csv, results/solver_comparison.csv and
results/full_traces.png.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import simulate_jr as m

BIN_HZ = 1000 / 4096          # Welch frequency resolution

base = pd.read_csv("results/baseline/summary.csv")
strict = pd.read_csv("results/strict/summary.csv")
lsoda = pd.read_csv("results/lsoda/summary.csv")

# Step 7: rule (written before looking): early vs late ptp differing by > 5 %
# means the 5 s exclusion is inadequate.
tr = base[["p", "ptp_5to10s_mV", "ptp_15to20s_mV"]].copy()
den = tr[["ptp_5to10s_mV", "ptp_15to20s_mV"]].max(axis=1)
tr["rel_diff_pct"] = np.where(den > 0, 100 * (tr.ptp_5to10s_mV - tr.ptp_15to20s_mV).abs() / den, 0.0)
tr["adequate"] = tr.rel_diff_pct <= 5
tr.round(4).to_csv("results/transient_check.csv", index=False)
print(tr.round(4).to_string(index=False))

# Step 8: agreement rule (same label; ptp within 1 %; peak within one bin)
rows = []
for name, other in [("strict", strict), ("lsoda", lsoda)]:
    for i in range(len(base)):
        b, o = base.iloc[i], other.iloc[i]
        same = bool(b.oscillating) == bool(o.oscillating)
        ptp_ok = abs(o.ptp_mV - b.ptp_mV) <= 0.01 * max(b.ptp_mV, 1e-12) if b.ptp_mV > 0 \
            else abs(o.ptp_mV) < 1e-6
        if np.isnan(b.peak_freq_Hz) and np.isnan(o.peak_freq_Hz):
            f_ok = True
        else:
            f_ok = abs(o.peak_freq_Hz - b.peak_freq_Hz) <= BIN_HZ
        rows.append({"p": b.p, "vs": name, "same_regime": same,
                     "ptp_within_1pct": bool(ptp_ok), "peak_within_1bin": bool(f_ok)})
cmp_ = pd.DataFrame(rows)
cmp_.to_csv("results/solver_comparison.csv", index=False)
print(cmp_.to_string(index=False))

# Step 7.2: full traces with exclusion line
fig, axes = plt.subplots(3, 1, figsize=(10, 8))
for ax, p in zip(axes, [90.0, 120.0, 150.0]):
    t, v, _ = m.simulate(p)
    ax.plot(t, v, lw=0.7)
    ax.axvline(m.T_DISCARD, color="red", ls="--")
    ax.set(title=f"Full simulation, p = {p:g}", ylabel="v (mV)")
axes[-1].set_xlabel("Time (s)")
fig.tight_layout()
fig.savefig("results/full_traces.png", dpi=150)
