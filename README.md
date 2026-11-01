# Single-column Jansen–Rit model: effect of constant input

## Question

How does constant external input p change the amplitude and dominant frequency of the output of a single-column Jansen–Rit model?

## Model overview

Three populations (pyramidal, excitatory interneurons, inhibitory interneurons), six state variables, output v = y1 − y2. Parameters from Jansen & Rit (1995); p enters only the y4 equation. Input is constant (the original used noise), so runs are deterministic. Code adapted from the reference implementation in the project guide.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; use source .venv/bin/activate elsewhere
pip install -r requirements.txt
```

## How to run

```bash
python -m pytest -q tests
python simulate_jr.py --run-name baseline
python simulate_jr.py --run-name strict --solver strict
python simulate_jr.py --run-name lsoda --solver lsoda
python check_robustness.py
python check_initial_conditions.py
python check_long_settling.py
```

## Outputs

- `results/<run>/`: `summary.csv`, `timeseries_p*.csv`, `input_comparison.png`, `run_info.json` (settings and versions) for `baseline`, `strict`, `lsoda`.
- `results/transient_check.csv`, `solver_comparison.csv`, `full_traces.png`: Steps 7–8.
- `results/initial_conditions.csv` and `.png`, `long_settling.csv`: Step 9.

## Main findings

From zeros: p = 90 is flat; p = 120 gives a slow spike-like oscillation (9.94 mV peak-to-peak, 2.44 Hz); p = 150 gives a near-sinusoidal oscillation (2.65 mV, 10.74 Hz). At p = 120 a second stable oscillation (2.07 mV, 10.50 Hz) exists, reached from the p = 150 end state, so the result depends on the starting state. See `report.md`.

## Checks

Transient (5% rule passed), solver (strict RK45 and LSODA agree), initial conditions (dependence at p = 120; p = 90 from the p = 150 state decays very slowly and is unresolved).

## Limitations

One model, three inputs, constant input, no real EEG, no stimulation modelling, threshold choices (0.1 mV, 1–40 Hz), no formal bifurcation analysis.

## Sources and acknowledgements

Jansen & Rit (1995); Grimbert & Faugeras (2006); SciPy `solve_ivp` and `welch` documentation.

## Licence

MIT (see `LICENSE`).
