# Datasheets: start here

Every datasheet for the control board, each PDF with a Markdown twin beside it:

- **`<part>.pdf`** is the original from the manufacturer. Its SHA-256 is in `manifest.json`.
- **`<part>.md`** has a header (role, reference designators, source, revision, hash), then the full text of every page under `## Page N`.
- **`docs/parts/<part>.md`** is the board-notes card: how we use the part, gotchas, and key specs with page links.

A citation like `(mcp3208 p.3)` means page 3 of `mcp3208.pdf`, which is `## Page 3` in `mcp3208.md`.

The 13 PDFs that were in the old OneDrive catalogue were re-downloaded on 2026-11-19, and each is **byte-identical** to the old copy (same SHA-256). So every existing citation still points at the same page.

## Parts

| Key | Part | Ref | Files | Must-know |
|---|---|---|---|---|
| pico2 | Raspberry Pi Pico 2 (SC1631) | A1 | [pdf](pico2.pdf) · [md](pico2.md) · [card](../../docs/parts/pico2.md) | +5V → VSYS · 3V3 ≤ 300 mA · ADC pins ≤ IOVDD + 0.3 V |
| rp2350 | RP2350 | in A1 | [pdf](rp2350.pdf) · [md](rp2350.md) · [card](../../docs/parts/rp2350.md) | E9 (no pull-downs) · PWM count on odd pins only · GPIO22 = GPIN1 · ADC R_IN ≥ 100 kΩ |
| mcp3208 | MCP3208-CI/SL | U1 | [pdf](mcp3208.pdf) · [md](mcp3208.md) · [card](../../docs/parts/mcp3208.md) | 1 MHz SPI at 3.3 V · CH4/5 floating |
| nhd_c12864lz | NHD-C12864LZ-FSW-FBW-3V3 | DS1 | [pdf](nhd_c12864lz.pdf) · [md](nhd_c12864lz.md) · [card](../../docs/parts/nhd_c12864lz.md) | VDD 2.7–3.3 V · LED 60–100 mA · 70 °C max |
| st7565r | ST7565R | in DS1 | [pdf](st7565r.pdf) · [md](st7565r.md) · [card](../../docs/parts/st7565r.md) | SPI ≥ 50 ns period · write-only |
| ntcs0603e3 | NTCS0603E3103FLT ×4 | off-board, J3–J6 | [pdf](ntcs0603e3.pdf) · [md](ntcs0603e3.md) · [card](../../docs/parts/ntcs0603e3.md) | B25/85 = 3435 K ±1 % |
| lm66100 | LM66100DCKR | U2 | [pdf](lm66100.pdf) · [md](lm66100.md) · [card](../../docs/parts/lm66100.md) | **abs max 6 V** · CE = VOUT |
| ao3400a | AO3400A | Q1 | [pdf](ao3400a.pdf) · [md](ao3400a.md) · [card](../../docs/parts/ao3400a.md) | fully on at 2.5 V gate |
| nx_74lvc1g17 | 74LVC1G17GV-Q100 (Nexperia) | U4, U5 | ⚠ PDF missing · [md](nx_74lvc1g17.md) · [card](../../docs/parts/nx_74lvc1g17.md) | VT+ 1.29–1.71 / VT− 0.88–1.24 V · t_pd 0.7–5.5 ns |
| nx_74lvc1g86 | 74LVC1G86GV (Nexperia) | U3 | ⚠ PDF missing · [md](nx_74lvc1g86.md) · [card](../../docs/parts/nx_74lvc1g86.md) | t_pd 0.5–5.0 ns |
| bat54ws_vishay | BAT54WS-G3-18 (Vishay) | D1, **fitted** | [pdf](bat54ws_vishay.pdf) · [md](bat54ws_vishay.md) | the Mouser part on the board |
| bat54ws_mcc | BAT54WS-TP (MCC) | D1, as designed | [pdf](bat54ws_mcc.pdf) · [md](bat54ws_mcc.md) · [card](../../docs/parts/bat54ws_mcc.md) | VR 30 V · VF 0.24 V @ 0.1 mA · CJ 10 pF |
| yageo_rc_l | Yageo RC_L resistors | R1–R31 | [pdf](yageo_rc_l.pdf) · [md](yageo_rc_l.md) · [card](../../docs/parts/yageo_rc_l.md) | 0805 1/8 W 150 V · 1206 1/4 W |
| kemet_x7r | KEMET C0805C105K3RACTU | C1, C4–C13 | [pdf](kemet_x7r.pdf) · [md](kemet_x7r.md) · [card](../../docs/parts/kemet_x7r.md) | 1 µF 25 V X7R (DC-bias loss) |
| kemet_c0g | KEMET C0G family | C30, C34, C36, C37 | [pdf](kemet_c0g.pdf) · [md](kemet_c0g.md) · [card](../../docs/parts/kemet_c0g.md) | stable, no DC-bias loss |
| omron_b3f | Omron B3F-1000 | SW1, SW2 | [pdf](omron_b3f.pdf) · [md](omron_b3f.md) · [card](../../docs/parts/omron_b3f.md) | bounce ≤ 5 ms |
| phoenix_1715022 | Phoenix MKDS 1,5/2 (1715022) | J1, J3–J6, J9–J12, J14, J16, J17 | [pdf](phoenix_1715022.pdf) · [md](phoenix_1715022.md) | 5.0 mm pitch · 1.3 mm hole · 17.5 A / 400 V |

**Not covered (generic parts):** the Samsung 0.1 µF / 10 µF X7R caps, the 1×14 header, the test pads and the solder jumpers.

## The two missing Nexperia PDFs
Nexperia's site blocks automated downloads, so these two have to come from a browser:
1. Open [74LVC1G17.pdf](https://assets.nexperia.com/documents/data-sheet/74LVC1G17.pdf) and [74LVC1G86.pdf](https://assets.nexperia.com/documents/data-sheet/74LVC1G86.pdf).
2. Save them into this folder as `nx_74lvc1g17.pdf` and `nx_74lvc1g86.pdf`.
3. Run `python3 hardware/datasheets/build_md.py nx_74lvc1g17 nx_74lvc1g86`. This fills in the two `.md` files and records the hashes in `manifest.json`.

## Tools
Both scripts need only `python3`, plus poppler for `build_md.py` (`brew install poppler`).
```bash
python3 hardware/datasheets/search.py hysteresis                  # prints [part p.N] + matching lines
python3 hardware/datasheets/search.py "input impedance" --part rp2350 -C 2
python3 hardware/datasheets/build_md.py                           # rebuild every .md from its PDF
python3 hardware/datasheets/build_md.py --check                   # verify each PDF against manifest.json
```

## Adding a datasheet for V2
1. Save the PDF here as `<key>.pdf`. The key is lower-case with underscores, e.g. `tps63000`.
2. Run `python3 hardware/datasheets/build_md.py <key>`. It adds the part to `manifest.json` with its hash and page count, and writes `<key>.md`.
3. Fill in `name`, `manufacturer`, `role`, `refs`, `source_url` and `revision` in `manifest.json`, then run step 2 again so the header picks them up.
4. Add a row to the table above. If the firmware talks to the part, also add a card in `docs/parts/` and rows in `docs/parts/specs.csv`.
