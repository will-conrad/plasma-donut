# KEMET C0805C105K3RACTU (X7R family)

| | |
|---|---|
| Manufacturer | KEMET (Yageo Group) |
| Role on board | 1 µF 25 V X7R: LCD charge pump, C1, C4 |
| Ref des | C1, C4–C13 |
| Datasheet | [pdf/kemet_c0805c105k3r.pdf](../pdf/kemet_c0805c105k3r.pdf) · text [text/kemet_x7r.txt](../text/kemet_x7r.txt) · 28 pages |
| Revision | C1002_X7R (2026-09-01) |
| Source | https://search.kemet.com/component-edge/download/datasheet/C0805C105K3RACTU.pdf |
| Requirements / checks | REQ-12 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- 1 µF X7R 25 V: C1 (LM66100 input), C4 (LCD VDD), C5–C13 (LCD VOUT/charge pump/V0–V4).

## Gotchas and design notes

- X7R loses capacitance under DC bias; V0 runs ≈ 8.5 V (nhd p.7). The datasheet has no DC-bias curve — use KEMET K-SIM. NHD asks for 1.0–2.2 µF on V0–V4, so effective value may sit below 1 µF (low risk: contrast stability).

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| electrical | X7R temperature stability |  | -15 |  | 15 | % | −55…+125 °C; no DC-bias curve in datasheet (use KEMET K-SIM) | [p.1](../pdf/kemet_c0805c105k3r.pdf#page=1) |
| electrical | C0805C105K3RACTU rating |  |  | 1 µF ±10 % | 25 | V |  | [p.1](../pdf/kemet_c0805c105k3r.pdf#page=1) |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
