# Firmware fixes for the Rev A board (2026-11-01)

Implements the firmware side of `Microcontroller-PCB/datasheets/ISSUES.md`. Host tests: `python3 -m pytest tests/host` (9 pass). **Nothing here has run on hardware yet.** Follow the bring-up order in CLAUDE.md and confirm each step on the board.

| Issue | What changed | Where |
|---|---|---|
| #5 CH4/CH5 floating | `MCP_CH_ENABLED` excludes CH4/5 (unless `BODGE_PICKUP_AMPLITUDE`). Optional per-coil frequency counters on GP5/GP7 behind `BODGE_SQ_TO_GP5_GP7` | config.py, freq.py |
| #6 GPIO22 even pin | `OscFC0`: sets GPIO22 to FUNCSEL 9 (clocks_gpin_1) and measures it with the on-chip frequency counter FC0 (SRC 7, 32 ms interval, ±62.5 Hz). `freq.self_test()` checks the clk_ref assumption against `machine.freq()`. PIO edge counter available as a fallback (`FREQ_METHOD = "pio"`) | freq.py |
| #7 backlight corners | PWM at 1 kHz, duty clamped to `BL_MAX_DUTY = 0.75` | board.py |
| #8 ADC loading | Pico ADC (VDD A/B, passive) read in 16-sample bursts, at least 5 ms apart per channel. Per-channel gain calibration saved in cal.json | picoadc.py, cal.py, sensors.py |
| #11 phase offset | `phase_deg(code, phi0)` plus `cal.phase_zero()`; `PHASE_REQUIRE_CAL` flag | sensors.py, cal.py |
| #15 thermistor faults | `ntc_temp_c` returns `open` (≥ 4090) or `short` (≤ 5) instead of a bogus temperature. B = 3435 K confirmed from the Vishay datasheet | sensors.py |
| #16 floating GPIOs | `init_unused_pins()` puts pull-ups on GP4–9 and GP20/21 (GP5/7 are skipped if the SQ bodge is fitted) | board.py |
| — divider ratio | VDD = 11 × V_pin (100k/10k), not 9.2 as in the old brief | config.py, sensors.py |

**Register addresses used (RP2350 datasheet):**
- CLOCKS base 0x40010000; FC0 registers at offsets 0x08C–0x0A8 (p.499 list; FC0_SRC Table 616)
- IO_BANK0 base 0x40028000; GPIO22_CTRL at offset 0x0B4, FUNCSEL 9 = clocks_gpin_1
- FC0 interval vs accuracy: Table 574, p.476

**First things to try on hardware:**
1. `import freq; freq.self_test()`. It should return `(True, ~150000, 150000.0)`.
2. With a function generator at 3.3 V into J9: `freq.OscFC0().read_hz()` should read about 13.56e6.

## Datasheet update (2026-11-02)
Every value below cites its page in `Microcontroller-PCB/datasheets/pdf`, or is tagged [web], [calc] or [netlist].
- **config.py**, new section "Datasheet-derived limits":
  - MCP3208 timing (p.3)
  - LCD SPI clock, reset timing and vendor init sequence (st7565r p.64–65, nhd_c12864lz p.13, command codes st7565r p.50)
  - LCD/backlight limits (nhd_c12864lz p.7)
  - NTC tolerance and time constant (ntcs0603e3 p.1)
  - RP2350 ADC ENOB and input impedance (p.1339), GPIO thresholds (p.1337)
  - Nexperia Schmitt thresholds [web], pickup window [calc]
- **mcp3208.py** (new): 3-byte frame per Fig 6-1/p.19, CS-high time, and it refuses the undriven CH4/CH5.
- **st7565.py** (new): vendor init, write-only SPI at ≤ 10 MHz, ≥ 10 µs reset pulse, contrast kept across the 5 s RF re-init, page/column addressing per Table 16.
- **picoadc.py**: drives GPIO23 high during ADC bursts (SMPS PWM mode lowers ADC-supply ripple, pico2 p.15).
- **CLAUDE.md** (brief) corrected against the schematic: 100k/10k ÷11 on the Pico ADC, τ = 1.0 ms, B confirmed, GPIO22/FC0, CH4/5 not driven, LCD init/timing, 75 % backlight cap.
- **Tests:** `tests/host/test_drivers.py` (6 new), 15 total passing.
