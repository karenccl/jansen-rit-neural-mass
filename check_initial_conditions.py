"""Step 9: does the starting state change the regime at constant p?

Run:  python check_initial_conditions.py
Writes results/initial_conditions.csv and results/initial_conditions.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import simulate_jr as m

PS = [90.0, 120.0, 150.0]
T_END = 60.0
T_ANALYSE = 40.0                      # analyse the last 20 s only

_, _, end90 = m.simulate(90.0)
_, _, end150 = m.simulate(150.0)
starts = {"zeros": np.zeros(6), "end_of_p90": end90, "end_of_p150": end150}

rows, traces = [], {}
for p in PS:
    for name, y0 in starts.items():
        t, v, _ = m.simulate(p, y_init=y0, t_end=T_END)
        late = t >= T_ANALYSE
        s, _ = m.summarise(t[late], v[late], p)
        rows.append({"p": p, "start": name,
                     **{k: s[k] for k in ["oscillating", "ptp_mV", "peak_freq_Hz"]}})
        traces[(p, name)] = (t, v)

res = pd.DataFrame(rows).round(3)
Path("results").mkdir(exist_ok=True)
res.to_csv("results/initial_conditions.csv", index=False)
print(res.to_string(index=False))

fig, axes = plt.subplots(len(PS), 1, figsize=(10, 3 * len(PS)), sharex=True)
for ax, p in zip(axes, PS):
    for name in starts:
        t, v = traces[(p, name)]
        w = (t >= 50.0)
        ax.plot(t[w], v[w], lw=0.9, label=f"start: {name}")
    ax.set(title=f"p = {p:g} (last 10 s of 60 s)", ylabel="v (mV)")
    ax.legend(loc="upper right", fontsize=7)
axes[-1].set_xlabel("Time (s)")
fig.tight_layout()
fig.savefig("results/initial_conditions.png", dpi=150)
