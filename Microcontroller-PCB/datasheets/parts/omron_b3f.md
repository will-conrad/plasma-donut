# Omron B3F-1000

| | |
|---|---|
| Manufacturer | Omron |
| Role on board | 6 mm tactile switches |
| Ref des | SW1, SW2 |
| Datasheet | [pdf/omron_b3f.pdf](../pdf/omron_b3f.pdf) · text [text/omron_b3f.txt](../text/omron_b3f.txt) · 9 pages |
| Revision | (current) |
| Source | https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf |
| Requirements / checks | REQ-12; DC-15 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- SW1/SW2 to GND with R16/R17 10k pull-ups and C28/C29 100 nF (τ = 1 ms).

## Gotchas and design notes

- Rated minimum 1 mA; pull-up gives 0.33 mA (plus the 100 nF discharge pulse). Fine for a demo; B3F-G is the low-current variant.
- Bounce ≤ 5 ms → firmware 20 ms debounce is ample.
- B3F-1000 was only on the 'Additions' sheet — confirm they're in hand.

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| electrical | Switch rating (resistive) |  | 1 |  | 50 | mA | 3–24 VDC (B3F-G variant for 100 µA) | [p.3](../pdf/omron_b3f.pdf#page=3) |
| electrical | Bounce time |  |  |  | 5 | ms |  | [p.3](../pdf/omron_b3f.pdf#page=3) |
| electrical | Contact resistance |  |  |  | 100 | mΩ | initial | [p.3](../pdf/omron_b3f.pdf#page=3) |
| thermal | Operating temperature |  | -25 |  | 70 | °C |  | [p.3](../pdf/omron_b3f.pdf#page=3) |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
