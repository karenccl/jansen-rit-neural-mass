# Constant input to a single Jansen–Rit column: amplitude, frequency and dependence on starting state

## Abstract

This project examined how constant external input (p) alters the output amplitude and dominant frequency of a single-column Jansen–Rit neural mass model, with all other parameters fixed at the values of Jansen and Rit (1995). From a resting initial state, p = 90 produced a flat output, p = 120 a large, slow, spike-like oscillation (9.94 mV peak-to-peak, 2.44 Hz), and p = 150 a smaller, near-sinusoidal oscillation (2.65 mV, 10.74 Hz). These results were unchanged by a longer settling period, stricter solver tolerances, or a different integrator. They were, however, dependent on the starting state: at p = 120, initialising the model from the end state of the p = 150 run yielded a different stable oscillation (2.07 mV, 10.50 Hz).

## Background

Neural mass models describe the average activity of a neural population using a small set of differential equations. The Jansen–Rit model is a compact and widely used example that generates EEG-like rhythms. Constant input was used here so that every simulation is deterministic. Jansen and Rit used random input, so this represents a deliberate simplification of the original model.

## Model

The column comprises three populations: pyramidal cells, excitatory interneurons, and inhibitory interneurons. Each synaptic connection is a second-order filter with two states (potential and rate of change), giving six states in total. External input p adds excitation to the pyramidal cells and enters through one equation only (that for y4). The output is v = y1 − y2, the net pyramidal membrane potential. Parameters were the standard values (A = 3.25 mV, B = 22 mV, a = 100 s⁻¹, b = 50 s⁻¹, C = 135, e0 = 2.5 s⁻¹, v0 = 6 mV, r = 0.56 mV⁻¹). The analysed signal is therefore the model's population output, rather than a simulated scalp recording.

## Methods

Input values were p = 90, 120, and 150 s⁻¹. Each simulation ran for 20 s from an all-zero state using SciPy `solve_ivp` (RK45, rtol 1e-6, atol 1e-8, maximum step 1 ms), with output sampled on a fixed 1000 Hz grid, and the first 5 s were excluded from analysis. Power spectra were estimated with Welch's method (4096-sample segments, frequency resolution of about 0.24 Hz), and the peak frequency was taken as the largest bin between 1 and 40 Hz. An output was classed as oscillating if its peak-to-peak range exceeded 0.1 mV, a practical threshold rather than a standard one; below it, no peak frequency was reported. Three checks were then carried out. First, for the transient check, peak-to-peak amplitude in 5–10 s was compared with that in 15–20 s, using a tolerance of 5%. Second, for the solver check, results were compared against stricter RK45 tolerances and against LSODA, and were considered to agree if the regime matched, amplitude was within 1%, and peak frequency was within one bin. Third, for the initial-condition check, each p was started from zeros and from the final states of the p = 90 and p = 150 runs, and the last 20 s of a 60 s simulation were analysed.

## Results

Baseline results are shown below (`results/baseline/summary.csv`).

| p (s⁻¹) | Oscillating | Peak-to-peak (mV) | Peak frequency (Hz) |
| --- | --- | --- | --- |
| 90 | no | 0.000 | not reported |
| 120 | yes | 9.944 | 2.44 |
| 150 | yes | 2.646 | 10.74 |

![Figure 1](results/baseline/input_comparison.png)

*Figure 1. Last 2 s of output and power spectra for each value of p.*

Amplitude was not monotonic in p, and the waveform changed abruptly between conditions: slow, sharp spikes with harmonics at p = 120, and a near-sinusoid at p = 150.

In the transient check (`results/transient_check.csv`), early and late amplitudes differed by 0% at p = 90 and 120 and by 0.24% at p = 150, indicating that the 5 s exclusion was adequate. In the solver check (`results/solver_comparison.csv`), both alternative settings met all three agreement criteria at every value of p.

The initial-condition results are summarised below (`results/initial_conditions.csv`, `results/initial_conditions.png`).

| p | start: zeros | start: end of p = 90 | start: end of p = 150 |
| --- | --- | --- | --- |
| 90 | flat | flat | 0.359 mV, 10.25 Hz (see below) |
| 120 | 9.944 mV, 2.44 Hz | 9.944 mV, 2.44 Hz | 2.065 mV, 10.50 Hz |
| 150 | 2.640 mV, 10.74 Hz | 2.640 mV, 10.74 Hz | 2.640 mV, 10.74 Hz |

At p = 120, both oscillations persisted unchanged for 300 s (`results/long_settling.csv`), indicating that two stable behaviours coexist at this input. At p = 90, started from the p = 150 end state, the oscillation was still shrinking after 300 s (from 0.65 to 0.20 mV across successive 20 s windows). This is consistent with a slow decay, but the simulation was not long enough to show it, so whether p = 90 is also bistable remains unresolved. Part of the difference between conditions therefore reflects the starting state and not p alone.

## Limitations

Several limitations should be noted. First, only one model, three input values, and constant input were examined, and no real EEG data or stimulation was modelled. Second, the 0.1 mV oscillation threshold and the 1–40 Hz analysis band were my own choices, and the conclusions may be sensitive to them. Third, no formal bifurcation analysis was performed, so the boundaries between regimes, and the nature of the slow decay at p = 90, are not established.

## References and code

- Jansen, B. H., & Rit, V. G. (1995). *Biological Cybernetics, 73*(4), 357–366.
- Grimbert, F., & Faugeras, O. (2006). *Neural Computation, 18*(12), 3052–3068.
- Code and outputs: this repository (`simulate_jr.py`, `check_*.py`, `results/`). Citation details should be checked against the originals.
