# hardware/

Everything needed to design the **V2 control board**: datasheets, plus the Rev A design as it was fabbed, so V2 starts from what was actually built.

| Folder | What | Status |
|---|---|---|
| `datasheets/` | Every part's PDF with a full-text `.md` beside it, plus `manifest.json`, `search.py` and `build_md.py`. Start at [datasheets/INDEX.md](datasheets/INDEX.md) | ✅ in the repo (2 Nexperia PDFs to add by hand) |
| `rev-a/kicad/` | Rev A KiCad project (schematic, PCB, local footprint library) | ⏳ run the import script |
| `rev-a/gerbers/` | The gerbers exactly as sent to manufacturing (`~/GERBS NEW`) | ⏳ run the import script |
| `rev-a/bom/` | KiCad BOM export, BOM-vs-orders, and the fab/assembler BOM spreadsheets | ⏳ run the import script |
| `rev-a/flagcheck/`, `rev-a/kicad-reports/` | Design-flag checker and the ERC/DRC reports | ⏳ run the import script |
| `rev-a/orders/` | Order forms and the parts check-in log (opt-in, see below) | ⏳ optional |
| `v2/kicad/` | The V2 KiCad project | ⏳ run the import script |

Board issues, bodges and design checks are in `docs/` (ISSUES.md, REWORK.md, design-requirements.md). They apply to both the firmware and V2.

## Importing from the Mac
The KiCad files, gerbers and BOMs live on Will's Mac (OneDrive `CAPSTONE/` and `~/GERBS NEW`). `import_from_mac.sh` copies them in. It only **reads** those folders and never changes them.

```bash
cd ~/plasma-donut                                    # your clone of this repo
git pull
bash hardware/import_from_mac.sh                     # 1. dry run: lists every file it would copy
bash hardware/import_from_mac.sh --go                # 2. copy for real
git status                                           # 3. check the list, then commit and push
```

What it does:
- It finds `CAPSTONE/` even if the folder was renamed, by searching `Fall 26` for `Microcontroller-PCB.kicad_sch`.
- It skips KiCad clutter: `*-backups/`, `*.lck`, `fp-info-cache`, `*.kicad_prl`, and the old `datasheets/pdf` copy, since `hardware/datasheets/` replaces it.
- It finds the V2 project by looking for a KiCad project folder under `CAPSTONE` with "v2" or "rev b" in its name. If it doesn't find one, it lists the projects it did see so you can copy the right one by hand.
- **Order forms are opt-in** (`--include-orders`) because **this repo is public**. Order forms usually carry names, budget or account numbers and addresses. If you include them, scrub those before committing.

## Rules for V2 (from the Rev A lessons)
- Don't edit `rev-a/`: it's the record of what was built. Make V2 changes in `v2/kicad/`.
- Check every silkscreen label before the final gerber export: debug-header pins, the resistors near the ADC, and the parts around VDD tap A were missing labels on Rev A.
- V2 layout notes from Will: spread the subsystems out with more room around each, make the test-point holes as big as the terminal holes, and use smaller screw terminals than the 5.0 mm MKDS 1,5.
