# Raspberry Pi Pico 2 (SC1631)

| | |
|---|---|
| Manufacturer | Raspberry Pi |
| Role on board | MCU module: RP2350, 3.3 V SMPS, USB |
| Ref des | A1 (SC1631) |
| Datasheet | [pdf/pico2.pdf](../pdf/pico2.pdf) · text [text/pico2.txt](../text/pico2.txt) · 24 pages |
| Revision | Build date 03/07/2026 |
| Source | https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf |
| Requirements / checks | REQ-10, REQ-11, REQ-16; DC-01, DC-06, DC-15, DC-17 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- A1. +5V (LM66100 output) → **VSYS pin 39**; VBUS pin 40 unconnected (the Pico's own VBUS→VSYS Schottky ORs USB in). This is the pico2 p.17 recommended ORing.
- 3V3 pin 36 = VCC for the whole board; ADC_VREF pin 35 unconnected (internal ADC uses the Pico's own filtered 3V3).
- Internal ADC used for VDD taps (GPIO26/27, 100k/10k ÷11) and passive level (GPIO28). AGND pin 33 = GNDA.
- Only frequency input: GPIO22 /FREQ_QUARTZ (via R14 330 Ω from J9).

## Gotchas and design notes

- Keep the 3V3 pin load under 300 mA (p.10).
- GPIO23/24/25/29 are used on the module itself (SMPS mode, VBUS sense, LED, VSYS/3) — don't route board signals to them (p.9).
- ADC_VREF is the 3V3 rail through ~201 Ω + 2.2 µF. Anything you load it with drops its voltage (p.15). See DC-06 if `/VREF_ADC` comes from this pin.
- GPIO26–29 (ADC pins) can only take IOVDD + 0.3 V and leak into 3V3 if the Pico is unpowered. GPIO0–25 don't have that limit (p.15).
- Driving GPIO23 high puts the SMPS in PWM mode, which lowers ripple on 3V3 and ADC_VREF. It's worth doing during ADC sweeps (p.15).
- Recommended max ambient is 70 °C (p.13), so keep the board away from the hot MOSFETs and coils inside the can.

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| power | VBUS input (USB) | VBUS |  | 5 |  | V | ±10% | [p.13](../pdf/pico2.pdf#page=13) |
| power | VSYS input range | VSYS | 1.8 |  | 5.5 | V | feeds RT6150 buck-boost | [p.13](../pdf/pico2.pdf#page=13) |
| power | 3V3 pin external load (recommended) |  |  |  | 300 | mA | depends on RP2350 load and VSYS | [p.10](../pdf/pico2.pdf#page=10) |
| power | 3V3_EN pull-up |  |  | 100 |  | kΩ | to VSYS; short low to disable 3.3 V | [p.10](../pdf/pico2.pdf#page=10) |
| power | VBUS→VSYS diode | D1 |  | Schottky |  |  | VSYS = VBUS − diode drop; safe to OR another source via diode/PFET | [p.16](../pdf/pico2.pdf#page=16) |
| analog | ADC_VREF filter | R7/C |  | 201 Ω / 2.2 µF |  |  | from 3V3; ~150 µA ADC draw gives ~30 mV offset | [p.15](../pdf/pico2.pdf#page=15) |
| analog | ADC_VREF external shunt option |  |  | 3.0 |  | V | LM4040 suggested; ~1.5 mA through 200 Ω | [p.15](../pdf/pico2.pdf#page=15) |
| io | ADC-capable GPIO26–29 max input |  |  |  | IOVDD+0.3 | V | internal diode to IOVDD; leaks into 3V3 if unpowered | [p.15](../pdf/pico2.pdf#page=15) |
| io | Internal-use GPIOs |  |  |  |  |  | GPIO23 SMPS PS, GPIO24 VBUS sense, GPIO25 LED, GPIO29 VSYS/3 | [p.9](../pdf/pico2.pdf#page=9) |
| pinout | Power pins |  |  |  |  |  | 40 VBUS, 39 VSYS, 37 3V3_EN, 36 3V3, 35 ADC_VREF, 33 AGND | [p.9](../pdf/pico2.pdf#page=9) |
| thermal | Operating temperature |  | -20 |  | 85 | °C | incl. self-heating; recommended max ambient 70 °C | [p.13](../pdf/pico2.pdf#page=13) |
| power | SMPS mode pin | GPIO23 |  |  |  |  | drive high = PWM mode, lower ripple on ADC_VREF | [p.15](../pdf/pico2.pdf#page=15) |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
