# Yageo RC_L series (RC0805FR-07…, RC1206FR-0724RL)

| | |
|---|---|
| Manufacturer | Yageo |
| Role on board | All chip resistors |
| Ref des | R1–R31 |
| Datasheet | [pdf/yageo_rc_l.pdf](../pdf/yageo_rc_l.pdf) · text [text/yageo_rc_l.txt](../text/yageo_rc_l.txt) · 11 pages |
| Revision | V.11 (May/Jul 2020) |
| Source | https://static.chipdip.ru/lib/770/DOC034770119.pdf (mirror of Yageo RC_L V.11) |
| Requirements / checks | DC-09, DC-14 (see [design-requirements.md](../design-requirements.md), [ISSUES.md](../ISSUES.md)) |

## How it's used on this board

- Every resistor on the board (0805 = 1/8 W, R1 1206 = 1/4 W).

## Gotchas and design notes

- R1 (24 Ω 1206) runs at 0.17 W nominal and up to ~0.22–0.33 W at tolerance corners — 1206 is rated 0.25 W at 70 °C (DC-14).
- R25/R27 (0805, 1/8 W) see nearly the whole pickup voltage: limit ≈ 35 V rms / 50 V pk (DC-09).
- R23/R24 (100k 0805) are fine up to 150 V working (VDD taps).

## Key specs (from the datasheet)

| Category | Parameter | Sym | Min | Typ | Max | Unit | Conditions | Page |
|---|---|---|---|---|---|---|---|---|
| power | RC0805 rated power | P70 |  |  | 0.125 | W | at 70 °C, derate to 0 at 155 °C | [p.5](../pdf/yageo_rc_l.pdf#page=5) |
| power | RC1206 rated power | P70 |  |  | 0.25 | W | at 70 °C (R1 24 Ω) | [p.6](../pdf/yageo_rc_l.pdf#page=6) |
| electrical | RC0805 max working voltage |  |  |  | 150 | V | overload 300 V | [p.5](../pdf/yageo_rc_l.pdf#page=5) |
| electrical | RC1206 max working voltage |  |  |  | 200 | V | overload 400 V | [p.6](../pdf/yageo_rc_l.pdf#page=6) |
| electrical | TCR (1 %, 10 Ω–10 MΩ) |  |  |  | ±100 | ppm/°C |  | [p.5](../pdf/yageo_rc_l.pdf#page=5) |

_Pages are PDF page numbers (they match the `=== p.N ===` markers in the text file)._
