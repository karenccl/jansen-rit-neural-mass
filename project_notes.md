# Project notes

## Question
How does constant external input (p) affect the amplitude and dominant frequency of the output of a single-column Jansen–Rit model?

## Design
p = 90, 120 and 150 pulses/s, all other parameters at the Jansen & Rit (1995) values. I compare time series, peak-to-peak amplitude and power spectra, and check the transient, the solver and the initial conditions.

## Out of scope
Fitting real EEG; modelling stimulation (TMS, tDCS, TUS); coupled columns; stochastic input; formal bifurcation analysis.

## Simplification
The original model used random input. I use constant input so each run is deterministic. No inferential statistics are needed because the simulations are deterministic, so differences are exact, not sampled.

## Model in my own terms
The model represents one cortical column as three average populations: pyramidal cells, excitatory interneurons and inhibitory interneurons. External input enters as extra excitation onto the pyramidal cells (the y4 equation). I analyse v = y1 − y2, the net pyramidal membrane potential. There are six states because each of the three PSP filters is second order (a potential and its rate of change). Sketch: `model_sketch.svg`.

- S(v0) = e0 = 2.5 s⁻¹, because at v = v0 the sigmoid is at half its maximum (2·e0).
- Removing p changes only the y4 equation.
- The inhibitory filter uses b = 50 s⁻¹ (20 ms) because inhibitory PSPs are slower than excitatory ones (a = 100 s⁻¹, 10 ms).
- Limitation: this is the model's population output, not a recording at a scalp electrode.

## Design choices
- Flat threshold 0.1 mV is practical, not a standard; below it the peak frequency is NaN.
- The 1–40 Hz band excludes the DC component.
- `nperseg` = 4096 gives about 0.24 Hz resolution, so peaks are not reported more precisely.
- Fixed 1000 Hz `t_eval` grid because Welch needs evenly spaced samples.
- Base code adapted from the project guide, with command-line options for run name and solver.
- Environment: Python 3.13 virtual environment, NumPy 2.5.4, SciPy 1.18.1.

## Observations (from saved outputs)
- Single p = 120 run: finished without warnings; a regular train of sharp spikes (about 1.2 to 11 mV) with a spectral peak near 2.4 Hz and harmonics.
- Baseline: p = 90 flat; p = 120 9.944 mV, 2.44 Hz; p = 150 2.646 mV, 10.74 Hz. Amplitude is not monotonic in p and the waveform changes shape.
- Transient rule (5%): passed for all p; largest difference 0.24% at p = 150. Settings kept: 20 s, 5 s excluded.
- Solver rule (same label, amplitude within 1%, peak within one bin): strict RK45 and LSODA agree at every p.
- Initial conditions: at p = 120 two stable behaviours exist (9.944 mV, 2.44 Hz versus 2.065 mV, 10.50 Hz, persisting 300 s). p = 150 is the same from all starts. At p = 90 from the p = 150 end state the oscillation decays slowly (0.65 to 0.20 mV over 300 s): unresolved.
- C2 test idea (0.8C to 0.9C): the three tests never use C2, so they would still pass; they check the sigmoid and where p enters, not the connectivity constants.

## Questions I should be able to answer
1. The model is a column as three average populations; the output is net pyramidal membrane potential, not a scalp recording.
2. Six states: three second-order PSP filters.
3. I varied p, which enters the pyramidal excitatory PSP equation (y4).
4. Time series show waveform shape; spectra show the dominant frequency and harmonics.
5. As p increased: flat, then large slow spikes, then a smaller 10.7 Hz near-sinusoid.
6. The transient and solver checks changed nothing; the initial-condition check showed two stable behaviours at p = 120.
7. If the starting state selects the behaviour, differences between conditions are not purely due to p.
8. I cannot conclude anything about real EEG, stimulation or noisy input.
