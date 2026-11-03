# config/

`pins.h`: one `#define` per GPIO, taken from `../../PINMAP.md`
(never edit a pin without checking the KiCad schematic). `config.h`: limits, thresholds and the bodge flags from `../../docs/REWORK.md`.
`cal.c/.h`: calibration values saved in the last flash sector (version + CRC).
