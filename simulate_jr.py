"""Single-column Jansen-Rit model: effect of constant external input.

Run:  python simulate_jr.py
Outputs go to results/<RUN_NAME>/.
Settings can be overridden from the command line, e.g.
    python simulate_jr.py --run-name strict --solver strict
"""
import argparse
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.signal import welch
from scipy.special import expit

# ---------------------------------------------------------------
# Run settings: change these, not the code below
# ---------------------------------------------------------------
RUN_NAME = "baseline"          # output subfolder
INPUTS = [90.0, 120.0, 150.0]  # external input p (pulses/s)
T_END = 20.0                   # simulated duration (s)
FS = 1000                      # output sampling rate (Hz)
T_DISCARD = 5.0                # initial period excluded from analysis (s)
FLAT_THRESHOLD = 0.1           # peak-to-peak (mV) below which output counts as flat
SOLVER = dict(method="RK45", max_step=1e-3, rtol=1e-6, atol=1e-8)
Y_INIT = np.zeros(6)           # initial state

# Named solver presets used by the robustness checks (Step 8)
SOLVER_PRESETS = {
    "baseline": SOLVER,
    "strict": dict(method="RK45", max_step=5e-4, rtol=1e-8, atol=1e-10),
    "lsoda": dict(method="LSODA", rtol=1e-8, atol=1e-10),
}

# ---------------------------------------------------------------
# Model parameters (Jansen & Rit, 1995)
# ---------------------------------------------------------------
A, B = 3.25, 22.0              # max PSP amplitudes (mV)
a, b = 100.0, 50.0             # inverse time constants (1/s)
C = 135.0
C1, C2, C3, C4 = C, 0.8 * C, 0.25 * C, 0.25 * C
E0, V0, R = 2.5, 6.0, 0.56     # sigmoid parameters


def sigmoid(v):
    """Convert mean membrane potential (mV) to mean firing rate (1/s)."""
    # Input: potential in mV. Output: firing rate in pulses/s, between 0 and 2*E0 = 5.
    return 2.0 * E0 * expit(R * (v - V0))


def rhs(t, y, p):
    """Time derivatives of the six state variables."""
    y0, y1, y2, y3, y4, y5 = y
    # Each PSP is a second-order filter: y0, y1, y2 are potentials, y3, y4, y5 their rates.
    dy0 = y3
    dy1 = y4
    dy2 = y5
    # Eq. for y3: pyramidal firing S(y1 - y2) drives the PSP y0 seen by the interneurons
    # (excitatory filter, rate a).
    # Eq. for y4 below: excitatory PSP on pyramidal cells, driven by external input p
    # plus excitatory-interneuron firing. p appears in this line and nowhere else.
    # Eq. for y5: inhibitory PSP, slower filter (rate b < a), driven by inhibitory interneurons.
    dy3 = A * a * sigmoid(y1 - y2) - 2 * a * y3 - a**2 * y0
    dy4 = A * a * (p + C2 * sigmoid(C1 * y0)) - 2 * a * y4 - a**2 * y1
    dy5 = B * b * C4 * sigmoid(C3 * y0) - 2 * b * y5 - b**2 * y2
    return [dy0, dy1, dy2, dy3, dy4, dy5]


def simulate(p, y_init=None, t_end=None, fs=None, solver=None):
    """Integrate the model; return time, output v = y1 - y2, final state."""
    y_init = Y_INIT if y_init is None else y_init
    t_end = T_END if t_end is None else t_end
    fs = FS if fs is None else fs
    solver = SOLVER if solver is None else solver
    # Evenly spaced grid: Welch's FFT assumes a constant sample interval, but an
    # adaptive solver takes uneven steps, so t_eval resamples onto a fixed 1000 Hz grid.
    t_eval = np.arange(0.0, t_end, 1.0 / fs)
    sol = solve_ivp(rhs, (0.0, t_end), y_init, args=(p,),
                    t_eval=t_eval, **solver)
    if not sol.success:
        raise RuntimeError(f"Integration failed for p={p}: {sol.message}")
    # Output v = y1 - y2: excitatory minus inhibitory PSP = net pyramidal membrane potential.
    return sol.t, sol.y[1] - sol.y[2], sol.y[:, -1]


def _ptp(x):
    """Peak-to-peak range, or NaN if the window is empty."""
    return np.ptp(x) if x.size else np.nan


def summarise(t, v, p, fs=None, windows=((5, 10), (15, 20))):
    """Amplitude and spectral summary of the post-transient output."""
    fs = FS if fs is None else fs
    keep = t >= T_DISCARD            # drop 0-5 s: the settling from the initial state
    vk = v[keep]
    ptp = np.ptp(vk)
    f, pxx = welch(vk, fs=fs, nperseg=min(4096, vk.size))   # resolution fs/4096 = 0.24 Hz
    band = (f >= 1.0) & (f <= 40.0)
    oscillating = ptp > FLAT_THRESHOLD   # "flat" means peak-to-peak <= 0.1 mV
    (e0, e1), (l0, l1) = windows
    early = _ptp(v[(t >= e0) & (t < e1)])
    late = _ptp(v[(t >= l0) & (t < l1)])
    return {
        "p": p,
        "mean_mV": vk.mean(),
        "sd_mV": vk.std(),
        "ptp_mV": ptp,
        "oscillating": oscillating,
        "peak_freq_Hz": f[band][np.argmax(pxx[band])] if oscillating else np.nan,
        f"ptp_{e0}to{e1}s_mV": early,
        f"ptp_{l0}to{l1}s_mV": late,
    }, (f, pxx)


def main(run_name=None, solver_name=None):
    run_name = run_name or RUN_NAME
    solver = SOLVER_PRESETS[solver_name] if solver_name else SOLVER
    out = Path("results") / run_name
    out.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(len(INPUTS), 2, figsize=(11, 3 * len(INPUTS)),
                             squeeze=False)
    rows = []
    for i, p in enumerate(INPUTS):
        t, v, _ = simulate(p, solver=solver)
        summary, (f, pxx) = summarise(t, v, p)
        rows.append(summary)
        pd.DataFrame({"t_s": t, "v_mV": v}).to_csv(
            out / f"timeseries_p{int(p)}.csv", index=False)

        win = (t >= T_END - 2.0)           # last 2 s for display
        axes[i, 0].plot(t[win], v[win], lw=1)
        axes[i, 0].set(title=f"p = {p:g}", xlabel="Time (s)",
                       ylabel="v = y1 - y2 (mV)")
        axes[i, 1].semilogy(f, pxx + 1e-20, lw=1)
        axes[i, 1].set(xlim=(0, 40), xlabel="Frequency (Hz)",
                       ylabel="PSD (mV²/Hz)")

    fig.tight_layout()
    fig.savefig(out / "input_comparison.png", dpi=150)
    pd.DataFrame(rows).to_csv(out / "summary.csv", index=False)

    run_info = {
        "run_name": run_name, "inputs": INPUTS, "t_end": T_END, "fs": FS,
        "t_discard": T_DISCARD, "flat_threshold_mV": FLAT_THRESHOLD,
        "solver": solver, "y_init": list(map(float, Y_INIT)),
        "python": platform.python_version(), "numpy": np.__version__,
        "scipy": scipy.__version__, "pandas": pd.__version__,
        "matplotlib": matplotlib.__version__,
    }
    (out / "run_info.json").write_text(json.dumps(run_info, indent=2))
    print(pd.DataFrame(rows).round(3).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", default=None)
    ap.add_argument("--solver", choices=list(SOLVER_PRESETS), default=None)
    args = ap.parse_args()
    main(args.run_name, args.solver)
