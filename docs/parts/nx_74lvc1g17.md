# 74LVC1G17GV-Q100 (Nexperia)

| | |
|---|---|
| Manufacturer | Nexperia |
| Role on board | Schmitt-trigger buffers squaring coil A/B taps |
| Ref des | U4, U5 |
| Datasheet | **not cached**, download: https://assets.nexperia.com/documents/data-sheet/74LVC1G17.pdf |
| Revision | Rev 16.1 (3 Sep 2024) |
| Source | https://assets.nexperia.com/documents/data-sheet/74LVC1G17.pdf |
| Requirements / checks | REQ-07; DC-09, DC-10 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- U4/U5 square up coil pickups. Path: J16/J17 → R25/R27 10k → R26/R28 330 Ω to GND (≈÷34 at 13.56 MHz) → C30/C34 1 nF → bias R18/R21 10k + R19/R22 7.15k (≈1.38 V) → A input. Outputs SQ_A/SQ_B go **only** to U3 and TP3/TP4.

## Gotchas and design notes

- Ordered part is the Nexperia **-Q100** automotive grade; thresholds differ from TI's SN74LVC1G17. Values here are Nexperia's (VCC = 3.0 V row).
- Nexperia blocks automated PDF download, so the PDF isn't in pdf/. Get it from the link and drop it in pdf/nx_74lvc1g17.pdf.
- Input below 0 V is out of recommended range; abs max allows it only if clamp current ≤ 50 mA (R25/R27 10k guarantee that). See DC-09.
- One spare on hand (3 bought, 2 used).

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| pinout | SOT753 (GV) pinout |  |  |  |  |  | 1 n.c., 2 A, 3 GND, 4 Y, 5 VCC — matches U4/U5 pads | p.3 |
| absmax | VCC / VI |  | -0.5 |  | 6.5 | V | VI negative rating may be exceeded if IIK ≤ 50 mA | p.4 |
| absmax | Input clamp current | IIK | -50 |  |  | mA | VI < 0 V | p.4 |
| power | VI (operating) | VI | 0 |  | 5.5 | V |  | p.5 |
| threshold | Positive-going threshold | VT+ | 1.29 | 1.5 | 1.71 | V | VCC = 3.0 V, −40…85 °C (no 3.3 V row) | p.6 |
| threshold | Negative-going threshold | VT− | 0.88 | 1.0 | 1.24 | V | VCC = 3.0 V | p.6 |
| threshold | Hysteresis | VH | 0.31 | 0.5 | 0.64 | V | VCC = 3.0 V | p.6 |
| timing | Propagation delay A→Y | tpd | 0.7 | 3.0 | 5.5 | ns | VCC 3.0–3.6 V, CL = 50 pF, RL = 500 Ω | p.8 |
| power | Power dissipation capacitance | CPD |  | 16.6 |  | pF | VCC = 3.3 V | p.8 |
| power | Supply current | ICC |  | 0.1 | 4 | µA | VI = rail, IO = 0 | p.5 |
| power | Extra current, input at VCC−0.6 V | ΔICC |  | 5 | 500 | µA | per input | p.6 |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
