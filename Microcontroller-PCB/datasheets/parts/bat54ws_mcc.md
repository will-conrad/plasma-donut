# BAT54WS-TP

| | |
|---|---|
| Manufacturer | Micro Commercial Components |
| Role on board | Schottky peak detector for passive-coil level |
| Ref des | D1 |
| Datasheet | [pdf/bat54ws_mcc.pdf](../pdf/bat54ws_mcc.pdf) · text [text/bat54ws_mcc.txt](../text/bat54ws_mcc.txt) · 5 pages |
| Revision | Rev 5.1 (04/23/2026) |
| Source | https://www.mccsemi.com/pdf/Products/BAT54WS(SOD-323).pdf |
| Requirements / checks | REQ-06; DC-12 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- D1: positive peak detector. J10 → C36 10 pF / C37 330 pF divider (k ≈ 0.029) with R29 1k bleed → D1 → C38 0.1 µF ∥ R30 100k (τ = 10 ms) → R31 10k → GPIO28/ADC2 (/PASSIVE_LEVEL).

## Gotchas and design notes

- Ordered as BAT54WS-TP (MCC) on order 8 because the Diodes BAT54WS-7-F was back-ordered; order 8 shipping is delayed.
- VR max 30 V: reverse voltage ≈ 2 × (divided peak) → passive coil ≤ ~500 V pk before D1 is at risk; the ADC pin limits much earlier (DC-12).
- CJ 10 pF loads the 330 pF divider leg by ~3 % — calibrate.

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| absmax | Reverse voltage | VR |  |  | 30 | V | VRRM 30 V, VR(RMS) 21 V | [p.2](../pdf/bat54ws_mcc.pdf#page=2) |
| absmax | Average forward current | IF(AV) |  |  | 200 | mA |  | [p.2](../pdf/bat54ws_mcc.pdf#page=2) |
| electrical | Forward voltage | VF |  |  | 0.24 / 0.32 / 0.40 | V | IF = 0.1 / 1 / 10 mA | [p.2](../pdf/bat54ws_mcc.pdf#page=2) |
| electrical | Junction capacitance | CJ |  |  | 10 | pF | VR = 1 V, 1 MHz | [p.2](../pdf/bat54ws_mcc.pdf#page=2) |
| electrical | Reverse current | IR |  |  | 2 | µA | VR = 25 V | [p.2](../pdf/bat54ws_mcc.pdf#page=2) |
| electrical | Reverse recovery | trr |  |  | 5 | ns |  | [p.2](../pdf/bat54ws_mcc.pdf#page=2) |
| pinout | SOD-323 |  |  |  |  |  | bar = cathode (KiCad pad 1 = K → /PASSIVE_PEAK ✓) | [p.1](../pdf/bat54ws_mcc.pdf#page=1) |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
