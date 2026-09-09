# Bill of Materials (first pass)

Quantities assume the two-channel (top coil + bottom coil), two-frequency
(2.45 GHz ignition + 13.56 MHz sustain) architecture from `rf-design.md`.
Prices are rough/typical, not quotes — check current distributor pricing
before ordering.

## RF synthesis / control

| Part | Qty | Role | Notes |
|---|---|---|---|
| Analog Devices ADF4351 (module, e.g. the common 35M–4.4GHz eval-style boards) | 2 | Ignition frequency synthesis | SPI-programmable; drive from RPi per `control-system.md`. Share one 10 MHz reference between both boards to keep the two channels frequency-coherent rather than free-running independently. |
| Analog Devices AD9910 | 2 | Sustain frequency synthesis | 1 GSPS DDS, far more resolution than needed at 13.56 MHz — headroom for fine detuning steps |
| Raspberry Pi (4 or 5) | 1 | Master controller | Needs enough GPIO/SPI for 2× ADF4351 + 2× AD9910 + 1× MCP3208; a single hardware SPI bus with multiple chip-selects, or a mix of hardware SPI + bit-banged GPIO, both work |
| MCP3208 | 1 | 8-ch 12-bit SPI ADC | RPi has no native analog input; reads 4 power detectors + 1–2 photodiodes with channels to spare |

## Ignition RF power chain (×2, one per coil)

| Part | Qty | Role | Notes |
|---|---|---|---|
| MMIC driver amp, ~20 dB gain, DC–4 GHz (e.g. Mini-Circuits PGA-103+ class part) | 2 | Bring ADF4351 output up to GaN gate drive level | Confirm gain/P1dB budget once the CGH40010's actual drive requirement is pulled from its datasheet |
| Wolfspeed CGH40010 (10 W, DC–6 GHz GaN HEMT) | 2 | Class E power stage | Needs a proper bias sequencer (Vgs before Vds) — see Safety section in README |
| Parallel-circuit Class E output matching network (discrete L/C or microstrip) | 2 | Shapes the switching waveform, transforms to load impedance | Design/tune per-board; loaded impedance depends on the loop applicator and will shift once plasma is struck |
| 2.4 GHz-band directional coupler, ~20 dB coupling | 2 | Sample forward/reflected power | Off-the-shelf RF coupler rated for the band |
| AD8318 log-amp power detector | 4 (2 per channel: fwd + rev) | Convert coupled RF to DC for the ADC | 1 MHz–8 GHz range, 60 dB dynamic range — comfortably covers 2.45 GHz |
| Single-turn/hairpin copper loop applicator | 2 | Couples ignition RF into the chamber | Custom-fabricated per final chamber geometry; not a wound coil (see `rf-design.md` for why) |

## Sustain RF power chain (×2, one per coil)

| Part | Qty | Role | Notes |
|---|---|---|---|
| RF power MOSFET (induction-heating/ham-radio class part) | 2 | Class D/E sustain power stage | Tens of watts; well-trodden design space at 13.56 MHz |
| Multi-turn coil | 2 | Sustain + position-control applicator | Wound directly on/around the torus tube near top and bottom; ordinary coil design math applies at this frequency |
| Directional coupler + AD8318 pair | 2 sets | Continuous Γ monitoring during sustain/control | Same detection approach as ignition side |

## Sensing

| Part | Qty | Role |
|---|---|---|
| Photodiode(s) (or small linear photodiode array) | 2+ | Strike confirmation + vertical position sensing for the control loop |

## Chamber / vacuum (scoped, not detailed here — separate subsystem)

| Item | Notes |
|---|---|
| Quartz (preferred) or borosilicate toroidal glass envelope | Quartz has lower RF/microwave loss tangent and higher thermal limit near the coupling regions; borosilicate is a cheaper acceptable first-prototype option |
| Roughing vacuum pump (two-stage rotary vane or similar) | For bakeout/purge before xenon backfill |
| Xenon gas supply + needle valve + capacitance manometer | Sealed fill to 20–50 Torr target |
| Enclosure | Required for RF safety — see README Safety section |

## Not yet specified

- Exact matching-network component values (depend on measured, not assumed,
  loaded impedance once a real loop/coil and chamber exist)
- Bias-sequencer circuit for the GaN HEMTs
- RF relay or PIN-diode switch, if using the "sequential" handoff pattern
  from `rf-design.md` rather than "assisted"
