# 74LVC1G86GV (Nexperia)

| | |
|---|---|
| Manufacturer | Nexperia |
| Role on board | XOR phase detector (SQ_A ⊕ SQ_B) |
| Ref des | U3 |
| Datasheet | **not cached**, download: https://assets.nexperia.com/documents/data-sheet/74LVC1G86.pdf |
| Revision | Rev 15 (13 Nov 2024) |
| Source | https://assets.nexperia.com/documents/data-sheet/74LVC1G86.pdf |
| Requirements / checks | REQ-07; DC-10 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- U3 XORs SQ_A and SQ_B; output (TP5) → R20 10k / C26 0.1 µF (τ = 1.0 ms) → MCP3208 CH6 (/PHASE, TP6). Average = VCC·φ/180°.

## Gotchas and design notes

- Same Nexperia PDF caveat as U4/U5.
- Two spares on hand (3 bought, 1 used).

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| pinout | SOT753 (GV) pinout |  |  |  |  |  | 1 B, 2 A, 3 GND, 4 Y, 5 VCC — matches U3 pads | p.3 |
| absmax | VCC / VI |  | -0.5 |  | 6.5 | V |  | p.4 |
| digital | VIH / VIL |  | 2.0 |  | 0.8 | V | VCC 2.7–3.6 V (min VIH / max VIL) | p.5 |
| digital | VOH at −100 µA | VOH | VCC−0.1 |  |  | V | light load (R20 10k into C26) | p.5 |
| digital | VOL at 100 µA | VOL |  |  | 0.10 | V |  | p.5 |
| timing | Propagation delay A/B→Y | tpd | 0.5 | 2.3 | 5.0 | ns | VCC 3.0–3.6 V, CL = 50 pF | p.6 |
| power | Power dissipation capacitance | CPD |  | 25 |  | pF | VCC = 3.3 V | p.6 |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
