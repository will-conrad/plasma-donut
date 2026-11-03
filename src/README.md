# src/

Firmware source in C, built with the Raspberry Pi Pico SDK (2.3.1, at `~/pico/pico-sdk`) for the Pico 2 (RP2350).

- `main.c` (top level, to be written): `main()`, which runs init and then the cooperative main loop.
- `config/`: pins and constants
- `drivers/`: chip-level drivers
- `sensors/`: turning raw readings into real units (pure C, host-testable)
- `ui/`: LCD pages, buttons, backlight

Pin assignments come from `../PINMAP.md`; required behaviour from `../CLAUDE.md`
and `../FIXES.md`. Each module is a `.c`/`.h` pair and is added to the target in
the top-level `CMakeLists.txt`.
