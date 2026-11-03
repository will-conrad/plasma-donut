# FLAGS: automated design check

Board: `Microcontroller-PCB` · checked 2026-11-02 02:20 · rules: [RULES.md](RULES.md) · tool: `flagcheck.py`

**3 error · 7 warn · 10 info**

Basis column: **netlist fact** (read from KiCad files) · **cited** (datasheet page, number verified on that page) · **computed** (calculated here) · **web** (secondary source, not page-verified) · **ASSUMED** (engineering assumption, needs confirmation).

| # | Sev | Rule | Where | Finding | Basis | Evidence / fix |
|---|---|---|---|---|---|---|
| 1 | error | R-B3 floating | `/PICKUP_A` | nothing drives '/PICKUP_A': only U1.5(input), C24(cap/tp) | netlist fact (netlist) | fix: connect a source, or disable the input in firmware and document it |
| 2 | error | R-B3 floating | `/PICKUP_B` | nothing drives '/PICKUP_B': only C25(cap/tp), U1.6(input) | netlist fact (netlist) | fix: connect a source, or disable the input in firmware and document it |
| 3 | error | R-F1 procurement | `unconfirmed` | 6 parts unconfirmed: C30, C34, J15, R3, SW1, SW2 | BOM-vs-orders.md (BOM-vs-orders.md) | fix: see REWORK.md step A for stand-ins |
| 4 | warn | R-B2 pinout | `U1.9` | DGND is on 'GND', datasheet expects 'GNDA' | cited (ds:mcp3208 p.24 ('both ... connected to the analog ground plane')) | PCB pad U1.9 net = GND |
| 5 | warn | R-B2 pinout | `U2.5` | ST is on 'unconnected-(U2-ST-Pad5)', datasheet expects 'GND' | cited (ds:lm66100 p.3 ('Connect to GND if not required'); open-drain output, floating is benign) | PCB pad U2.5 net = unconnected-(U2-ST-Pad5) |
| 6 | warn | R-C1 ratings | `DS1.14` | VCC up to 3.4 V exceeds recommended max 3.3 V (abs 3.6 V) | cited (ds:nhd_c12864lz p.7 (VDD 2.7-3.3 V); ds:st7565r p.56 (abs 3.6 V)) | rail basis: assumed: Pico 2 SMPS tolerance not given in pico2 DS; 3 % high allowance |
| 7 | warn | R-C2 required parts | `U1.16` | C15 0.1uF within 5.0 mm = 0.10 µF < required 1.00 µF | cited (ds:mcp3208 p.23 ('A bypass capacitor value of 1 uF is recommended')) | calc: sum of caps on the pin's net to GND/GNDA within distance |
| 8 | warn | R-C4 derating | `R1` | P = (2.8 V)^2 / 24 = 0.327 W vs rated 0.25 W at 70 °C. Firmware caps PWM duty at 75 % -> average 0.25 W. | cited (ds:yageo_rc_l p.6) | calc; voltage basis: calc: 5.5 V (+5V max) - 2.7 V (VLED min, ds:nhd_c12864lz p.7) |
| 9 | warn | R-C5 MCU pins | `/FREQ_QUARTZ` | GPIO22 is even (PWM A): no hardware edge counting. mitigated: GPIO22 = GPIN1 -> FC0 counter (ds:rp2350 p.19, p.476); see freq.py | cited (ds:rp2350 p.980) |  |
| 10 | warn | R-F1 procurement | `in_transit` | 17 parts in_transit: C36, C37, D1, J1, J10, J11, J12, J14, J16, J17, J3, J4, J5, J6, J9, R19, R22 | BOM-vs-orders.md (BOM-vs-orders.md) | fix: see REWORK.md step A for stand-ins |
| 11 | info | R-A1 provenance | `ISSUES.md` | 3/16 lines with numeric claims carry no source tag | computed (calc) | L31: 1. Bare board: meter TP7↔TP8 (issue 2) and check for shorts on +5V/VCC/VREF.; L32: 2. Power from USB only: check TP2 ≈ 3.3 V (issue 14) and TP1 ≈ 4.6 V.; L33: 3. J1 at 5.0 V, with the supply turned on *after* wiring (issue 3). · fix: tag as (part p.N), [calc], [assumed], [measured] or [web] |
| 12 | info | R-A1 provenance | `REWORK.md` | 20/22 lines with numeric claims carry no source tag | computed (calc) | L14: | R3 (10 Ω) | (33.4, 80.1), next to the 3V3 test pad | Solder bridge across the pads (0 Ω). VREF los; L15: | R19, R22 (7.15k) | (64.2, 85.8), (64.2, 93.8) | **10k**. Bias becomes 1.65 V (the originally simul; L16: | C30, C34 (1 nF C0G) | (62.5, 82.5), (62.5, 90.5) | Alexis's 1 nF radial C0G (C323C102KAG5TA) with  · fix: tag as (part p.N), [calc], [assumed], [measured] or [web] |
| 13 | info | R-A1 provenance | `design-requirements.md` | 32/85 lines with numeric claims carry no source tag | computed (calc) | L19: | Temps ×4 | J3–J6 NTC (off-board) ↔ R4–R7 10k from /VREF_ADC (via JP1–4) · C18–C21 0.1 µF | MCP3208; L20: | Coil VDD A/B | J11/J12 → R23/R24 100k → R8/R9 10k to GNDA · C22/C23 0.1 µF | **Pico ADC0/1 (GPIO26; L21: | Passive coil level | J10 → C36 10 pF / C37 330 pF (R29 1k bleed) → D1 BAT54WS → C38 0.1 µF ∥ R30 1 · fix: tag as (part p.N), [calc], [assumed], [measured] or [web] |
| 14 | info | R-A2 citation | `specs.csv` | 18 spec rows come from web-fetched datasheets (no local text): not page-verifiable | web (not page-verified) (web) | fix: download the PDFs into pdf/ and re-index |
| 15 | info | R-B3 floating | `A1.35` | ADC_VREF unconnected by design: ADC_VREF is the Pico's filtered 3V3 output/optional reference input (ds:pico2 p.10) | netlist fact (netlist) |  |
| 16 | info | R-C4 derating | `R25` | P = (33.0 V)^2 / 10k = 0.109 W vs rated 0.125 W at 70 °C. Rescale per REWORK.md D if the pickup is larger. | cited (ds:yageo_rc_l p.5) | calc; voltage basis: assumed: pickup at top of design window 47 V pk (DC-08) |
| 17 | info | R-C4 derating | `R27` | P = (33.0 V)^2 / 10k = 0.109 W vs rated 0.125 W at 70 °C. Rescale per REWORK.md D if the pickup is larger. | cited (ds:yageo_rc_l p.5) | calc; voltage basis: assumed: pickup at top of design window 47 V pk (DC-08) |
| 18 | info | R-E2 tools | `A1.D2` | unrouted: Pad D2 [GND] of A1 on F.Cu (WAIVED: Will deleted the A1.D2 GND trace on 2026-10-08; D2 is grounded inside the Pico) | netlist fact (netlist) |  |
| 19 | info | R-E2 tools | `ERC` | 0 errors | netlist fact (netlist) |  |
| 20 | info | R-F2 spares | `DS1` | only 1 LCD bought | BOM-vs-orders.md (BOM-vs-orders.md) |  |

## Transparency ledger

- **Cited spec rows:** 135 verified on their page · 0 mismatched · 18 web-only (not verifiable locally).
- **design-requirements.md:** 53/85 numeric lines carry a source tag (62 %).
- **ISSUES.md:** 13/16 numeric lines carry a source tag (81 %).
- **REWORK.md:** 2/22 numeric lines carry a source tag (9 %).
- **Assumptions this run depends on** (from board_rules.py):
  - assumed: Pico 2 SMPS tolerance not given in pico2 DS; 3 % high allowance
  - assumed: standard 0.1 uF logic decoupling
