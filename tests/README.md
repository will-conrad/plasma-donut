# tests/

- `host/`: tests that compile with the Mac's own C compiler (`cc`) and run without
  the Pico. They cover the pure-C code in `src/sensors/` and the button state
  machine. Use plain `assert` or a small framework such as Unity.
- `hw/` (to be added): one tiny program per step of the bring-up sequence in
  `../CLAUDE.md`, each built as its own UF2 and confirmed on the board before the next.
