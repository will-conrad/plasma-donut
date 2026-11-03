# Control board: requirements ↔ circuit ↔ datasheet checks (v2)

**Board:** Plasma Donut control board, `Microcontroller-PCB` (schematic saved 2026-10-22 17:43, PCB saved 22:46)
**Rebuilt:** 2026-11-01. Every value below comes from the real netlist (`kicad-cli 10.0.8`), the datasheets in this folder, and the parts orders.
**Tool results:** ERC 0 errors · DRC 0 errors · schematic↔PCB parity 0 issues. One unconnected pad remains (A1 pad D2, the debug GND), which is Will's intentional deletion on 10-08.

How to read this file:
- Each design check (DC-xx) shows its math and cites PDF pages, using the `part p.N` keys from `specs.csv`.
- Status: ✅ meets spec · ⚠ marginal or needs a bench check · ❌ violates a datasheet limit somewhere in the expected operating range.
- Fixes are in [ISSUES.md](ISSUES.md), and they only use parts already bought.

---

## 1. Signal map: what the board actually does
(Read this first; several things differ from the firmware brief.)

| Function | Path (from netlist) | Ends at |
|---|---|---|
| Temps ×4 | J3–J6 NTC (off-board) ↔ R4–R7 10k from /VREF_ADC (via JP1–4) · C18–C21 0.1 µF | MCP3208 CH0–3 |
| Coil VDD A/B | J11/J12 → R23/R24 100k → R8/R9 10k to GNDA · C22/C23 0.1 µF | **Pico ADC0/1 (GPIO26/27)**, ratio ÷11 |
| Passive coil level | J10 → C36 10 pF / C37 330 pF (R29 1k bleed) → D1 BAT54WS → C38 0.1 µF ∥ R30 100k → R31 10k | **Pico ADC2 (GPIO28)** |
| Coil A/B squaring | J16/J17 → R25/R27 10k → R26/R28 330 Ω to GND → C30/C34 1 nF → bias 10k/7.15k → U4/U5 | SQ_A/SQ_B → U3 + TP3/TP4 **only** |
| Phase A–B | U3 XOR → R20 10k / C26 0.1 µF | MCP3208 CH6 |
| Pickup A/B "ADC" | /PICKUP_A, /PICKUP_B: **only C24/C25, nothing drives them** | MCP3208 CH4/5 (floating) |
| Oscillator tap | J9 → R14 330 Ω | **GPIO22** (even pin: no PWM edge count) |
| Spare analog | J14 → R13 1k / C27 | MCP3208 CH7 |
| LCD | SPI1: GP10 SCL, GP11 SI, GP12 A0, GP13 /CS, GP15 /RES; backlight +5V → R1 24 Ω → LED → Q1 (GP14, R2 100k pull-down) | DS1 |
| Buttons | GP2/GP3, R16/R17 10k pull-ups, C28/C29 100 nF, switch to GND | SW1/SW2 |
| Power | J1 → U2 LM66100 (CE = VOUT) → +5V → **Pico VSYS (pin 39)**; Pico VBUS pin unconnected; VCC = Pico 3V3 | — |
| VREF | VCC → R3 10 Ω → /VREF_ADC (C16 0.1 µF + C17 10 µF to GNDA) | MCP3208 VREF + thermistor tops |
| Grounds | GND and GNDA pours with **no net-tie on the PCB**. They only meet inside the Pico (AGND pin 33) and through the MCP3208 (AGND→GNDA, DGND→GND) | — |

---

## 2. Requirements traceability

| ID | Requirement | Implemented by | Checks | Status |
|---|---|---|---|---|
| REQ-01/02 | Temps: MOSFET A/B, coil A/B | NTC dividers → MCP3208 CH0–3 | DC-04, DC-05 | ✅ |
| REQ-03 | Surface-mount heat sensors | NTCS0603 (0603) | — | ✅ |
| REQ-04 | VDD of each coil | ÷11 dividers → Pico ADC0/1 | DC-07 | ✅ up to 36 V (calibrate) |
| REQ-05 | ΔVDD in software | firmware | — | ✅ |
| REQ-06 | Drive and passive oscillator frequency; both coil pickups | Only J9 → GPIO22. Coils A/B and the passive coil have **no frequency path** | DC-10, DC-11, DC-12 | ⚠ only f_osc measurable as built (fixes in ISSUES) |
| REQ-07 | Phase A–B | Schmitt ×2 → XOR → RC → CH6 | DC-08, DC-09 | ⚠ amplitude window, calibrate |
| REQ-08 | "Oscillating?" flag 13.56 MHz ±5 % | GPIO22 | DC-11 | ✅ needs PIO counter or GPIN1+FC0 |
| REQ-09 | Monitor only; no MCU output to the HV boards | Every connector except J1/J15 is an input | — | ✅ verified in netlist |
| REQ-10 | Power from USB or 5 V | LM66100 + Pico VBUS Schottky ORing into VSYS | DC-01, DC-02 | ⚠ hot-plug overshoot |
| REQ-11 | 5 V / 3.3 V rails, VCC = 3V3 | Pico SMPS | DC-03 | ✅ |
| REQ-12 | LCD paged with 2 buttons, RF-robust | DS1 on SPI1, SW1/2 | DC-13, DC-15 | ✅ |
| REQ-13 | Dimmable backlight | Q1 + R1 | DC-14 | ⚠ R1 power at corners |
| REQ-14 | Separate GND / GNDA | two pours | DC-06 | ⚠ verify the tie point |
| REQ-15 | Decoupling caps beside their ICs | layout | DC-16 | ✅ (MCP3208 has 0.1 µF, datasheet asks for 1 µF) |
| REQ-16 | Survive conditions inside the can | LCD 70 °C, Pico 70 °C, B3F 70 °C | DC-17 | ⚠ placement |
| REQ-17 | M1: zero DRC errors. M2: data pageable by about Nov 19 | ERC/DRC clean | — | ✅ / in progress |
| REQ-18 | Low-cost discrete sensing | — | — | ✅ |

---

## 3. Design checks

### DC-01 · 5 V input path (LM66100) ⚠
- **Wiring vs datasheet:** VIN = J1, CE tied to VOUT (always-on reverse-current blocking, lm66100 p.9 ✅), 1 µF C1 at VIN (p.13 ✅), ST floating (p.3 says tie it to GND if unused; ST is an open-drain output, so floating is benign).
- **Load:** the Pico needs about 30 mA from VSYS and the backlight takes about 83 mA, so roughly 0.12 A total, against the 1.5 A rating (p.4). The drop is $0.12\,\text{A}\times95\,\text{m}\Omega \approx 11\,\text{mV}$ (p.5).
- **Overvoltage:** VIN recommended max is 5.5 V, absolute max **6 V** (p.4). Plugging a live bench supply into a ceramic-only input can ring up to about 2× the supply voltage, per Linear Tech AN88 ("Ceramic Input Capacitors Can Cause Overvoltage Transients"). For a 5 V supply that's about 10 V, which is ❌ above absolute max. → ISSUES #3.
- **ORing:** USB arrives through the Pico's internal VBUS→VSYS Schottky. J1 arrives through U2 into the same VSYS. This matches the Pico datasheet's recommended second-source scheme (pico2 p.17) ✅. Each source blocks the other from back-feeding.

### DC-02 · Supply voltage seen by the backlight and Pico ✅
Running from J1 gives $V_{+5V} \approx V_{J1} - 11\,\text{mV}$. Running from USB gives $V_{BUS} - V_{F,Schottky} \approx 4.6\text{–}4.7\,\text{V}$ (the sim used 4.7 V). VSYS allows 1.8–5.5 V (pico2 p.13) ✅.

### DC-03 · 3.3 V rail budget ✅
The recommended maximum is 300 mA (pico2 p.10). The board's own loads:

| Load | Estimate | Source |
|---|---|---|
| MCP3208 | 0.4 mA | mcp3208 p.3 |
| LCD logic | 2.0 mA max | nhd p.7 |
| U4 + U5 at 13.56 MHz | $2(C_{PD}+C_L)V f = 2(16.6+10)\,\text{pF}\cdot3.3\cdot13.56\,\text{MHz} \approx 2.4\,\text{mA}$ | nx_74lvc1g17 p.8 |
| U3 (output toggling at up to 27 MHz) | $(25+10)\,\text{pF}\cdot3.3\cdot27.1\,\text{MHz} \approx 3.1\,\text{mA}$ | nx_74lvc1g86 p.6 |
| Thermistor dividers (worst case, hot) | 4 × 0.32 mA ≈ 1.3 mA | computed below |
| Bias dividers, pull-ups | ≈ 1 mA | — |

The total is about 10 mA, roughly 3 % of the limit ($C_L$ = 10 pF is an assumed load).

### DC-04 · /VREF_ADC = VCC through R3 (10 Ω) ✅
Loads on /VREF_ADC: the MCP3208 reference (≤ 150 µA, mcp3208 p.2) plus four thermistor dividers. Each divider draws $3.3/(10\text{k}+R_{NTC})$: 0.165 mA at 25 °C, rising to 0.32 mA at 150 °C. The worst-case drop is
$$\Delta V = (4\times0.32 + 0.15)\,\text{mA}\times10\,\Omega \approx 14\,\text{mV}$$
- Thermistors are fed from /VREF_ADC itself, so they're ratiometric and this drop cancels exactly.
- The phase channel is referenced to VCC but measured against VREF, so the drop gives at most 0.4 % error, about 0.8°.
- Filter corner: $1/(2\pi\cdot10\,\Omega\cdot10\,\mu\text{F}) = 1.6\,\text{kHz}$.

If R3 isn't in hand (it was only on the "Additions" sheet), a solder bridge (0 Ω) still works. You lose the RC filter but keep the 10 µF.

### DC-05 · Thermistor channels ✅
- The topology is the firmware's assumed one: 10k on top, NTC on the bottom, $R = 10\,\text{k}\Omega\cdot\frac{N}{4096-N}$. B25/85 = 3435 K ±1 % and R25 ±1 % (ntcs p.1) confirm the constants in `config.py`.
- Resolution: $\frac{dN}{dT} = 4096\,x(1-x)\frac{B}{T^2}$ with $x = R/(R+10\text{k})$:

| T | R_NTC | °C per LSB |
|---|---|---|
| 25 °C | 10.0 kΩ | 0.025 |
| 85 °C | 1.45 kΩ | 0.082 |
| 100 °C | 987 Ω | 0.121 |
| 150 °C | 333 Ω | 0.41 |

  The -C grade INL is ±2 LSB (mcp3208 p.2), which is ±0.8 °C at 150 °C ✅.
- Sampling: each channel has 0.1 µF at the pin, so the MCP3208's 20 pF sample cap disturbs it by less than 0.1 LSB (mcp3208 p.3, p.17) ✅.
- Self-heating: $\frac{(1.65\,\text{V})^2}{10\,\text{k}\Omega}\div3\,\text{mW/K} \approx 0.09\,\text{K}$ ✅ (ntcs p.1).
- The Beta model is exact at 25 °C and 85 °C. Above 85 °C, use Vishay's R-T table if accuracy matters.
- Fault detection: an open cable reads about 4095 and a short reads about 0. Have the firmware flag both.
- The NTC leads run past 13.56 MHz coils, so RF on the cable can rectify in the ADC input diodes. Use twisted pair, and keep C18–C21 (they're the filter).

### DC-06 · Ground scheme ⚠ (bench check)
The PCB has **no net-tie** between GND and GNDA (only zones; no NT footprint). The only DC paths between them are:
1. The Pico's AGND pin 33 to its internal ground. The Pico datasheet calls AGND a separate analog plane "terminating at this pin" (pico2 p.10), and says it *can* be connected to digital ground if ADC performance isn't critical. Whether it's tied inside the module needs a meter check.
2. Through the MCP3208: AGND (pin 14) is on GNDA and DGND (pin 9) is on GND, and the two are joined inside the die by 5–10 Ω of substrate (mcp3208 p.24). The datasheet wants **both pins on the analog plane**.

If (1) turns out to be open, every GNDA return current (about 1–2 mA of thermistor and VREF current, plus whatever the VDD-tap cable grounds carry) flows through the ADC die. That shifts ADC readings and stresses the part. → ISSUES #2 (a meter check, then a bodge wire).

Also note the cable grounds: J11/J12 pin 1 are on **GNDA**, while J9/J10/J16/J17 pin 1 are on **GND**. If the HV board grounds all these cable returns together, the two grounds get tied at the far end too, creating an RF ground loop. → ISSUES #9.

### DC-07 · Coil VDD taps on the Pico ADC ✅ (calibrate)
- Ratio: $\frac{100\text{k}+10\text{k}}{10\text{k}} = 11$. With a 3.3 V full scale (rp2350 p.1339), the readable maximum is $3.3\times11 = 36.3\,\text{V}$. ENOB is 9–9.5 bits (p.1339), so the effective step is $36.3/2^{9} \approx 70\,\text{mV}$.
- **Input impedance:** RIN_ADC is at least 100 kΩ (rp2350 p.1339). Against a $100\text{k}\parallel10\text{k} = 9.1\,\text{k}\Omega$ source, continuous loading would read up to **8.3 % low**. The 0.1 µF caps C22/C23 hold the voltage if the firmware samples in short bursts: 16 samples droop it by about $16\times C_s/C_{22} < 0.05\,\%$, and it recovers with $\tau = 9.1\,\text{k}\Omega\times0.1\,\mu\text{F} = 0.9\,\text{ms}$. So sample in bursts at least 5 ms apart, and do a one-point gain calibration against a multimeter.
- **Overvoltage:** the ADC pins can take IOVDD + 0.3 V (pico2 p.15), which corresponds to a coil VDD of 39.6 V. Above that, the current injected into 3V3 is small: at 48 V, $(48-3.6)/100\text{k} - 3.6/10\text{k} \approx 84\,\mu\text{A}$.
- **Pico unpowered while the HV supply is live:** the tap voltage leaks through the ADC pin diode into the dead 3V3 rail (pico2 p.15). Power the control board first. → ISSUES #10.
- The dividers are 1 % Yageo resistors (yageo p.5). The resistors give ±2 % ratio error worst case, which calibration removes.

### DC-08 · Coil-pickup squaring chain ⚠ (bench-measure the amplitudes)
Transfer at 13.56 MHz: R25 = 10k, then R26 = 330 Ω in parallel with (C30 1 nF + bias Thevenin $10\text{k}\parallel7.15\text{k} = 4.17\,\text{k}\Omega$). Computed:
$$\left|\frac{V_A}{V_{J16}}\right| = 0.0293 \;(\approx \div 34),\qquad V_B = 3.3\cdot\frac{7.15}{17.15} = 1.376\,\text{V},\qquad f_{HPF} \approx 35\,\text{kHz}$$
The Nexperia thresholds at VCC = 3.0 V are VT+ 1.29–1.71 V and VT− 0.88–1.24 V (nx_74lvc1g17 p.6). The input swings $V_B \pm A$:
$$A_{min} = \max(1.71 - 1.376,\; 1.376 - 0.88) = 0.50\,\text{V pk} \;\Rightarrow\; \textbf{17 V pk at J16/J17}$$
$$A_{max,\,in\text{-}spec} = V_B = 1.38\,\text{V pk (input stays} \ge 0\text{ V, p.5)} \;\Rightarrow\; \textbf{47 V pk at J16/J17}$$
- Above 47 V pk the input clamps below 0 V. That's within absolute max as long as $I_{IK} \le 50\,\text{mA}$ (p.4), and R25/R27 keep it in the low-mA range, so the part survives. Duty cycle distorts, though, which shifts the phase reading.
- **R25/R27 power:** almost the whole pickup voltage sits across them. At 1/8 W (yageo p.5), the limit is $V_{rms} \le \sqrt{0.125\times10^4} = 35\,\text{V}$, about **50 V pk** ❌ if the pickup is larger.
- **Window: about 17–47 V pk at the pickup terminals.** Nobody has measured the real pickup amplitude yet. → ISSUES #4 (rescale with resistors you own).

### DC-09 · Phase detector ⚠ (calibrate)
- $\bar V = V_{CC}\,\frac{\phi}{180^\circ}$. U3's output stays within 0.1 V of the rails at this light load (nx_74lvc1g86 p.5). Resolution is $180^\circ/4096 = 0.044^\circ$ per LSB.
- Filter: $\tau = R_{20}C_{26} = 1.0\,\text{ms}$ (not the 2.1 ms in the brief). Settling to 1 LSB takes $\tau\ln4096 = 8.3\,\text{ms}$, and ripple at 27 MHz is negligible.
- **U4/U5 skew:** $t_{pd}$ = 0.7–5.5 ns at 50 pF (nx_74lvc1g17 p.8). That's 4.88° per ns at 13.56 MHz, so a worst-case 4.8 ns spread gives **up to 23°** of offset. U3's own rise/fall asymmetry (0.5–5.0 ns, nx_74lvc1g86 p.6) adds duty error on top.
- **Bias vs threshold centre:** the typical window centre is $(1.5+1.0)/2 = 1.25\,\text{V}$, but the bias is 1.376 V. The 0.13 V offset skews duty by roughly $\frac{1}{\pi}\arcsin(0.13/A)$, which is about 4 % at A = 1 V pk.
- All of this is fixed by the firmware's zero-phase calibration (same signal into both inputs), **done at the operating amplitude**.

### DC-10 · Coil A/B frequency ❌ not routed
SQ_A/SQ_B reach only U3 and TP3/TP4, and no GPIO counts them. Because one crystal drives both coils (team decision), $f_A = f_B = f_{osc}$ by construction, so Δf is zero by design and f_osc on GPIO22 covers REQ-06. To *prove* each coil is switching, there's a bodge: TP3 → GP5 (PWM2 B), TP4 → GP7 (PWM3 B) on J15. These are odd pins on separate slices (rp2350 p.976, p.980). → ISSUES #5.

### DC-11 · Oscillator tap on GPIO22 ⚠
- GPIO22 is even (PWM3 A), so PWM edge counting is impossible (rp2350 p.980). But **GPIO22 is also GPIN1**, a clock input up to 50 MHz (rp2350 p.19). The on-chip frequency counter FC0 can measure it with 62.5 Hz accuracy in 32 ms (p.476), which is far tighter than the ±678 kHz "oscillating?" window. Alternatively use a PIO edge counter. No hardware change is needed either way.
- **Levels:** the oscillator ordered on order 8 (IQD LFSPXO025876) is a **5 V HCMOS** 13.56 MHz part (Digi-Key listing). GPIO22 is a fault-tolerant pin: 5.5 V absolute max with IOVDD = 3.3 V present, but **3.63 V with the Pico unpowered** (rp2350 p.1336). VIH is 2.0 V ✅. → ISSUES #6 (power order, or a divider made from 1k resistors).
- E9: the source is low-impedance (330 Ω from a CMOS output), so the leakage doesn't matter ✅.

### DC-12 · Passive-coil peak detector ⚠ (bench-measure the amplitude)
- Divider: $k = \frac{C_{36}}{C_{36}+C_{37}} = \frac{10}{340} = 0.0294$ (0.0286 including D1's $C_J$ = 10 pF, bat54ws p.2). R29 makes a high-pass corner at $1/(2\pi\cdot1\,\text{k}\Omega\cdot340\,\text{pF}) = 468\,\text{kHz}$ ✅.
- Reading: $V_{C38} \approx k\,V_{pk} - V_F$, with $V_F \approx 0.24\,\text{V}$ at about 0.1 mA (bat54ws p.2).
  - Full scale (3.3 V) is reached at $V_{pk} \approx 120\,\text{V}$.
  - The ADC pin starts injecting current at $V_{pk} \approx 130\,\text{V}$.
  - Below about 10 V pk, the reading is dominated by the diode threshold.
- D1 reverse voltage is about $2kV_{pk} \le 30\,\text{V}$, so $V_{pk} \le 510\,\text{V}$ (bat54ws p.2). C36 is ordered as 500 V C0G.
- Decay: $\tau = R_{30}C_{38} = 10\,\text{ms}$, which suits 20 Hz updates.
- Loading: RIN_ADC behind R31 needs the same burst-sampling rule as DC-07.
- **Window: about 10–120 V pk.** It's amplitude only; there's no frequency path.

### DC-13 · LCD interface ✅
- Pinout matches nhd p.6: serial mode (PS = C86 = GND), /WR and /RD to VCC, C5–C13 1 µF at every pump and bias pin ✅.
- VDD 3.3 V is at the maximum of the 2.7–3.3 V range (nhd p.7). The ST7565R absolute max is 3.6 V (st7565r p.56) ⚠.
- VIH is 0.8·VDD = 2.64 V. The Pico drives about 3.3 V into this light load ✅ (rp2350 p.1337).
- SPI1 is used only by the LCD. It's write-only (st7565r p.24) and can run up to 20 MHz (p.64); 10 MHz is recommended.
- The X7R charge-pump caps lose some capacitance at V0 ≈ 8.5 V. KEMET's datasheet has no DC-bias curve (kemet_x7r p.1), and the NHD sheet asks for 1.0–2.2 µF. Low risk.

### DC-14 · Backlight ⚠
$I = \frac{V_{+5V} - V_{LED}}{24\,\Omega}$ with VLED = 2.7–3.3 V (nhd p.7), and $P_{R1} = I^2\cdot24\,\Omega$ against a rating of 0.25 W at 70 °C (yageo p.6):

| V+5V | VLED 3.3 V | VLED 3.0 V | VLED 2.7 V |
|---|---|---|---|
| 4.6 V (USB) | 54 mA / 0.07 W | 67 mA / 0.11 W | 79 mA / 0.15 W |
| 5.0 V (J1) | 71 mA / 0.12 W | **83 mA / 0.17 W** | 96 mA / 0.22 W ⚠ |
| 5.25 V | 81 mA / 0.16 W | 94 mA / 0.21 W | 106 mA / 0.27 W ❌ |
| 5.5 V | 92 mA / 0.20 W | 104 mA / 0.26 W ❌ | 117 mA / 0.33 W ❌ |

Q1 is fully on with a 3.3 V gate: VGS(th) ≤ 1.45 V and R_DS(on) ≤ 48 mΩ at 2.5 V (ao3400a p.2). R2 holds it off during boot ✅. → ISSUES #7 (firmware duty cap; keep J1 at 5.0 V).

### DC-15 · Buttons ✅
They're active-low with external 10k pull-ups, so they're immune to E9 (rp2350 p.1359) ✅. RC = 1 ms, and B3F bounce is ≤ 5 ms (omron p.3), so 20 ms software debounce is ample. The B3F is rated for at least 1 mA (p.3), while the pull-up gives 0.33 mA plus the cap-discharge pulse. That's acceptable for a demo.

### DC-16 · Decoupling placement (from PCB coordinates) ✅
| IC pin | Nearest cap on the same net | Datasheet asks |
|---|---|---|
| U1 VDD | C15 0.1 µF at 2.8 mm | 1 µF (mcp3208 p.23) ⚠ add or stack a 1 µF |
| U1 VREF | C16 0.1 µF at 2.4 mm, C17 10 µF at 4.3 mm | — ✅ |
| U3 / U4 / U5 VCC | C33 / C32 / C35 0.1 µF at 2.5–3.2 mm | ✅ |
| DS1 VDD | C4 1 µF at 2.3 mm | ✅ |
| U2 VIN / VOUT | C1 1 µF at 3.4 mm / C2 10 µF at 3.9 mm | 1 µF (lm66100 p.13) ✅ |

### DC-17 · Thermal ⚠
The LCD (−20 to 70 °C, nhd p.7), the Pico (70 °C recommended ambient, pico2 p.13) and the B3F switches (≤ 70 °C, omron p.3) set a **70 °C ceiling** for the control board. Keep it out of the hot zone of the can.

### DC-18 · Pinout cross-check against datasheets ✅
| Part | Pads (netlist) | Datasheet | |
|---|---|---|---|
| U1 MCP3208 SOIC-16 | 1–8 CH, 9 DGND, 10 CS, 11 DIN, 12 DOUT, 13 CLK, 14 AGND, 15 VREF, 16 VDD | mcp3208 p.15 | ✅ |
| U2 LM66100 SC-70-6 | 1 VIN, 2 GND, 3 CE, 4 NC, 5 ST, 6 VOUT | lm66100 p.3 | ✅ |
| U3 74LVC1G86GV | 1 B, 2 A, 3 GND, 4 Y, 5 VCC | nx_74lvc1g86 p.3 | ✅ |
| U4/U5 74LVC1G17GV | 1 nc, 2 A, 3 GND, 4 Y, 5 VCC | nx_74lvc1g17 p.3 | ✅ |
| Q1 AO3400A | 1 G, 2 S, 3 D | ao3400a p.1 | ✅ |
| D1 BAT54WS | pad 1 (K) → C38 side | bat54ws p.1 | ✅ positive peak detector |
| DS1 | 1 /CS1 … 28 PS, A/K backlight | nhd p.6 | ✅ |
| A1 | symbol is "RaspberryPi_Pico" (Pico 1) with a Pico 1 datasheet link; the Pico 2 is pin-compatible | pico2 p.9 | ✅ (documentation only) |
