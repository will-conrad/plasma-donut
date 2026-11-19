# Bring-up log (Rev A control board)

Results of the `tests/hw/` programs on the assembled board. Steps follow the bring-up order in `../CLAUDE.md`.

## 2026-11-17

Pico 2: RP2350A rev A2 (QFN-60), flash blank on arrival (`picotool info -a`).

| Step | Program | Result | Readings |
|---|---|---|---|
| 1 Pico alive | `step1_pico` | Pass | clk_sys 150 000 kHz; VSYS 4.68 V on USB; chip sensor 19.5 °C |
| 2 Buttons | `step2_buttons` | Pass (Will) | Both read 1 released, 0 pressed; one count per tap; long press at 0.8 s |
| 3 LCD | `step3_lcd` | Pass (Will) | Orientation needs `A0` + `C8` (top-bottom flip, no column offset). Vendor contrast 0x19 gave vertical streaks; 0x13 is much better (Will) |
| 4 Backlight | `step3_lcd`, `step4_backlight` | Pass at 50 % (Will) | `step4_backlight` works (Will): BTN1 = up, BTN2 = down (`BTN_IDX_UP` in config.h), tap 5 %, hold to ramp, capped at 75 % |
| 5 MCP3208 | `step5_mcp3208` | Pass | CH0–3 ≈ 4087 (no NTCs connected); CH4/5 = 0; CH6 = 0 (no oscillator); CH7 ≈ 45 (36 mV, J14 open). Burst spread 8–14 LSB on CH0–3 |
| 6b Thermistors | `step6b_temps` | Inputs open | All four `OPEN`: NTCs not plugged in yet |
| 6a Pico ADC | `step6a_picoadc` | Pass | VDD A/B ≈ 7 codes (0.06 V) with nothing connected, so no RP2350-E9 leakage; passive level 27 mV |

### Firmware changes from this session
- `NTC_CODE_OPEN` lowered from 4090 to 4070: an open input reads 4080–4094 on this board, so 4090 would have shown an unplugged sensor as about −80 °C. −55 °C is code 4037 [calc], so no real range is lost.
- LCD orientation set to `A0` + `C8` in `src/config/config.h`; `step3_lcd` has an `o` key to cycle all four.
- LCD contrast default lowered from the vendor 0x19 to 0x13 (vertical streaks at 0x19).

- Button debounce and short/long press logic in `src/ui/buttons.c`, host-tested in `tests/host/test_buttons.c`.

### Re-check after the display demo (same day)
Readings match the first run within 1 LSB: MCP3208 CH0–3 ≈ 4087, Pico ADC ≈ 7 codes, VSYS 4.68 V. CH7 (spare) has drifted from 45 to 0 with J14 open, which is expected for a floating input.
- **Pico ADC zero offset ≈ 7 codes** (≈ 64 mV on VDD after ×11). Calibrate offset as well as gain (two-point: 0 V and a known voltage).
- **First VSYS reading after boot read 3.48 V**, then 4.68 V from the next second. Discard the first sweep after start-up.
- **MCP3208 open-input spread 9–15 LSB p-p** in a 16-sample burst. The 16-sample average brings that to about ±1.5 LSB (≈ 0.04 °C at 25 °C) [calc]. Watch it on the live rig.

## 2026-11-18: MOS A thermistor (J3, sensor on Brennan's board)
- Thermal camera read 60 °C (falling) while the board read about 20 °C. Will set a +40.0 °C offset on MOS A (`TEMP_CAL_OFFSET` in config.h). Gain left at 1.
- Same session: the board read a steady 19.9 kΩ (≈ 8 °C); a meter across the thermistor read 1380 Ω (≈ 87 °C by the Beta model); with the cable unplugged, the meter showed open between its two wires at the J3 end. The thermistor sits in parallel with a capacitor on Brennan's board.
- Second point: camera 36 °C while the board read 17.0 kΩ (shown 52 °C with the +40 offset). A fixed offset can't fit both points. **About 10 kΩ in series with the NTC fits both** within the camera's ±2 °C, so the +40 offset is replaced by `TEMP_SERIES_OHM` = 10 kΩ on MOS A (offset back to 0). With it, 17.0 kΩ reads 34.7 °C.
- **To confirm with Brennan:** is there a 10 kΩ resistor in series with the MOS A thermistor (an RC filter with its parallel cap)? If his value differs, change `TEMP_SERIES_OHM` and `SERIES` in `tools/cal_thermistors.py`.

### Still to do
- Plug in the NTCs: a 10 k resistor should read 25.0 °C, a finger should warm it.
- Bench supply into J11/J12 against a multimeter, then store the VDD gains.
- Optional: fine-tune contrast below 0x13 (`+`/`-` in `step3_lcd`), and re-check it warm, since LCD contrast drifts with temperature.
- Steps 7 (frequency counter) and 8 (phase) need firmware not written yet.
