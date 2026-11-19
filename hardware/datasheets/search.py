#!/usr/bin/env python3
"""Search every datasheet .md in this folder and print hits as [part p.N].

    python3 hardware/datasheets/search.py hysteresis
    python3 hardware/datasheets/search.py "input impedance" --part rp2350
    python3 hardware/datasheets/search.py "t_?pd" --regex       # regular expression
    python3 hardware/datasheets/search.py backlight -C 2        # 2 lines of context

All words must appear on the same page (case-insensitive). p.N is the PDF
page, so you can jump straight there in Preview with Option-Cmd-G.
"""
import argparse
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def pages(path):
    """Yield (page_number, lines) for one generated .md file."""
    n, buf = None, []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^## Page (\d+)$", line)
            if m:
                if n is not None:
                    yield n, buf
                n, buf = int(m.group(1)), []
            elif n is not None and not line.startswith("```"):
                buf.append(line.rstrip("\n"))
    if n is not None:
        yield n, buf


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="+")
    ap.add_argument("--part", help="only this part key, e.g. mcp3208")
    ap.add_argument("--regex", action="store_true", help="treat the terms as one regular expression")
    ap.add_argument("-C", type=int, default=0, help="lines of context around each hit")
    ap.add_argument("--max", type=int, default=40, help="stop after this many pages")
    a = ap.parse_args()

    if a.regex:
        pats = [re.compile(" ".join(a.terms), re.I)]
    else:
        pats = [re.compile(re.escape(t), re.I) for t in a.terms]

    shown = 0
    for fn in sorted(os.listdir(HERE)):
        if not fn.endswith(".md") or fn in ("INDEX.md", "README.md"):
            continue
        key = fn[:-3]
        if a.part and key != a.part:
            continue
        for n, lines in pages(os.path.join(HERE, fn)):
            text = "\n".join(lines)
            if not all(p.search(text) for p in pats):
                continue
            print(f"[{key} p.{n}]")
            for i, line in enumerate(lines):
                if pats[0].search(line):
                    for j in range(max(0, i - a.C), min(len(lines), i + a.C + 1)):
                        print(f"    {lines[j].strip()[:160]}")
                    if a.C:
                        print("    --")
            shown += 1
            if shown >= a.max:
                print(f"... stopped at {a.max} pages (use --max or --part to narrow)")
                return


if __name__ == "__main__":
    main()
