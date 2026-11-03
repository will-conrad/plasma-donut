# src/

Firmware source (MicroPython, Pico 2). Copied to the Pico's filesystem.

- `main.py` (top level, to be written) — entry point the Pico runs on boot.
- `config/` — pins and constants
- `drivers/` — chip-level drivers
- `sensors/` — turning raw readings into real units
- `ui/` — LCD pages, buttons, backlight

Pin assignments come from `../PINMAP.md`; required behaviour from `../CLAUDE.md`
and `../FIXES.md`.
