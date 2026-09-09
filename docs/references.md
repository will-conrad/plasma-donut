# References

Sources used to ground the numbers and design choices in this repo. Worth
reading the primary sources directly before finalizing any dollar-value
purchase — these searches surfaced good starting points, not a substitute
for reading full datasheets/papers.

## Frequency synthesis / RPi control

- ADF4351 overview and modules (35 MHz–4.4 GHz PLL synthesizer, SPI-programmable):
  [Analog Devices ADF4351 datasheet](https://datasheet4u.com/datasheets/Analog-Devices/ADF4351/791272),
  [Tindie module listing](https://www.tindie.com/products/yihang/adf4351-signal-generator-module-35m-44ghz/)
- Working Raspberry Pi → ADF4351 control code (bit-banged SPI over GPIO):
  [davecrump/RPiADF4351 on GitHub](https://github.com/davecrump/RPiADF4351)

## Class E at GHz frequencies

- [Design of an Efficient Single-Stage and 2-Stages Class-E Power Amplifier (2.4GHz) for Internet-of-Things](https://arxiv.org/pdf/1812.01385) — single/two-stage 2.4 GHz Class E PAE figures (49.5%/53.1% experimental)
- [Design and Analysis of 2.4 GHz GaN HEMT Class E Switching RF Power Amplifier (IEEE)](https://ieeexplore.ieee.org/document/8909401) — 22 W, 64.7% PAE at 2.4 GHz
- [A wideband 0.9–2.4 GHz 25 W high-efficiency GaN RF power amplifier](https://onlinelibrary.wiley.com/doi/full/10.1002/eng2.12386) — >65% efficiency 1.3–2.4 GHz
- Parallel-circuit Class E topology background: [Switched-mode RF and microwave parallel-circuit Class E power amplifiers](https://www.researchgate.net/publication/227831715_Switched-mode_RF_and_microwave_parallel-circuit_Class_E_power_amplifiers)
- Wolfspeed GaN HEMT power devices, DC–6 GHz family:
  [CGH40025 datasheet](https://www.mouser.com/datasheet/2/90/CGH40025-1879764.pdf),
  [CGH40010 datasheet](https://www.mouser.com/datasheet/2/90/cgh40010-876424.pdf)

## 2.45 GHz plasma torches (ignition-stage precedent)

- [Performance analysis of a 2.45 GHz microwave plasma torch for CO2 decomposition in gas swirl configuration](https://iopscience.iop.org/article/10.1088/1361-6595/abaa84)
- [Generation of plasma torch by 2.45 GHz microwaves from a solid-state power amplifier](https://pubs.aip.org/aip/adv/article/9/1/015309/1069750/Generation-of-plasma-torch-by-2-45-GHz-microwaves) — solid-state (transistor) 2.45 GHz PA driving a plasma torch, higher efficiency than magnetron-driven designs; note this source describes kW-class atmospheric-pressure torches, much larger than the sealed low-pressure benchtop scale recommended here — power figures were scaled down accordingly, not copied directly
- [Design and Construction of 2.45 GHz Microwave Plasma Source at Atmospheric Pressure](https://www.researchgate.net/publication/251716162_Design_and_Construction_of_245_GHz_Microwave_Plasma_Source_at_Atmospheric_Pressure)

## Frequency-tuned matching / detuning as a control variable (sustain-stage precedent)

- [Fast and Automatic Control of a Frequency-Tuned Radiofrequency Plasma Source (Frontiers in Physics, 2019)](https://www.frontiersin.org/articles/10.3389/fphy.2019.00227/full) — reflection coefficient Γ = √(Pᵣ/Pf) computed from forward/reflected power detectors, frequency swept (not mechanically tuned) to minimize Γ, ~10 ms settling; this is the direct model for the ignition-detection and detuning control-loop approach in `control-system.md`

## Coil geometry / ICP and electrodeless lamp precedent

- [Multiple coil antenna for inductively-coupled plasma generation systems (US6463875B1)](https://patents.google.com/patent/US6463875B1/en) — two-coil ICP geometry, coupling localization by coil position
- [The effect of various coil parameters on ICP torch simulation](https://iopscience.iop.org/article/10.1088/1742-6596/208/1/012048)
- [Equivalent circuit and numerical analyses of an inductively coupled plasma torch with a tapped induction coil](https://pubs.aip.org/aip/adv/article/8/11/115208/127755/Equivalent-circuit-and-numerical-analyses-of-an)

## Xenon fill pressure / breakdown

- Rare-gas discharge fluorescent lamp efficiency vs. fill pressure (10–200 Torr window, best 20–100 Torr) — from patent literature search on electrodeless/RF-driven rare gas lamps
- [Radio Frequency and DC High Voltage Breakdown of ... (xenon RF vs. DC Paschen behavior)](https://arxiv.org/pdf/1909.05860) — RF breakdown voltages run ~30% below DC for xenon, most pronounced near the Paschen minimum

## Ignition detection hardware

- AD8318 log-amp power detector (1 MHz–8 GHz, 60 dB dynamic range) — standard part for forward/reflected power sensing in RF/plasma match systems, referenced across multiple patent and application sources found during this search
