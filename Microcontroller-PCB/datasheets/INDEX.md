# Control board datasheet catalogue: start here

**Board:** Microcontroller-PCB, schematic 2026-10-22 · 99 placed parts · ERC 0 errors · DRC 0 errors · schematic↔PCB parity clean (kicad-cli 10.0.8)
**Read next:**
- [flagcheck/FLAGS.md](flagcheck/FLAGS.md): automated design flags; the rules behind them are in [flagcheck/RULES.md](flagcheck/RULES.md). Re-run `flagcheck.py` after every change
- [ISSUES.md](ISSUES.md): 18 issues ranked by severity, each with a fix that uses parts you already own
- [design-requirements.md](design-requirements.md): the signal map, requirements traceability, and every circuit-math check
- [BOM-vs-orders.md](BOM-vs-orders.md): each BOM line matched to what was ordered, and what's still in transit

## Parts and datasheets

| Key | Part | Ref | Card | Must-know |
|---|---|---|---|---|
| pico2 | Raspberry Pi Pico 2 (SC1631) | A1 | [card](parts/pico2.md) · [pdf](pdf/pico2.pdf) | +5V → VSYS · 3V3 ≤ 300 mA · ADC pins ≤ IOVDD + 0.3 V |
| rp2350 | RP2350 | in A1 | [card](parts/rp2350.md) · [pdf](pdf/rp2350.pdf) | E9 (no pull-downs) · PWM count on odd pins only · **GPIO22 = GPIN1** · ADC RIN ≥ 100 kΩ |
| mcp3208 | MCP3208-CI/SL | U1 | [card](parts/mcp3208.md) · [pdf](pdf/mcp3208.pdf) | CH4/5 floating · 1 MHz SPI · both grounds should go to analog plane |
| nhd_c12864lz | NHD-C12864LZ-FSW-FBW-3V3 | DS1 | [card](parts/nhd_c12864lz.md) · [pdf](pdf/nhd_c12864lz.pdf) | VDD 2.7–3.3 V · LED 60–100 mA · 70 °C max |
| st7565r | ST7565R | in DS1 | [card](parts/st7565r.md) · [pdf](pdf/st7565r.pdf) | SPI ≥ 50 ns period · write-only |
| ntcs0603e3 | NTCS0603E3103FLT ×4 | off-board, J3–J6 | [card](parts/ntcs0603e3.md) · [pdf](pdf/ntcs0603e3.pdf) | B25/85 = 3435 K ±1 % |
| lm66100 | LM66100DCKR | U2 | [card](parts/lm66100.md) · [pdf](pdf/lm66100.pdf) | **abs max 6 V** · CE = VOUT ✓ |
| ao3400a | AO3400A | Q1 | [card](parts/ao3400a.md) · [pdf](pdf/ao3400a.pdf) | fully on at 2.5 V gate |
| nx_74lvc1g17 | 74LVC1G17GV-Q100 (Nexperia) | U4, U5 | [card](parts/nx_74lvc1g17.md) · PDF ⚠ not cached | VT+ 1.29–1.71 / VT− 0.88–1.24 V · t_pd 0.7–5.5 ns |
| nx_74lvc1g86 | 74LVC1G86GV (Nexperia) | U3 | [card](parts/nx_74lvc1g86.md) · PDF ⚠ not cached | t_pd 0.5–5.0 ns |
| bat54ws_mcc | BAT54WS-TP (MCC) | D1 | [card](parts/bat54ws_mcc.md) · [pdf](pdf/bat54ws_mcc.pdf) | VR 30 V · VF 0.24 V @ 0.1 mA · CJ 10 pF |
| yageo_rc_l | Yageo RC_L resistors | R1–R31 | [card](parts/yageo_rc_l.md) · [pdf](pdf/yageo_rc_l.pdf) | 0805 1/8 W 150 V · 1206 1/4 W |
| kemet_x7r | KEMET C0805C105K3RACTU | C1, C4–C13 | [card](parts/kemet_x7r.md) · [pdf](pdf/kemet_c0805c105k3r.pdf) | 1 µF 25 V X7R (DC-bias loss) |
| kemet_c0g | KEMET C0G family | C30, C34, C36, C37 | [card](parts/kemet_c0g.md) · [pdf](pdf/kemet_c0g.pdf) | stable, no DC-bias loss |
| omron_b3f | Omron B3F-1000 | SW1, SW2 | [card](parts/omron_b3f.md) · [pdf](pdf/omron_b3f.pdf) | bounce ≤ 5 ms · ≥ 1 mA rated |

**No datasheet needed (generic or tooling):** the Samsung 0.1 µF/10 µF X7R caps, Phoenix 1715022 terminals, the 1×14 header, test pads and solder jumpers. They're listed in BOM-vs-orders.md.
**Nexperia PDFs:** Nexperia's site blocks automated downloads, so the specs on those two cards were read from the PDFs through a web fetch. Download [74LVC1G17](https://assets.nexperia.com/documents/data-sheet/74LVC1G17.pdf) and [74LVC1G86](https://assets.nexperia.com/documents/data-sheet/74LVC1G86.pdf) into `pdf/`, then run the add step in the README.

## Top 5 things to act on (from ISSUES.md)
1. 🔴 Order 8 is delayed: it has the screw terminals, 7.15k, C36/C37 and D1. There are stop-gaps for all of them.
2. 🔴 Meter TP7↔TP8 before power-up. The PCB has no GND/GNDA tie of its own.
3. 🔴 Never hot-plug a live supply into J1, and keep it at 5.0 V (the LM66100 is 6 V absolute max).
4. 🟠 Scope the pickup and passive-coil amplitudes, then rescale R25/R27 from stock values. The windows are 17–47 V pk and 10–120 V pk.
5. 🟠 Firmware: hide MCP3208 CH4/5, burst-sample the Pico ADC and calibrate it, cap the backlight at 75 %, and measure f_osc with GPIN1 + FC0.

## Files
| File | What it is |
|---|---|
| `parts/*.md` | One card per part: usage on this board, gotchas, key specs with page links |
| `specs.csv` | Every key spec as one row: part, parameter, min/typ/max, unit, conditions, page, tags |
| `datasheets.db` | **SQLite FTS5** full-text index: every datasheet page plus every spec, ranked and stemmed (used by `search.py`) |
| `text/*.txt` | Full text with `=== part p.N ===` page markers, for grep or VS Code search |
| `pdf/*.pdf` | Original datasheets |
| `bom-kicad.csv` | BOM exported by kicad-cli from the schematic |
| `kicad-reports/` | Raw ERC and DRC reports. The library warnings come from the cloud machine's missing global libraries; there are 0 real errors |
| `manifest.json` | Source URL, revision, page count, SHA-256 and retrieval date for each PDF |
