# Project notes

## Question
How does constant external input (p) affect the amplitude and dominant frequency of the output of a single-column Jansen–Rit model?

## Design
p was set to 90, 120, and 150 pulses/s, with all other parameters at the Jansen and Rit (1995) values. Time series, peak-to-peak amplitude, and power spectra are compared across conditions, and the transient, the solver, and the initial conditions are each checked.

## Out of scope
Fitting real EEG; modelling stimulation (TMS, tDCS, TUS); coupled columns; stochastic input; formal bifurcation analysis.

## Simplification
The original model used random input. Constant input is used here so that each run is deterministic. Inferential statistics are not needed, since the simulations are deterministic and differences between conditions are exact rather than sampled.

## The model in my own terms
The model represents one cortical column as three average populations: pyramidal cells, excitatory interneurons, and inhibitory interneurons. External input enters as additional excitation onto the pyramidal cells (the y4 equation). The analysed output is v = y1 − y2, the net pyramidal membrane potential. There are six states because each of the three PSP filters is second order, comprising a potential and its rate of change. The sketch is in `model_sketch.svg`.

- S(v0) equals e0 = 2.5 s⁻¹, because at v = v0 the sigmoid is at half of its maximum (2·e0).
- Removing p would alter only the y4 equation.
- The inhibitory filter uses b = 50 s⁻¹ (20 ms), since inhibitory PSPs are slower than excitatory ones (a = 100 s⁻¹, 10 ms).
- A limitation to keep in mind is that this is the model's population output, not a recording at a scalp electrode.

## Design choices
- The flat threshold of 0.1 mV is practical rather than standard; below it, the peak frequency is NaN.
- The 1–40 Hz band excludes the DC component.
- `nperseg` = 4096 gives a resolution of about 0.24 Hz, so peaks are not reported more precisely than this.
- A fixed 1000 Hz `t_eval` grid is used because Welch's method requires evenly spaced samples.
- The base code was adapted from the project guide, with command-line options added for run name and solver.
- Environment: Python 3.13 virtual environment, NumPy 2.5.4, SciPy 1.18.1.

## Observations (from saved outputs)
- The single p = 120 run finished without warnings and showed a regular train of sharp spikes (about 1.2 to 11 mV), with a spectral peak near 2.4 Hz and harmonics.
- Baseline: p = 90 was flat; p = 120 gave 9.944 mV at 2.44 Hz; p = 150 gave 2.646 mV at 10.74 Hz. Amplitude was not monotonic in p, and the waveform changed shape.
- Transient rule (5%): passed for all p, with the largest difference (0.24%) at p = 150. The settings were therefore kept at 20 s with 5 s excluded.
- Solver rule (same label, amplitude within 1%, peak within one bin): strict RK45 and LSODA agreed with the baseline at every p.
- Initial conditions: two stable behaviours exist at p = 120 (9.944 mV at 2.44 Hz versus 2.065 mV at 10.50 Hz), persisting for 300 s. The result at p = 150 was the same from all starts. At p = 90, from the p = 150 end state, the oscillation decayed slowly (0.65 to 0.20 mV over 300 s), which remains unresolved.
- C2 test idea (0.8C to 0.9C): the three tests never use C2, so they would still pass. They check the sigmoid and where p enters, not the connectivity constants.

## Questions I should be able to answer
1. The model is a column of three average populations, and the output is the net pyramidal membrane potential, not a scalp recording.
2. There are six states because there are three second-order PSP filters.
3. The varied parameter is p, which enters the pyramidal excitatory PSP equation (y4).
4. Time series show the waveform shape, whereas spectra show the dominant frequency and harmonics.
5. As p increased, the output was flat, then showed large slow spikes, then a smaller 10.7 Hz near-sinusoid.
6. The transient and solver checks changed nothing, whereas the initial-condition check showed two stable behaviours at p = 120.
7. If the starting state selects the behaviour, differences between conditions cannot be attributed to p alone.
8. Nothing can be concluded about real EEG, stimulation, or noisy input.
