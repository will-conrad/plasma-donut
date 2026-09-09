# RF Design

This walks through the RF chain from first principles, so the part choices
make sense rather than just being a list.

## Why two frequencies, not one

You asked for a GHz-range Class E oscillator to "kick start" ionization,
and separately for enough frequency flexibility to control the plasma once
it exists. Those are two different jobs with two different favorable
frequencies, and I'm recommending they actually run at two different
frequencies rather than one, for a physical and a practical reason:

**Breakdown** (getting a neutral gas to first ionize) is easiest when you
can concentrate a strong electric field into a small volume — which is
exactly what a high frequency, physically small resonant structure gives
you. It's also the regime real microwave plasma torches already live in:
2.45 GHz magnetron-driven torches are a well-established category, and more
recent designs replace the magnetron with a solid-state (transistor)
2.45 GHz power amplifier for better efficiency and control — see
`references.md`. 2.45 GHz is also an ISM (industrial/scientific/medical)
band, so running RF-heating equipment there is license-exempt in the US
under FCC Part 18, as long as the equipment is enclosed and doesn't leak
excessively — unlike almost any other frequency you could pick, where
you'd need an amateur license or a different regulatory path entirely.

**Sustaining and steering** the plasma once it's lit is a different
problem: you want a coil geometry with well-understood, controllable
coupling, and you want the detuning-vs-response relationship to be
predictable so a control loop can use it. Every real precedent for
"detune the drive frequency to control an RF-plasma load" that I found
(electrodeless HID/fluorescent lamps, ICP torches, a published frequency-
tuned automatic matching system for a plasma source) runs in the low-MHz
range with genuine multi-turn coils. That's not a coincidence — it's a
consequence of wavelength, explained next.

## Why a multi-turn coil doesn't work at 2.45 GHz

A coil is only a "lumped" inductor — the kind of simple component your
intuition and hand calculations (V = L di/dt, etc.) are built around — if
it's physically much smaller than the wavelength of the signal driving it.

- At 13.56 MHz, free-space wavelength λ = c/f ≈ 22 m. A coil a few
  centimeters across is a tiny fraction of that — it behaves like a normal
  inductor, and this is exactly the regime every ICP torch, electrodeless
  lamp, and induction heater reference design uses: real multi-turn coils,
  sometimes with ferrite, straightforward matching.
- At 2.45 GHz, λ ≈ 122 mm. A multi-turn coil that same "few centimeters
  across" is now a meaningful fraction of a wavelength — each turn is
  itself a length of transmission line, the coil will have its own internal
  standing waves, unpredictable self-resonances, and will radiate instead
  of staying a clean near-field inductor. This is why every 2.45 GHz
  plasma torch design uses a resonant cavity, waveguide applicator, or a
  small single-turn/loop-gap resonator instead of a wound coil.

**Consequence for this design:** the 2.45 GHz ignition stage should drive a
small single-turn (or "hairpin," half-turn) copper loop positioned close to
the glass near the top and bottom of the torus — not a coil wound around
the tube. The 13.56 MHz sustain stage, once the gas is already ionized and
you've handed off control, *can* use real multi-turn coils, matching every
proven reference design. This is the second reason (beyond breakdown
physics) for splitting ignition and sustain into two frequencies: it lets
each stage use the applicator geometry that actually works at its
frequency.

If a single-frequency, GHz-only system is a hard requirement of your
capstone brief, it's still buildable — you'd carry the loop-applicator
approach through to the sustain/detuning stage too, and detuning would
have to be characterized against the loop's own (likely lower, harder to
predict) loaded Q. Flagging this as the harder path rather than ruling it
out.

## Class E stage — what it is and why "parallel" and "double"

Class E is a switch-mode amplifier: the transistor is driven hard enough
that it acts as an on/off switch rather than a linear gain device, and a
resonant output network (an L and C, sized so the network "rings" the
right way) shapes the drain/collector voltage so it's at zero right when
the switch turns back on. That's the whole trick — a normal switch turning
on into a non-zero voltage dumps energy into the switch's own capacitance
every cycle (this is most of the switching loss in a hard-switched design);
Class E arranges for that loss to not happen, which is why it can reach
efficiencies linear amplifiers can't.

The classic ("shunt-C") Class E topology gets harder to realize cleanly as
frequency rises, because the required loaded Q and component tolerances get
tight. A documented variant — **parallel-circuit Class E** — rearranges
where the shunt element sits in the network and tolerates a lower loaded Q,
which is specifically why it's the topology of choice in the 2.4 GHz Class
E literature (see references — published parallel-circuit Class E designs
at 2.4 GHz reaching 60%+ power-added efficiency). That's almost certainly
what "double parallel Class E" should mean: **two** parallel-circuit
Class E stages, one per coil (top and bottom), each independently tunable
in frequency — which is also exactly what the two-coil detuning control
scheme needs.

### Per-channel ignition chain (×2, top and bottom)

1. **ADF4351** PLL synthesizer (Analog Devices) — covers 35 MHz–4.4 GHz,
   fully SPI-programmable, ~0 dBm output. This is the part the Raspberry
   Pi actually talks to; see `control-system.md`.
2. **Driver/pre-amp** — a small MMIC gain block (e.g. a 20 dB, DC–4 GHz
   part) to bring the synthesizer's ~0 dBm up to the ~+20 dBm needed to
   properly saturate the GaN HEMT's gate for switch-mode operation.
3. **Power stage** — a single Wolfspeed **CGH40010** GaN HEMT (10 W,
   DC–6 GHz), biased and matched as a parallel-circuit Class E stage.
   Target: ~8–10 W RF out, in the 55–65% PAE range that published 2.4 GHz
   GaN Class E designs report.
4. **Output matching network** — the parallel-Class-E L/C network,
   transforming the 50 Ω system impedance to whatever the loop
   applicator's loaded impedance turns out to be (measure, don't assume —
   this is dominated by the plasma's own loading once lit, and will differ
   pre-strike vs. post-strike).
5. **Directional coupler** sampling forward and reflected power, feeding
   the ignition-detection chain (`control-system.md`).
6. **Loop applicator** — small single-turn loop, positioned at the top or
   bottom of the torus.

### Per-channel sustain chain (×2), after handoff

1. **AD9910** DDS (1 GSPS, useful output well past 13.56 MHz, sub-Hz
   frequency resolution) — far more tuning resolution than needed, which
   is fine; it gives headroom for fine detuning steps.
2. **Power stage** — a simpler RF MOSFET class D/E stage (parts like the
   classic induction-heating/ham-radio RF MOSFETs are well documented for
   this), tens of watts.
3. **Multi-turn coil** wrapped near the top/bottom of the torus tube —
   a real inductor at this frequency, so ordinary coil design math applies.
4. **Directional coupler + detector**, same purpose as the ignition side,
   used continuously for the detuning control loop rather than just a
   one-shot ignition check.

## Handoff between ignition and sustain

Two workable patterns, either is fine to prototype with:

- **Sequential**: fire the 2.45 GHz stage, detect strike (see
  `control-system.md`), then immediately bring up the 13.56 MHz sustain
  stage and drop the ignition stage to standby.
- **Assisted** (more robust, more complex): run the sustain coils
  continuously at a below-breakdown level, and use the GHz pulse only as
  the trigger — the sustain field is already present the instant the gas
  ionizes, so there's no gap where the plasma could re-extinguish while the
  sustain stage is still ramping up. This is the same idea used in
  microwave-assisted ignition for RF plasma sources.

Start with sequential for a first prototype (simpler to instrument and
debug); move to assisted if the plasma proves hard to keep lit through the
handoff.
