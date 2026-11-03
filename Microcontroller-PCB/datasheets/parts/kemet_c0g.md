# KEMET C0805C331G5GACTU (C0G family)

| | |
|---|---|
| Manufacturer | KEMET (Yageo Group) |
| Role on board | C0G caps: C37 330 pF (same family as C30/C34 1 nF, C36 10 pF) |
| Ref des | C30, C34, C36, C37 |
| Datasheet | [pdf/kemet_c0g.pdf](../pdf/kemet_c0g.pdf) · text [text/kemet_c0g.txt](../text/kemet_c0g.txt) · 22 pages |
| Revision | (2026) |
| Source | https://search.kemet.com/component-edge/download/datasheet/C0805C331G5GACTU.pdf |
| Requirements / checks | REQ-06, REQ-07 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- C0G (NP0) caps where value must be stable: C30/C34 1 nF coupling, C36 10 pF / C37 330 pF divider.

## Gotchas and design notes

- C0G = no DC-bias loss, so the passive-coil divider ratio is set by values (±2 % G-tolerance on C37, ±5 % J on C36) plus D1's 10 pF.

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| electrical | C0G stability |  |  | 0 ±30 ppm/°C |  |  | no DC-bias or ageing loss | [p.1](../pdf/kemet_c0g.pdf#page=1) |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
