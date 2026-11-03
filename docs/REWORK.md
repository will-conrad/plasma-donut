# Rev A rework guide (owned parts only)

These are the hardware fixes from [ISSUES.md](ISSUES.md), written as bench steps. The firmware side is already done in `CAPSTONE/pico-firmware/` (see `FIXES.md` there).

**Map:** [rework_map.png](rework_map.png) shows the top side of the board with the letters below circled.
**Coordinates** are in mm from the board's top-left corner, as you look at the top (component) side.
**Before any soldering:** KiCad doesn't need to change. All of these are bench changes to the fabricated Rev A.

---

## A · Stop-gaps while order 8 is late (ISSUES #1)
| Ref | Location | If the real part isn't here yet | When the real part arrives |
|---|---|---|---|
| R3 (10 Ω) | (33.4, 80.1), next to the 3V3 test pad | Solder bridge across the pads (0 Ω). VREF loses its RC filter but keeps C17's 10 µF | Remove the bridge, fit 10 Ω |
| R19, R22 (7.15k) | (64.2, 85.8), (64.2, 93.8) | **10k**. Bias becomes 1.65 V (the originally simulated case). The pickup then needs ≥ 26 V pk at J16/J17 | Fit 7.15k, redo phase calibration |
| C30, C34 (1 nF C0G) | (62.5, 82.5), (62.5, 90.5) | Alexis's 1 nF radial C0G (C323C102KAG5TA) with legs trimmed, or Brennan's 10 nF 0603 (GRM1885C1H103JA01D) centred on the 0805 pads | — (either works) |
| Screw terminals J1–J17 | board edges | Solder wires straight into the 5 mm holes. Square pad = pin 1 = ground | Desolder the wires, fit the terminals |
| C36 / C37 / D1 | passive-coil detector | Leave them out. The firmware reports the passive level as "none" | Fit them; D1 bar (cathode) faces C38 |

## B · Define the GND–GNDA tie (ISSUES #2), *before* first power-up
1. Fit the Pico (A1). Leave everything unpowered.
2. Meter in Ω mode: **TP7 (GND, at 40.2, 73.5) ↔ TP8 (GNDA, at 70.5, 114.5)**.
3. **< 0.5 Ω:** the Pico ties AGND to GND internally, so you're done.
4. **Higher:** solder one insulated wire from TP7 to TP8. Both are through-hole pads, so this is easy. That wire becomes the board's single GND/GNDA tie point. Don't add a second one anywhere.

## C · First power-up (ISSUES #3, #10, #14)
1. Wire J1 with the bench supply **output off**. Set it to 5.00 V with a 0.3 A limit. Then turn the output on.
2. Check **TP1 (+5V) ≈ 5.0 V** and **TP2 (3V3) ≤ 3.35 V**.
3. From now on: control board on **first**, before any HV supply, and off **last**.

## D · Pickup amplitude scaling (ISSUES #4), after scoping the real signal
1. With the rig running, scope **J16 pin 2 and J17 pin 2** to ground. Note the peak voltage $V_{pk}$.
2. Choose R25/R27 (at **(57.5, 81.7)** and **(57.5, 94.3)**) from stock:

| Works for pickup $V_{pk}$ | R25 / R27 (stock parts) | $k = \frac{306}{R+306}$ |
|---|---|---|
| 2.1–5.9 V | 1k | 0.234 |
| 3.7–10.4 V | 1k + 1k in series (tombstone) | 0.133 |
| 8.6–24 V | 10k ∥ 10k (piggyback) | 0.058 |
| 17–47 V | 10k (as built) | 0.029 |
| 33–91 V | 10k + 10k in series (tombstone) | 0.015 |
| 82–150 V | 100k ∥ 100k (above 150 V the resistors overheat) | 0.006 |

Each window is $V_{pk}$ from $0.50/k$ (worst-case Schmitt threshold) to $1.38/k$ (input reaches 0 V). Pick the row with your measured $V_{pk}$ near the middle.

3. Check: **TP3 / TP4** should show clean 0–3.3 V square waves at about 50 % duty.
4. Re-run the phase-zero calibration in firmware (same signal into both inputs).

## E · Optional: per-coil frequency (ISSUES #5)
1. Cut two insulated wires about 15 cm long. Solder a spare **330 Ω** in series at one end of each.
2. **TP3 (SQ_A, at 74.0, 81.7)** → 330 Ω → **J15 pin 7 (GP5)**.
3. **TP4 (SQ_B, at 72.5, 96.0)** → 330 Ω → **J15 pin 9 (GP7)**. J15 pin 1 is the square pad at the top.
4. Twist each wire with a ground wire (J15 pin 14 = GND).
5. In `src/config/config.h` set `#define BODGE_SQ_TO_GP5_GP7 1`. The firmware then counts f_A and f_B with PIO.

## F · GPIO22 level shift for the 5 V oscillator (ISSUES #6)
Only needed if J9 carries the raw output of the **5 V** HCMOS oscillator (LFSPXO025876). Check with Brennan.
1. Stack two **1 kΩ** 0805 resistors on top of each other (in parallel, 500 Ω).
2. Solder the pair between **A1 pad 29 (GP22, at 31.3, 30.4)** and **A1 pad 28 (GND, at 31.3, 32.9)**. These are neighbouring castellated pads, 2.5 mm apart.
3. With R14 (330 Ω) this makes a divider: $5\,\text{V}\times\frac{500}{830} = 3.0\,\text{V}$. That's above VIH (2.0 V) and safe even when the Pico is unpowered.
4. Check: scope GP22 for a clean 0–3 V square at 13.56 MHz, and confirm the firmware's f_osc reads ≈ 13.560 MHz.

## G · MCP3208 decoupling (ISSUES #12)
Stack a spare **1 µF** (C0805C105K3RACTU) on top of **C15 (27.1, 84.6)**, soldered end-to-end on the same pads.

---
**After any rework:** run the host tests (see `tests/README.md`), then follow the firmware bring-up order in `CLAUDE.md`.
