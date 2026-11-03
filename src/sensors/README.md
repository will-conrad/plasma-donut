# sensors/

Converts driver readings into real units, with fault detection:
- Temperatures (NTC thermistors) — `../../docs/parts/ntcs0603e3.md`
- Coil supply voltages (divider math)
- A/B phase difference (XOR + RC filter output) and phase calibration
- Oscillator frequency

See `../../docs/ISSUES.md` and `../../docs/design-requirements.md` for limits.
