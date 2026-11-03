# Plasma Donut

UVA ECE capstone (Fall 2026): a sealed glass torus of xenon, struck by an HV
sparker and sustained by a 13.56 MHz class E oscillator driving two coils, with
a Raspberry Pi Pico 2 control board for diagnostics (temperatures, coil supply
voltages, A/B phase) on a 128x64 LCD.

## Repository layout (current, Nov 2026)

| Folder | What it is |
|---|---|
| `Microcontroller-PCB/` | Control board: KiCad 10 schematic + PCB (Pico 2, MCP3208 ADC, phase detector, LCD), custom footprints in `PlasmaDonut.pretty` |
| `Microcontroller-PCB/datasheets/` | Part catalogue (per-part notes, `specs.csv`, `search.py`), design requirements, BOM-vs-orders, known issues, rework guide, `flagcheck/` rule checker, DRC/ERC reports. Vendor PDFs stay local, not in git |
| `Footprints/` | Downloaded symbols/footprints/3D models used by the control board (`${KIPRJMOD}/../Footprints`) |
| `pico-firmware/` | MicroPython firmware for the control board (monitor only, never controls the HV side), pin map, host-side tests |
| `OSC-PCB/` | Class E oscillator board (KiCad) |
| `HaloPlasma/` | KiCad project |
| `Pulse Generator/KiCad Project/spark/` | Sparker / pulse generator board (KiCad) |
| `Sims/` | ngspice decks and results, board previews |
| `Enclosure CAD/` | Parametric enclosure script (PlasmaCan) |
| `docs/` | **Superseded** first-pass design from Sept 2026 (GHz ignition, Raspberry Pi), kept for history |

---

## First-pass design (Sept 2026, superseded)

Everything below is the original first-pass system design and no longer
matches the build (the project moved to a Pico 2, a single 13.56 MHz class E
oscillator, and HV spark ignition). Kept for reference.

A benchtop capstone project: a sealed, glass **toroidal xenon chamber**, ionized
inductively by a pair of driver coils (top and bottom), with the ionized
xenon "torus" shape, height, and stability controlled by **detuning** the two
coils relative to each other. Ignition is kicked off with a high-frequency
(GHz-band) switch-mode RF stage; the whole system is orchestrated by a
Raspberry Pi.

This document is the first-pass system design: architecture, the reasoning
behind each choice, concrete numbers, a sourced parts list, and the open
questions still worth testing before committing to a full build. It is a
starting point for the design, not a finished, verified circuit — see
[Open Risks](#open-risks--what-to-test-first) before ordering the expensive
parts.

## Contents

- [`docs/rf-design.md`](docs/rf-design.md) — the RF chain: why GHz for
  ignition, why a different frequency for sustain, the Class E stage design,
  and the coil/applicator problem at each frequency.
- [`docs/control-system.md`](docs/control-system.md) — the Raspberry Pi
  side: how it programs the synthesizers, how ignition is detected, and the
  detuning control loop for position/stability.
- [`docs/bom.md`](docs/bom.md) — parts list with part numbers and why each
  one was picked.
- [`docs/references.md`](docs/references.md) — every source used, so any of
  these numbers can be checked or superseded.

## System overview

```
                     ┌─────────────────────────┐
                     │      Raspberry Pi        │
                     │  (control + sensing)     │
                     └───┬───────────┬─────┬────┘
                SPI/GPIO │           │SPI  │SPI (ADC)
              ┌──────────┘           │     └────────────┐
              ▼                      ▼                   ▼
      ┌───────────────┐     ┌───────────────┐   ┌────────────────┐
      │ ADF4351 synth  │ x2  │ AD9910 DDS    │x2 │ MCP3208 ADC     │
      │ (2.45 GHz      │     │ (13.56 MHz    │   │ (Γ + photodiode │
      │  ignition)     │     │  sustain)     │   │  readback)      │
      └───────┬────────┘     └───────┬───────┘   └────────────────┘
              ▼                      ▼
      ┌───────────────┐     ┌───────────────┐
      │ Parallel-Class-E│    │ Class E/D MOSFET│
      │ GaN stage (x2)  │    │ sustain stage x2│
      └───────┬────────┘     └───────┬───────┘
              ▼                      ▼
      ┌────────────────────────────────────┐
      │  Directional couplers + loop/coil   │
      │  applicators, TOP and BOTTOM of the │
      │  torus                              │
      └──────────────┬─────────────────────┘
                      ▼
           ┌─────────────────────┐
           │ Sealed glass torus,  │
           │ xenon fill, 20-50 Torr│
           └─────────────────────┘
```

Two independent RF chains — one per coil — so that the ignition frequency,
sustain frequency, and power on the top coil can differ from the bottom
coil. That differential ("detuning") is the actual control handle for torus
height and stability; see [`docs/control-system.md`](docs/control-system.md).

## Key numbers (first pass)

| Parameter | Value | Why |
|---|---|---|
| Chamber major diameter | ~120 mm | Keeps the whole envelope on the order of one free-space wavelength at 2.45 GHz (λ ≈ 122 mm) or smaller — benchtop-scale |
| Chamber tube (minor) diameter | ~25 mm | Benchtop scale, room for coil wrap at the sustain stage |
| Xenon fill pressure | 20–50 Torr, sealed | Sits in the efficiency "sweet spot" (10–200 Torr, best 20–100 Torr) documented for rare-gas discharge lamps |
| Ignition frequency | 2.45 GHz (ISM band) | License-exempt for RF-heating use (FCC Part 18); small field volume needed to strike gas; parts (GaN HEMTs, PLL synths) are inexpensive and available up to 6 GHz |
| Sustain / control frequency | 13.56 MHz (ISM band) | Coils can be real multi-turn geometry (λ ≈ 22 m — electrically small); matches every proven ICP/electrodeless-lamp reference design; detuning behaves predictably |
| Ignition RF power (per coil) | ~8–10 W | Matches literature data points for single-GaN-HEMT Class E stages at 2.45 GHz (22 W / 64.7% PAE achieved in published designs; scaled down for a benchtop sealed low-pressure fill rather than an atmospheric-pressure torch) |
| Sustain RF power (per coil) | ~10–30 W | Typical of electrodeless HID/fluorescent lamp drive levels |
| Detuning range | fraction of loaded-Q bandwidth (to be measured; expect tens–hundreds of kHz at 13.56 MHz) | Enough to shift relative coupled power between coils without either one losing its own resonance |

Everything above is a **starting point**, chosen to be defensible and
buildable, not a value pulled from thin air — the reasoning and sources for
each number are in `docs/rf-design.md` and `docs/references.md`.

## Open risks — what to test first

1. **Does differential coil detuning actually move the plasma vertically?**
   This is the load-bearing physical hypothesis of the whole "detuning
   controls height" idea. The mechanism is plausible and grounded in real
   plasma physics (a plasma is diamagnetic — it tends to exclude a rapidly
   oscillating RF field, so the near-field of a more strongly driven coil
   should push the plasma away from itself; two opposed coils with unequal
   coupling should shift the equilibrium point where the two pushes
   balance). But no source found here demonstrates this specific
   geometry — it hasn't been validated for a toroidal chamber with two
   coils. **Build a small single straight-tube, two-coil test article
   first** and confirm the sign and rough magnitude of the effect before
   committing to the full donut and its vacuum/glasswork cost.
2. **GHz coil/applicator design.** At 2.45 GHz a multi-turn coil is not a
   valid applicator (see `docs/rf-design.md`); a small resonant loop is.
   That loop's exact dimensions depend on your final chamber geometry and
   need EM simulation or bench tuning, not just hand calculation.
3. **Vacuum + xenon fill system** is a whole subsystem (roughing pump, gas
   manifold, capacitance manometer, seal-off or valve) not detailed here —
   it's outside "RF design" but gates the whole project.

## Safety (read before building)

- **RF/microwave exposure.** Watts at 2.45 GHz is the same band as a
  microwave oven. The chamber and both coil applicators need a fully
  enclosed, gasketed metal enclosure with no gaps larger than a fraction of
  a wavelength, and leakage should be measured, not assumed. This is a
  hard requirement, not a nice-to-have.
- **Sealed low-pressure glass vessel** is an implosion hazard. Handle and
  operate behind a shield at all times.
- **GaN HEMT bias sequencing.** The Wolfspeed CGH-series parts require Vgs
  to be applied and set before Vds, per their datasheets, or the device is
  destroyed. Use a real bias-sequencer circuit, not a single power switch.
- **Regulatory path is FCC Part 18** (ISM/RF-heating equipment), not Part
  15 (unintentional radiators) or Part 97 (amateur radio) — different
  compliance rules apply.
- Xenon itself is inert and non-toxic; the hazards here are the vacuum
  system and the RF power, not the gas.
