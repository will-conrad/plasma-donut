# Control System

The Raspberry Pi is the "brain" — it never generates or amplifies the RF
itself, it programs dedicated chips that do, and reads back low-speed
sensor data over SPI. That split matters: a GPIO pin physically cannot
toggle at gigahertz rates, but it can absolutely write a 32-bit register to
a synthesizer chip in a few microseconds, which is all "tuning the
frequency from software" actually requires.

## What the Pi talks to

| Bus | Device | Count | Purpose |
|---|---|---|---|
| SPI (bit-banged GPIO or hardware SPI) | ADF4351 | 2 | Sets the 2.45 GHz ignition frequency, per coil |
| SPI | AD9910 | 2 | Sets the 13.56 MHz sustain frequency, per coil, with sub-Hz resolution |
| SPI | MCP3208 (8-ch, 12-bit ADC) | 1 | Reads back forward/reflected power detectors + photodiode(s) — the Pi has no native analog input, so this is required |

There's a working open-source reference for the ADF4351 half of this:
`davecrump/RPiADF4351` on GitHub bit-bangs LE/CLK/DATA over configurable
GPIO pins and exposes a simple `./adf4351 <freq_MHz>` command-line
interface. That's a solid starting point to adapt rather than writing the
SPI protocol from scratch — the ADF4351's register format (six 32-bit
registers written MSB-first) is a known quantity there.

## Ignition detection

The core trick, borrowed from a published frequency-tuned RF plasma
matching system (see `references.md`): compute the **reflection
coefficient** from forward and reflected power,

```
Γ = sqrt(P_reflected / P_forward)
```

using AD8318 log-amp power detectors on the coupled ports of each
directional coupler, read through the MCP3208. Before the gas breaks down,
the loop/coil is driving essentially nothing (an unloaded resonator), so
Γ sits high. The instant the gas ionizes, the load impedance changes
abruptly (the plasma starts absorbing real power), and Γ drops sharply.
Watching **dΓ/dt** rather than Γ's absolute value catches this reliably
even if the absolute matching isn't perfect — you're looking for the sharp
transition, not a specific target value.

Cross-check with a plain **photodiode** aimed into the chamber, on a spare
MCP3208 channel. This is deliberately redundant with the RF-side detection:
it's cheap, unambiguous (light either turned on or it didn't), and doesn't
depend on any of the RF math being right. Treat "RF says lit AND photodiode
says lit" as the actual strike-confirmed condition before handing off to
the sustain stage.

## Control loop, end to end

1. **Ignition sweep.** Step the two ADF4351s across ~2.40–2.50 GHz (the
   ISM band) at the ignition power level, watching Γ on each channel for a
   dip (indicates the loop applicator's own resonance, and/or the point
   where the gas actually breaks down).
2. **Strike detection.** On a qualifying dΓ/dt drop plus photodiode
   confirmation, log the strike frequency and move to step 3.
3. **Handoff.** Drop the ignition stage to standby (or hold it at a low
   assist level — see the "assisted" handoff pattern in `rf-design.md`),
   bring up both AD9910 sustain channels at a conservative starting power.
4. **Position/stability loop.** This is the actual "detuning controls
   height" control loop:
   - Outer loop error signal: torus vertical position, sensed optically —
     simplest version is a **pair of photodiodes** (or a small linear
     photodiode array) positioned to see the plasma's centroid height
     through the chamber wall.
   - Control variable: Δf = f_top − f_bottom on the sustain synthesizers.
   - The AD9910's tuning resolution is far finer than needed here, so the
     control loop will be limited by how precisely you can measure
     position optically and by the coil's own loaded Q (which sets how
     much a given Δf actually changes coupled power) — not by synthesizer
     resolution.
   - **This loop's transfer function (Δf → Δheight) is not yet known** —
     it needs to be measured on the test article described in the README's
     Open Risks section before this control loop can be tuned for real.
     Start with a simple proportional controller and characterize the
     response empirically; don't assume a sign or gain in advance.
5. **Ongoing supervision.** Keep watching Γ on the sustain channels too —
   if it degrades badly (poor coupling, plasma about to extinguish), that's
   a fault condition worth reacting to (e.g., fall back to step 3's
   assist level, or re-trigger ignition).

## Why this is a reasonable job for a Raspberry Pi specifically

Nothing here needs hard real-time guarantees in the microsecond range —
the fastest loop (ignition strike detection) only needs to react within
tens of milliseconds (the published reference matching system settled its
frequency-hunt in about 10 ms, for comparison), which is comfortably within
what Linux-on-RPi plus SPI can do if the polling loop is written
straightforwardly (avoid anything that blocks the SPI reads, and keep the
loop's Python/C overhead modest — a compiled control loop, or at least a
tight Python loop without library overhead per iteration, is worth
budgeting for once you're past the getting-something-lit stage).
