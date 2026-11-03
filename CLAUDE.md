# Plasma Donut — Pico 2 firmware brief

This is the handoff for writing the control-board firmware for the **Plasma Donut** capstone (UVA ECE, Fall 2026). Read the whole file before writing code.

> **Datasheet update 2026-11-02.** This brief has been corrected against the real schematic and the datasheet catalogue (part notes in `docs/parts/`; full PDFs + `search.py` in the OneDrive `CAPSTONE/Microcontroller-PCB/datasheets/`). Follow the claim-tag rules in `docs/RULES.md`: `(part p.N)` = cited datasheet page, `[netlist]` = KiCad fact, `[calc]`, `[web]`, `[assumed]`. Pin map: PINMAP.md. Firmware fixes: FIXES.md.

## The project in one paragraph
A sealed glass torus of low-pressure xenon is ionized by an HV "sparker" and sustained by a 13.56 MHz class E oscillator driving two flat coils (A above, B below), with a passive stabilization coil in the middle. Will Conrad owns the **low-voltage control board**: a Raspberry Pi Pico 2 that reads temperatures, coil supply voltages, pickup-coil frequencies and the A–B phase difference, and shows them on a 128×64 LCD you page through with two buttons. The HV boards belong to Brennan Coleman (oscillator/drivers) and Alexis Easton (sparker); Alexis also helps on firmware.

**Milestone 2 (target: the week before Thanksgiving, about Nov 19 2026):** heat-sensor data, ADC pickup data and signal taps all integrated in firmware and pageable on the LCD.

## Ground rules
1. **The firmware only monitors.** It reads sensors and drives the LCD, backlight and USB log. Oscillator VDD is set by a hardware potentiometer, not by the MCU. If you find any GPIO that reaches the HV boards as an *output* (an enable, a gate, a relay), report it to Will. Leave it as a high-impedance input until he says otherwise.
2. **The pin map comes from the schematic.** Never guess or reuse a "typical" Pico pinout (Step 0 below).
3. **Don't touch the KiCad files.** Treat them as read-only.
4. **Teach as you go.** Will wants explanations that walk through each piece step by step and refer back to earlier steps. Write all math in LaTeX. Cite the datasheet section for any spec you depend on.
5. **Build in small steps.** Use the bring-up order below and get Will to confirm each step on hardware before you move on.

## Hardware on the control board (as of Oct 2026)
| Part | Role |
|---|---|
| Raspberry Pi Pico 2 (RP2350, SC1631) | MCU, powered from USB or the 5 V input (LM66100 ideal-diode input protection) |
| MCP3208 | 8-channel 12-bit SPI ADC; its reference is net `/VREF_ADC` |
| NHD-C12864LZ-FSW-FBW-3V3 | 128×64 COG LCD with an ST7565R controller, 4-wire SPI |
| AO3400A | Low-side FET for the LCD backlight (R1 = 24 Ω, ~72–83 mA) |
| NTCS0603E3103FLT ×4 | 10 kΩ NTC thermistors: MOSFET A, MOSFET B, coil A, coil B |
| 100k/10k dividers ×2 (R23/R8, R24/R9) | Coil VDD taps A and B → **Pico ADC0/ADC1 (GPIO26/27)**, ratio 11 [netlist] |
| Nexperia 74LVC1G17GV-Q100 ×2 (U4, U5) + 74LVC1G86GV XOR (U3) + R20 10k / C26 0.1 µF | Squares up the coil A/B taps; XOR phase detector, filtered output to MCP3208 CH6 [netlist] |
| R14 330 Ω | Oscillator tap J9 → **GPIO22**, the only frequency input. The coil pickups do not reach any GPIO [netlist] |
| BAT54WS peak detector (D1, C36/C37, C38, R30/R31) | Passive-coil amplitude → Pico ADC2 (GPIO28) [netlist] |
| 2 buttons | UI |

Net naming: **`VCC` = the 3.3 V rail** (Pico 3V3 out). `GND` and `GNDA` are separate pours.

## Step 0: build the pin map from the schematic
Schematic: `~/Library/CloudStorage/OneDrive-UniversityofVirginia/Acedemics/2026/Fall 26/CAPSTONE/Microcontroller-PCB/Microcontroller-PCB.kicad_sch`. The folder was renamed once, so if it isn't there, search under `Fall 26` for `Microcontroller-PCB.kicad_sch`.

Easiest route: `kicad-cli sch export netlist --format kicadxml` (KiCad 10; KiCad 9 can't read these files), then parse it. Otherwise parse the S-expressions directly. Produce `config.py` with one constant per GPIO, plus a table for Will in this form: **GPIO → net name → function**.

Check and report each of these:
- **Frequency inputs**: which GPIOs are they, and are they **odd-numbered**? Only PWM **B** pins (GPIO 1, 3, 5, …) can count input edges in hardware (RP2040/RP2350 datasheet, PWM chapter). If any input sits on an even GPIO, use a PIO edge counter for it instead.
- **MCP3208 channels**: which net goes to each of CH0–CH7, and which SPI peripheral and pins (SCK/MOSI/MISO/CS) it uses.
- **LCD**: the SI, SCL, A0 (data/command), /CS1 and /RES pins, the backlight FET gate pin, and whether the LCD shares an SPI bus with the ADC.
- **Buttons**: their pins, and whether there are external pull-ups or pull-downs. Because of **RP2350 erratum E9**, internal pull-downs are unreliable, so use pull-ups and active-low buttons. Tell Will if the hardware is wired for pull-down.
- **`/VREF_ADC`**: answered. It is VCC through R3 = 10 Ω with C16 0.1 µF + C17 10 µF, so ≈ 3.3 V minus ≤ 14 mV [netlist][calc]. It feeds only the MCP3208 and the thermistor dividers; the VDD taps use the Pico's own ADC.
- **Thermistor dividers**: the fixed resistor value, and whether the NTC is on the top or the bottom of the divider.
- **Phase detector**: the gate type (XOR?) and its supply, and the values of **R19 and R22**. The sim recommended changing them to 7.15 kΩ; if they are still 10 kΩ, the phase reading saturates near 147°.
- **Anything else**: any GPIO connected to the HV board connector that isn't listed above (see ground rule 1).

**Stop after Step 0 and have Will confirm the table.**

## Language and tools
- **MicroPython** (the RP2350 / Pico 2 build). Deploy with `mpremote`. Will can also use Thonny.
  - Why: the data rates are slow (the phase filter takes ≈ 8.3 ms to settle and the display refreshes at 5 Hz), the REPL makes hardware bring-up fast, and the team can read Python.
  - The 13.56 MHz counting is done by the PWM or PIO hardware, so Python speed doesn't limit it.
- Keep the conversion math in pure Python with no `machine` imports, so `pytest` can run it on the Mac without the board.

Suggested layout:
```
pico-firmware/
  CLAUDE.md          (this file)
  src/  main.py config.py mcp3208.py st7565.py freq.py sensors.py ui.py cal.py
  tests/host/        (pytest: conversions, button state machine)
  tests/hw/          (one tiny script per bring-up step)
```
Calibration values live in `cal.json` on the Pico's filesystem.

## Drivers

### MCP3208 (Microchip DS21298E)
- **SPI mode 0,0** (mode 1,1 also works).
- **Clock:** 1.0 MHz max at 2.7 V and 2.0 MHz max at 5 V (mcp3208 p.3). At 3.3 V, use **1 MHz**. Keep the clock ≥ 10 kHz or the sample cap droops (mcp3208 p.3, note 3). CS must stay high ≥ 500 ns between conversions (t_CSH, mcp3208 p.3).
- **3-byte transaction** (mcp3208 p.21, Figure 6-1; config bits p.19), single-ended mode:
  - Send `[0x06 | (ch >> 2), (ch & 0x03) << 6, 0x00]`.
  - Result = `((rx[1] & 0x0F) << 8) | rx[2]`.
  - Byte 1 is five leading zeros, the start bit, SGL = 1, then D2.
- Oversample 16 times per reading and average.
- **Channel map [netlist]:** CH0 MOS A, CH1 MOS B, CH2 Coil A, CH3 Coil B, **CH4/CH5 not driven (never display)**, CH6 phase, CH7 spare (J14). Implemented in `src/mcp3208.py`.

### LCD: ST7565R, 4-wire SPI
- **Memory layout:** 8 pages × 128 columns, one byte = 8 vertical pixels, which matches MicroPython `framebuf.MONO_VLSB`.
- **Initialization (nhd_c12864lz p.13):** hardware reset, then `A2` (1/9 bias), `A0` (ADC normal), `C8`+`C0` (the vendor sends both; the second wins, so COM = normal), `40` (start line 0), `25` (resistor ratio 5), `81 19` (electronic volume 0x19), `2F` (all power circuits on), `AF` (display on). Command codes are in st7565r p.50, Table 16. Tune contrast with the volume byte on the hardware. Implemented in `src/st7565.py`.
- **SPI:** write-only (st7565r p.24), SI sampled on the rising edge, MSB first, so mode 0 works. Clock period ≥ 50 ns at 3.3 V and ≥ 100 ns at 2.7 V (st7565r p.64), so run at **≤ 10 MHz**. /RES low pulse ≥ 1 µs at 3.3 V (st7565r p.65).
- **Supply:** VDD max is 3.3 V (nhd_c12864lz p.7), so the 3.3 V rail is at the limit. Operating temperature is −20 to 70 °C (p.7).
- **RF immunity:** the LCD sits near a 13.56 MHz field, so re-send the init sequence every ~5 s and redraw. This recovers from RF-induced glitches without anyone noticing.
- **Backlight:** PWM on the AO3400A gate (GP14) at about 1 kHz. **Duty capped at 75 %** (ISSUES #7): the LED max is 100 mA (nhd_c12864lz p.7) and R1's rating is 0.25 W (yageo_rc_l p.6).

### Frequency counter
- **Hardware counter:** in PWM counter mode (DIVMODE = rising edge of B), the counter advances on each rising edge of the B pin. Both the high and low periods must be longer than one system-clock period, so the input must be below $f_{sys}/2$, which is 75 MHz at the RP2350's 150 MHz default. 13.56 MHz is fine.
- **16-bit wrap:** at 13.56 MHz the counter wraps every ~4.8 ms. Either use the clock divider as a prescaler or count wraps.
- **Targets:** resolution ≤ 1 kHz, update ≥ 2 Hz. Measure the actual gate time with `ticks_us()` and compute $f = \frac{\text{edges}}{t_{gate}}$.
- **Channels as built [netlist]:** only the oscillator tap (GPIO22). GPIO22 is an even pin (PWM A), so PWM counting can't be used on it (rp2350 p.980). Use **GPIN1 + the FC0 frequency counter** instead (GPIO22 FUNCSEL 9, rp2350 p.19; FC0 Table 574 p.476), or a PIO counter; both are in `src/freq.py`. Per-coil f_A/f_B needs the docs/REWORK.md step E bodge (TP3→GP5, TP4→GP7). Δf = 0 by design, because one crystal drives both coils.
- **"Oscillating?" flag:** true when the oscillator tap reads within 13.56 MHz ± 5%. Put the window in `config.py`.

## Conversions (sensors.py; unit-test these on the host)
Let $N$ be the 12-bit code and $V_{ref}$ the `/VREF_ADC` voltage. Then $V_{pin} = \frac{N}{4096}V_{ref}$.

**Coil VDD (100k/10k divider, Pico ADC0/ADC1) [netlist]:**
$$V_{DD} = V_{pin}\cdot\frac{100\,\text{k}\Omega + 10\,\text{k}\Omega}{10\,\text{k}\Omega} = 11\,V_{pin}$$
The full-scale reading is $3.3 \times 11 = 36.3$ V [calc]. Also report $\Delta V_{DD} = V_{DD,A} - V_{DD,B}$.
- The RP2350 ADC's input impedance is only ≥ 100 kΩ (rp2350 p.1339) against a 9.1 kΩ source, so read in **16-sample bursts ≥ 5 ms apart** and apply a per-channel gain calibration (`src/picoadc.py`, `cal.json`). ENOB is 9–9.5 bits (rp2350 p.1339), so expect a step of about 70 mV [calc].

**Thermistors (Beta model):**
$$\frac{1}{T} = \frac{1}{T_0} + \frac{1}{B}\ln\!\left(\frac{R}{R_0}\right),\quad R_0 = 10\,\text{k}\Omega,\; T_0 = 298.15\,\text{K},\; B = 3435\,\text{K}$$
- $B$ = 3435 K is **confirmed** as the B25/85 value, ±1 %, and R25 is ±1 % for the …103**F**L**T** part (ntcs0603e3 p.1). Above 85 °C the Beta model drifts; use Vishay's R-T table if that range matters. The thermal time constant is < 4 s (ntcs0603e3 p.1).
- $R$ comes from the divider. If the NTC is on the bottom with $R_{fix}$ on top and the divider is fed from $V_{ref}$, the reading is ratiometric:
$$R = R_{fix}\cdot\frac{N}{4096 - N}$$
  This is the topology on the board: R4–R7 10k on top from /VREF_ADC, NTC on the bottom [netlist]. An open cable reads ≈ 4095 and a short ≈ 0, so flag those.
- Expected resolution: about 0.025 °C/LSB at 25 °C and 0.12 °C/LSB at 100 °C.
- Labels: MOS A, MOS B, Coil A, Coil B.

**Phase A–B** (assuming an XOR-type detector averaged by the RC filter; confirm in Step 0):
$$\phi = 180^\circ\cdot\frac{V_{pin}}{V_{logic}} - \phi_0$$
- The result is a magnitude, 0–180°, with no lead/lag sign.
- **Settling:** $\tau = R_{20}C_{26} = 10\,\text{k}\Omega \times 0.1\,\mu\text{F} = 1.0$ ms, and 1-LSB settling is $\tau\ln 4096 \approx 8.3$ ms [calc]. Don't trust a reading taken sooner than 10 ms after the signal changes.
- **$\phi_0$ is the zero-phase calibration offset.** The Nexperia t_pd is 0.7–5.5 ns at 3.0–3.6 V and 50 pF [web: Nexperia 74LVC1G17 Table 9], so the U4/U5 mismatch alone can reach ~23° (1 ns = 4.9° at 13.56 MHz) [calc]. Calibration is required, at the real operating amplitude.
- **Amplitude mismatch also skews the reading.** The Schmitt hysteresis delays each edge by about $\arcsin(0.275/A)$, where $A$ is the tap's peak amplitude. With A at 1 V pk and B at 0.7 V pk the error is about −7°. Show a "?" next to phase if $|V_{DD,A} - V_{DD,B}|$ is large; Will can set the threshold.

**Calibration routine (Setup page → "Zero phase"):**
1. Prompt the user to feed the same signal to both inputs.
2. Average for 2 s.
3. Save $\phi_0$ to `cal.json`.

## UI
- **Buttons:** both active-low, with 20 ms software debounce.
  - **Button 1** short press: next page.
  - **Button 2** short press: the page's action. Long press (>800 ms): back, or exit a menu.
- **Status bar** (top line): page n/5, an "OSC" indicator, and a warning flag.

| Page | Shows |
|---|---|
| 1 Overview | Oscillating? f_osc, VDD A/B, hottest sensor, phase A–B |
| 2 Temps | MOS A, MOS B, Coil A, Coil B (°C) |
| 3 Coils | VDD A, VDD B, ΔVDD; f A, f B, Δf |
| 4 Phase | φ (deg), raw volts, φ₀, settled/unsettled |
| 5 Setup | backlight %, contrast, zero-phase cal, about/version |

**Over-temperature warning:** a per-sensor threshold in `config.py`. Use 80 °C as a **placeholder** until Brennan confirms the real MOSFET and coil limits. When it trips, invert the status bar and blink the backlight. **Monitor only:** don't switch anything off.

## Main loop
A cooperative scheduler using `time.ticks_ms()`, with no threads:
- buttons every 10 ms
- ADC sweep every 50 ms
- frequency gate running continuously and read when done
- LCD redraw at 5 Hz
- LCD re-init every 5 s
- **USB CSV log line** at 2 Hz, for bench data capture and Milestone 2 evidence. Columns: `t_ms, T_mosA, T_mosB, T_coilA, T_coilB, VDD_A, VDD_B, f_A, f_B, f_osc, phase`.

Add a `machine.WDT(timeout=2000)`, fed once per loop.

## Bring-up order (each step has a script in `tests/hw/` and is confirmed by Will on hardware before the next)
1. REPL and onboard LED blink.
2. Buttons: print presses to the REPL.
3. LCD: init, then show "Hello Donut". Tune contrast.
4. Backlight PWM sweep.
5. MCP3208: print all 8 raw codes, with a channel tied to VCC (≈4095) and to GND (≈0) as sanity checks.
6. Conversions against a multimeter: bench supply into a VDD tap; finger or heat gun on a thermistor.
7. Frequency counter with a function generator at 1 MHz, 10 MHz and 13.56 MHz.
8. Phase: same signal to both inputs, then calibrate. Then a known shift (a coax delay or a 2-channel generator).
9. The full UI pages and the CSV log.
10. On the live HV rig: watch for LCD glitches, ADC noise and counter jitter with the oscillator running.

## Open questions (ask Will; don't guess)
- Is there any MCU-controlled on/off or enable line? The MVP describes an "on/off switch integrated into the LCD".
- What are the real over-temperature limits per part?
- Does the passive stabilization coil tap go to the ADC, to a frequency input, or both?
- ~~Has the R19/R22 = 7.15 kΩ fix been applied?~~ Yes, in the schematic [netlist]. The parts are on order 8 (in transit).
- What pickup amplitudes reach J16/J17? With R25/R26 ≈ ÷34, the Schmitt works cleanly for about **17–47 V pk at the terminals** [calc, DC-08]. Rescale options are in docs/REWORK.md step D.

## Sources
- **Local datasheet catalogue (primary):** part notes + `specs.csv` in `docs/parts/`; PDFs and `search.py` in OneDrive `CAPSTONE/Microcontroller-PCB/datasheets/`, with page-verified citations in the `(part p.N)` form.
- Microchip MCP3204/3208 datasheet, DS21298E: https://www.microchip.com/content/dam/mchp/documents/APID/ProductDocuments/DataSheets/21298e.pdf
- Newhaven NHD-C12864LZ-FSW-FBW-3V3 (ST7565R, 4-wire SPI): https://newhavendisplay.com/128x64-graphic-cog-lcd-fstn-display-with-white-side-backlight/
- Vishay NTCS0603E3 datasheet, doc 29056 (B25/85 = 3435 K ±1 %): local pdf/ntcs0603e3.pdf p.1
- RP2350 PWM counter mode, B-pin input: rp2350 p.980 (verified in the local catalogue; replaces the earlier RP2040 web link)
- RP2350 erratum E9: rp2350 p.1359 (Appendix D.5.1), local catalogue
- Control-board SPICE results (2026-09-30): Claude project doc `claude/sim-results-control-board.md`
