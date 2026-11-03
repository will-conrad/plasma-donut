# Datasheet catalogue: how to use it

Start with [INDEX.md](INDEX.md). This folder lives inside `Microcontroller-PCB/`, so it travels with the KiCad project.

## Open-source tools used
- **poppler-utils** (`pdfinfo`, `pdftotext`) extracts every page of every datasheet into `text/` with page markers.
- **SQLite FTS5** (built into Python's `sqlite3`) is the full-text search engine in `datasheets.db`. It ranks results with BM25 and stems words, so "clamp" also matches "clamping".
- **kicad-cli** exports the BOM and runs the ERC/DRC/parity checks in `kicad-reports/`.

## Searching
Run these in Terminal from this folder. Nothing needs installing; macOS's `python3` has sqlite3 with FTS5.
```bash
python3 search.py backlight current           # key specs + the best-matching datasheet pages
python3 search.py hysteresis --part nx_74lvc1g17
python3 search.py 'NEAR(input clamp)' --pages 5  # FTS5 operators: AND OR NOT NEAR(a b) "exact phrase" prefix*
python3 search.py --parts                     # part keys, reference designators, roles
```
Results look like `[mcp3208 p.3] Sample capacitor (CSAMPLE): typ 20 pF`. **p.N is the PDF page**, so you can jump there in Preview with ⌥⌘G.

Other ways in:
- Open `specs.csv` in Excel and filter by `part`, `category` or `tags`.
- Run `grep -n -i hysteresis text/*.txt`.
- Use DB Browser for SQLite (free) on `datasheets.db`.

## Conventions
- **Part keys** match the file names: `pico2 rp2350 mcp3208 nhd_c12864lz st7565r ntcs0603e3 lm66100 ao3400a nx_74lvc1g17 nx_74lvc1g86 bat54ws_mcc yageo_rc_l kemet_x7r kemet_c0g omron_b3f`.
- **REQ-xx / DC-xx** are defined in `design-requirements.md`. **Issue #n** is in `ISSUES.md`.
- **Text-extraction artifacts:** in symbol fonts, "mW" can mean mΩ and "mA" can mean µA (the AO3400A sheet especially). The values in `specs.csv` and the cards were corrected by hand.

## Adding a datasheet (e.g. the two Nexperia PDFs)
```bash
f=nx_74lvc1g17     # part key; save the PDF as pdf/$f.pdf first
n=$(pdfinfo pdf/$f.pdf | awk '/Pages/{print $2}'); : > text/$f.txt
for p in $(seq 1 $n); do echo "=== $f p.$p ===" >> text/$f.txt; pdftotext -layout -f $p -l $p pdf/$f.pdf - | tr -d '\f' >> text/$f.txt; done
python3 - <<'EOF'
import sqlite3,re; f="nx_74lvc1g17"; con=sqlite3.connect("datasheets.db")
t=open(f"text/{f}.txt").read(); c=re.split(r"^=== \S+ p\.(\d+) ===$",t,flags=re.M)
con.execute("DELETE FROM pages WHERE part=?",(f,))
for i in range(1,len(c),2): con.execute("INSERT INTO pages VALUES(?,?,?)",(f,int(c[i]),c[i+1]))
con.execute("UPDATE parts SET pdf=? WHERE part=?",(f"{f}.pdf",f)); con.commit()
EOF
```
`pdfinfo`/`pdftotext` come from poppler (`brew install poppler`). For a new part, also add rows to `specs.csv`, a `parts/<key>.md` card, and a line in INDEX.md.

## After a schematic change
1. Re-export the BOM: `kicad-cli sch export bom … -o bom-kicad.csv`, and diff it against BOM-vs-orders.md.
2. Re-run the affected DC-xx check in design-requirements.md. Every check shows its formula, so you can swap in the new values.
3. Re-run ERC/DRC and drop the reports in `kicad-reports/`.
