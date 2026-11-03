# Plasma Donut — Pico 2 firmware

MicroPython firmware for the Plasma Donut control board (UVA ECE capstone,
Fall 2026). A Raspberry Pi Pico 2 reads board temperatures, coil supply
voltages and the A/B phase signal, and shows them on a 128x64 ST7565R LCD.
**The firmware only monitors — it never controls the HV side.**

> Nothing here has run on hardware yet. Follow the bring-up order in
> `CLAUDE.md` and confirm each step on the board.

## Layout

| Path | What it is |
|---|---|
| `src/` | Firmware: `config.py` (pins + constants), `mcp3208.py` (ADC), `picoadc.py` (Pico ADC burst sampling), `st7565.py` (LCD), `sensors.py`, `freq.py`, `cal.py`, `board.py` |
| `tests/host/` | Host-side tests (run on a laptop, no Pico needed) |
| `PINMAP.md` | GPIO → net → function, from the KiCad netlist |
| `CLAUDE.md` | Firmware brief: architecture, conversion math, bring-up sequence |
| `FIXES.md` | Firmware side of the known board issues |
| `docs/ISSUES.md` | Known board issues the firmware works around (`ISSUES #n` in code) |
| `docs/REWORK.md` | Optional hardware bodges (gated by flags in `config.py`) |
| `docs/design-requirements.md` | Design requirements (`DC-xx` in code) |
| `docs/RULES.md` | Claim-tag rules: `(part p.N)`, `[netlist]`, `[calc]`, `[web]`, `[assumed]` |
| `docs/parts/` | Datasheet notes + `specs.csv` for the parts the firmware talks to |

The source of truth for pins is the KiCad schematic, which lives outside this
repo (OneDrive `CAPSTONE/Microcontroller-PCB/`), along with the full datasheet
PDFs that `(part p.N)` citations point to.

## Run the host tests

```bash
python3 -m pytest tests/host
```

## Put it on the Pico

```bash
pip install mpremote
mpremote cp src/*.py :
```
