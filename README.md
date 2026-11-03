# Plasma Donut — Pico 2 firmware

C firmware (Raspberry Pi Pico SDK) for the Plasma Donut control board (UVA ECE capstone,
Fall 2026). A Raspberry Pi Pico 2 reads board temperatures, coil supply
voltages and the A/B phase signal, and shows them on a 128x64 ST7565R LCD.
**The firmware only monitors — it never controls the HV side.**

> **Firmware is being rebuilt from scratch.** The repo is an outline with no
> code yet; the previous version is in git history (commit `903789a`). The pin
> map, brief, fixes list and `docs/` are the spec for the rebuild.

## Layout

| Path | What it is |
|---|---|
| `src/` | Firmware source (empty outline): `config/`, `drivers/`, `sensors/`, `ui/`, plus `main.c`; `CMakeLists.txt` at the root (to be written) |
| `tests/host/` | Laptop-side tests (empty) |
| `tools/` | Helper scripts, e.g. deploy to the Pico (empty) |
| `PINMAP.md` | GPIO → net → function, from the KiCad netlist |
| `CLAUDE.md` | Firmware brief: architecture, conversion math, bring-up sequence |
| `FIXES.md` | Firmware side of the known board issues |
| `docs/ISSUES.md` | Known board issues the firmware works around (`ISSUES #n` in code) |
| `docs/REWORK.md` | Optional hardware bodges (gated by flags in `src/config/config.h`) |
| `docs/design-requirements.md` | Design requirements (`DC-xx` in code) |
| `docs/RULES.md` | Claim-tag rules: `(part p.N)`, `[netlist]`, `[calc]`, `[web]`, `[assumed]` |
| `docs/parts/` | Datasheet notes + `specs.csv` for the parts the firmware talks to |

The source of truth for pins is the KiCad schematic, which lives outside this
repo (OneDrive `CAPSTONE/Microcontroller-PCB/`), along with the full datasheet
PDFs that `(part p.N)` citations point to.

## Build (once the code exists)

```bash
export PICO_SDK_PATH=~/pico/pico-sdk      # SDK 2.3.1
cmake -B build -DPICO_BOARD=pico2
cmake --build build
# hold BOOTSEL, plug in the Pico 2, copy build/<target>.uf2 to the drive
```

