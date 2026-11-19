#!/bin/bash
# Copy the control-board design files from the Mac into hardware/.
#
#   cd ~/plasma-donut                       # your clone of this repo
#   bash hardware/import_from_mac.sh        # dry run: lists what it would copy
#   bash hardware/import_from_mac.sh --go   # copy for real
#   bash hardware/import_from_mac.sh --go --include-orders   # also the order forms
#
# It only READS from OneDrive and ~/GERBS NEW; it never changes those files.
# The repo is public, so order forms (names, budget numbers, addresses) are
# left out unless you pass --include-orders.
#
# Override any source path with an environment variable, e.g.
#   CAPSTONE="/path/to/CAPSTONE" GERBERS="/path/to/GERBS NEW" bash hardware/import_from_mac.sh
set -euo pipefail   # pipefail: a failed rsync stops the script instead of looking like success
command -v rsync >/dev/null || { echo "rsync not found (macOS ships it in /usr/bin)."; exit 1; }

GO=0; ORDERS=0
for a in "$@"; do
  case "$a" in
    --go) GO=1 ;;
    --include-orders) ORDERS=1 ;;
    *) echo "unknown option: $a"; exit 2 ;;
  esac
done

REPO="$(cd "$(dirname "$0")/.." && pwd)"
HW="$REPO/hardware"
FALL="$HOME/Library/CloudStorage/OneDrive-UniversityofVirginia/Acedemics/2026/Fall 26"
CAPSTONE="${CAPSTONE:-$FALL/CAPSTONE}"
GERBERS="${GERBERS:-$HOME/GERBS NEW}"
DOWNLOADS="${DOWNLOADS:-$HOME/Downloads}"

# The CAPSTONE folder was renamed once (CLAUDE.md, Step 0): find it by the schematic.
if [ ! -f "$CAPSTONE/Microcontroller-PCB/Microcontroller-PCB.kicad_sch" ]; then
  sch="$(find "$FALL" -name Microcontroller-PCB.kicad_sch -not -path '*backups*' 2>/dev/null | head -1 || true)"
  if [ -z "$sch" ]; then
    echo "Can't find Microcontroller-PCB.kicad_sch under: $FALL"
    echo "Set CAPSTONE=/path/to/CAPSTONE and run again."; exit 1
  fi
  CAPSTONE="$(dirname "$(dirname "$sch")")"
fi
REVA="$CAPSTONE/Microcontroller-PCB"

# KiCad noise that never belongs in git.
EXCL=(--exclude '*-backups/' --exclude '*.lck' --exclude 'fp-info-cache' --exclude '*.kicad_prl'
      --exclude '.DS_Store' --exclude '~*' --exclude '_autosave-*' --exclude '.history/')

if [ $GO = 1 ]; then RS=(rsync -a --itemize-changes); else RS=(rsync -a --dry-run --itemize-changes); fi

copy() {  # copy <label> <src dir/> <dest dir/> [extra rsync args...]
  local label="$1" src="$2" dst="$3"; shift 3
  if [ ! -e "$src" ]; then echo "  -- skip $label: not found ($src)"; return; fi
  echo "== $label"
  echo "   from $src"
  echo "   to   ${dst#$REPO/}"
  [ $GO = 1 ] && mkdir -p "$dst"
  "${RS[@]}" "${EXCL[@]}" "$@" "$src" "$dst" | sed 's/^/   /'
}

echo "CAPSTONE: $CAPSTONE"
[ $GO = 1 ] || echo "(dry run: nothing is copied; add --go to copy)"
echo

# 1. Rev A KiCad project as fabbed: schematic, PCB, project, local libraries.
#    The datasheets/ subfolder is skipped: hardware/datasheets/ replaces it.
copy "Rev A KiCad project" "$REVA/" "$HW/rev-a/kicad/" --exclude 'datasheets/'

# 2. Rev A engineering records from the old datasheet catalogue.
for d in flagcheck kicad-reports; do
  copy "Rev A $d" "$REVA/datasheets/$d/" "$HW/rev-a/$d/"
done
for f in bom-kicad.csv BOM-vs-orders.md; do
  copy "Rev A $f" "$REVA/datasheets/$f" "$HW/rev-a/bom/"
done
# The fab and assembler BOM spreadsheets (BOM-RevA-fab-*.xlsx and friends).
for f in "$REVA"/datasheets/BOM-*.xlsx "$REVA"/datasheets/BOM-*.csv; do
  [ -e "$f" ] && copy "Rev A $(basename "$f")" "$f" "$HW/rev-a/bom/"
done

# 3. The gerbers exactly as sent to manufacturing.
copy "Rev A gerbers (as fabbed)" "$GERBERS/" "$HW/rev-a/gerbers/"

# 4. The V2 project: any KiCad project under CAPSTONE other than Rev A whose
#    folder name looks like V2 / Rev B. Listed so you can check it's the right one.
echo
echo "Looking for a V2 project under CAPSTONE..."
found=0
while IFS= read -r pro; do
  dir="$(dirname "$pro")"
  [ "$dir" = "$REVA" ] && continue
  case "$(basename "$dir" | tr 'A-Z' 'a-z')" in
    *v2*|*rev*b*|*ver*b*|*revb*) ;;
    *) continue ;;
  esac
  found=1
  copy "V2 KiCad project ($(basename "$dir"))" "$dir/" "$HW/v2/kicad/"
done < <(find "$CAPSTONE" -maxdepth 3 -name '*.kicad_pro' -not -path '*backups*' 2>/dev/null)
if [ $found = 0 ]; then
  echo "  -- no V2 project folder found (looked for v2 / rev b in the folder name)."
  echo "     Other KiCad projects under CAPSTONE:"
  find "$CAPSTONE" -maxdepth 3 -name '*.kicad_pro' -not -path '*backups*' 2>/dev/null | sed "s#$CAPSTONE/#       #"
  echo "     Copy one by hand with: rsync -a \"<folder>/\" hardware/v2/kicad/"
fi

# 5. Order forms and the check-in log: private-ish, so opt-in only.
echo
if [ $ORDERS = 1 ]; then
  for f in "PlasmaDonut-PartsOrder3.xlsx" "Plasma Bagel-8.5-1.xlsx" "Plasma Bagel-PartsOrder8-1.xlsx"; do
    copy "order form $f" "$DOWNLOADS/$f" "$HW/rev-a/orders/"
  done
  for f in "$DOWNLOADS"/parts-checkin-*.csv; do
    [ -e "$f" ] && copy "check-in $(basename "$f")" "$f" "$HW/rev-a/orders/"
  done
  echo "  !! Open each order form and delete account numbers, addresses and phone"
  echo "     numbers before you commit: this repo is public."
else
  echo "Order forms skipped (public repo). Add --include-orders to copy them."
fi

echo
if [ $GO = 1 ]; then
  echo "Done. Next: git status, check nothing private slipped in, then commit."
else
  echo "Dry run finished. If the list looks right: bash hardware/import_from_mac.sh --go"
fi
