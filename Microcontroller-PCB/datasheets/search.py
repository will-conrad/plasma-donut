#!/usr/bin/env python3
"""Search the control-board datasheet catalogue.

Uses datasheets.db (SQLite FTS5, ranked, stemmed: "clamp" also finds "clamping") if present,
otherwise falls back to specs.csv + text/*.txt.

Examples (run from this folder):
    python3 search.py backlight current             # key specs + ranked datasheet pages
    python3 search.py "input clamp" --part nx_74lvc1g17
    python3 search.py '"pull down" OR pulldown' --pages 10   # FTS5 syntax: AND OR NOT, NEAR(a b), "phrase", prefix*
    python3 search.py --parts                       # list part keys, ref des, roles
"""
import argparse, csv, os, re, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "datasheets.db")

def fts_query(terms):
    q = " ".join(terms)
    if re.search(r'\b(AND|OR|NOT)\b|NEAR\(|["*]', q):
        return q
    return " ".join('"' + t.replace('"', '') + '"' for t in terms)  # implicit AND of quoted words

def with_db(a):
    con = sqlite3.connect(DB)
    if a.parts:
        for row in con.execute("SELECT part, refs, role FROM parts ORDER BY part"):
            print(f"{row[0]:14} {row[1]:28} {row[2]}")
        return
    q = fts_query(a.terms)
    part_sql = " AND part = ?" if a.part else ""
    args = [q] + ([a.part] if a.part else [])
    rows = con.execute(f"SELECT part, parameter, symbol, min, typ, max, unit, conditions, pdf_page FROM specs WHERE specs MATCH ?{part_sql} ORDER BY bm25(specs)", args).fetchall()
    print(f"## Key specs ({len(rows)} hits)")
    for p, par, sym, mn, ty, mx, un, cond, pg in rows:
        rng = " / ".join(x for x in (mn and f"min {mn}", ty and f"typ {ty}", mx and f"max {mx}") if x)
        print(f"- [{p} p.{pg}] {par}{' (' + sym + ')' if sym else ''}: {rng} {un}{'  — ' + cond if cond else ''}")
    rows = con.execute(f"SELECT part, page, snippet(pages, 2, '[', ']', ' … ', 18) FROM pages WHERE pages MATCH ?{part_sql} ORDER BY bm25(pages) LIMIT ?", args + [a.pages]).fetchall()
    print(f"\n## Datasheet pages (top {len(rows)})")
    for p, pg, snip in rows:
        print(f"- [{p} {'§' if p.startswith('doc:') else 'p.'}{pg}] {re.sub(r'\s+', ' ', snip)}")

def without_db(a):
    rows = list(csv.DictReader(open(os.path.join(HERE, "specs.csv"), encoding="utf-8")))
    if a.parts:
        for k in sorted({r["part"] for r in rows}): print(k)
        return
    terms = [t.lower() for t in a.terms]
    for r in rows:
        if (not a.part or r["part"] == a.part) and all(t in " ".join(r.values()).lower() for t in terms):
            print(f"- [{r['part']} p.{r['pdf_page']}] {r['parameter']}: {r['min']} {r['typ']} {r['max']} {r['unit']} {r['conditions']}")
    tdir = os.path.join(HERE, "text"); n = 0
    for fn in sorted(os.listdir(tdir)):
        if a.part and fn[:-4] != a.part: continue
        page = "?"
        for ln in open(os.path.join(tdir, fn), encoding="utf-8", errors="replace"):
            m = re.match(r"^=== \S+ p\.(\d+) ===", ln)
            if m: page = m.group(1); continue
            if all(t in ln.lower() for t in terms):
                print(f"- [{fn[:-4]} p.{page}] {ln.strip()}"); n += 1
                if n >= a.pages: return

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="*")
    ap.add_argument("--part", help="limit to one part key (see --parts)")
    ap.add_argument("--pages", type=int, default=8, help="max datasheet-page hits (default 8)")
    ap.add_argument("--parts", action="store_true", help="list parts")
    a = ap.parse_args()
    if not a.terms and not a.parts:
        ap.print_help(); return
    (with_db if os.path.exists(DB) else without_db)(a)

if __name__ == "__main__":
    main()
