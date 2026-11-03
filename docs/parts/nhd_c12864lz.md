# NHD-C12864LZ-FSW-FBW-3V3

| | |
|---|---|
| Manufacturer | Newhaven Display |
| Role on board | 128x64 COG LCD module, ST7565R, 4-wire SPI, white LED backlight |
| Ref des | DS1 |
| Datasheet | [pdf/nhd_c12864lz.pdf](../pdf/nhd_c12864lz.pdf) · text [text/nhd_c12864lz.txt](../text/nhd_c12864lz.txt) · 15 pages |
| Revision | Rev 12 (10/30/2023) |
| Source | https://newhavendisplay.com/content/specs/NHD-C12864LZ-FSW-FBW-3V3.pdf |
| Requirements / checks | REQ-12, REQ-13, REQ-16; DC-02, DC-03, DC-04, DC-13, DC-17 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- DS1 on SPI1: SCL GP10, SI GP11, A0 GP12, /CS GP13, /RES GP15. /WR,/RD tied to VCC; C86 and PS tied to GND (serial). C5–C13 1 µF on VOUT/CAP/V0–V4 ✓ per nhd p.6.
- Backlight: +5V → R1 24 Ω → LED → Q1.

## Gotchas and design notes

- VDD max is **3.3 V** (p.7), so the 3.3 V rail sits right at the limit. The ST7565R's absolute max is 3.6 V (st7565r p.56).
- Input-high threshold is 0.8·VDD = 2.64 V. The Pico drives about 3.3 V into this light load, so it's fine (DC-03).
- Backlight: 60–100 mA at about 3.0 V (2.7–3.3 V). It is current-driven, and the max current must not be exceeded (p.7, see DC-13).
- Operating temperature is −20 to **70 °C** (p.7), lower than the board's other parts.
- The required external caps are 1 µF on VOUT and the CAP pins, and 1.0–2.2 µF on V0–V4 (p.6). Confirm they're all on the BOM.
- The example init (p.13) sends C8 and then C0, so the second command overrides the first. Also, 0x40 is 'display start line = 0', not an 'operating mode' as the comment says. Tune contrast with 0x81 + the volume byte.
- The serial timing diagrams on pp.9–12 are images. Use the ST7565R tables (st7565r p.64).

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| power | Supply voltage | VDD | 2.7 | 3.0 | 3.3 | V |  | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |
| power | Supply current | IDD | 0.2 | 0.5 | 2.0 | mA | VDD = 3.0 V | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |
| power | LCD drive (contrast) voltage | VLCD | 8.2 | 8.5 | 8.8 | V | 25 °C, generated internally | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |
| digital | Input high | VIH | 0.8·VDD |  | VDD | V | = 2.64 V at 3.3 V | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |
| digital | Input low | VIL | VSS |  | 0.2·VDD | V |  | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |
| backlight | LED backlight current | ILED | 60 | 80 | 100 | mA | drive by current, not voltage | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |
| backlight | LED backlight voltage | VLED | 2.7 | 3.0 | 3.3 | V | ILED = 80 mA | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |
| thermal | Operating temperature | TOP | -20 |  | 70 | °C |  | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |
| pinout | 28-pin LCD connector |  |  |  |  |  | 1 /CS1, 2 /RES, 3 A0, 4 /WR, 5 /RD, 6–11 DB0–DB5 (NC in serial), 12 DB6=SCL, 13 DB7=SI, 14 VDD, 15 VSS, 16 VOUT, 17–21 charge-pump caps, 22–26 V4–V0, 27 C86, 28 PS (L = serial) | [p.6](../pdf/nhd_c12864lz.pdf#page=6) |
| passives | Charge-pump and bias caps |  |  | 1 |  | µF | VOUT, CAP pins 1 µF; V0–V4 1.0–2.2 µF to VSS | [p.6](../pdf/nhd_c12864lz.pdf#page=6) |
| mechanical | Connector pitch |  |  | 1.27 |  | mm | LCD pins; backlight pins 1.5 mm wide; breakout NHD-PCB40 | [p.6](../pdf/nhd_c12864lz.pdf#page=6) |
| firmware | Example init sequence |  |  |  |  |  | A2, A0, C8, C0, 40, 25, 81, 19, 2F, AF (note C8 is immediately overridden by C0) | [p.13](../pdf/nhd_c12864lz.pdf#page=13) |
| optical | Response time (rise) | Tr |  | 150 |  | ms |  | [p.7](../pdf/nhd_c12864lz.pdf#page=7) |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
