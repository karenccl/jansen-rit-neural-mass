"""Step 9 follow-up: is the p=90 / p=120 oscillation from the p=150 end state
a coexisting attractor, or a very slow transient? Runs 300 s and reports
peak-to-peak in successive windows.

Run:  python check_long_settling.py   -> results/long_settling.csv
"""
import numpy as np
import pandas as pd

import simulate_jr as m

_, _, end150 = m.simulate(150.0)
starts_at = (0, 20, 60, 120, 200, 280)
rows = []
for p in (90.0, 120.0):
    t, v, _ = m.simulate(p, y_init=end150, t_end=300.0)
    for a in starts_at:
        w = (t >= a) & (t < a + 20)
        rows.append({"p": p, "window_start_s": a, "ptp_mV": round(float(np.ptp(v[w])), 4)})
res = pd.DataFrame(rows)
res.to_csv("results/long_settling.csv", index=False)
print(res.pivot(index="window_start_s", columns="p", values="ptp_mV").to_string())
