#!/usr/bin/env python3
"""flagcheck.py -- deterministic design flag checker for KiCad boards + datasheet catalogue.

Implements the automatable rules in RULES.md. Every flag states its basis:
  netlist  = fact read from the KiCad files        ds:...  = cited datasheet page (page-verified)
  calc     = computed here from netlist values      web:... = secondary source, not page-verified
  assumed  = engineering assumption (says so)

Usage (from the CAPSTONE folder):
  python3 Microcontroller-PCB/datasheets/flagcheck/flagcheck.py --capstone .
Writes Microcontroller-PCB/datasheets/flagcheck/FLAGS.md (+ FLAGS.json). Exit code 1 if any 'error' flags.
No third-party packages needed. kicad-cli is used for ERC/DRC if found (optional).
"""
import argparse, ast, csv, importlib.util, json, math, os, re, runpy, shutil, subprocess, sys
from collections import defaultdict
sys.dont_write_bytecode = True   # don't leave __pycache__ in the project folders

SEV_ORDER = {"error": 0, "warn": 1, "info": 2}

# ------------------------------------------------------------------ S-expression helpers
_TOK = re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+')

def sparse(text):
    st = [[]]
    for m in _TOK.finditer(text):
        x = m.group(0)
        if x == "(":
            st.append([])
        elif x == ")":
            v = st.pop(); st[-1].append(v)
        else:
            st[-1].append(x[1:-1] if x.startswith('"') else x)
    return st[0][0]

def kids(node, name):
    return [c for c in node[1:] if isinstance(c, list) and c and c[0] == name]

def kid(node, name):
    k = kids(node, name)
    return k[0] if k else None

# ------------------------------------------------------------------ value parsing
_MULT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "k": 1e3, "K": 1e3, "M": 1e6, "R": 1}

def parse_value(s):
    """'10k'->1e4, '7.15k'->7150, '0.1uF'->1e-7, '10pF 250V C0G'->1e-11, '24'->24, '4k7'->4700."""
    if s is None:
        return None
    s = s.strip().split()[0] if s.strip() else s
    m = re.match(r"^([\d.]+)\s*([pnuµmkKMR]?)(\d*)", s)
    if not m:
        return None
    try:
        base = float(m.group(1) + ("." + m.group(3) if m.group(3) and "." not in m.group(1) else ""))
    except ValueError:
        return None
    return base * _MULT.get(m.group(2), 1) if m.group(2) else base

# ------------------------------------------------------------------ design loading
def load_pcb(path):
    root = sparse(open(path, encoding="utf-8").read())
    fps = {}
    for fp in kids(root, "footprint"):
        ref = val = ""
        for p in kids(fp, "property"):
            if p[1] == "Reference": ref = p[2]
            if p[1] == "Value": val = p[2]
        at = kid(fp, "at"); x0, y0 = float(at[1]), float(at[2]); rot = float(at[3]) if len(at) > 3 else 0.0
        a = math.radians(-rot)
        pads = {}
        for pd in kids(fp, "pad"):
            pa = kid(pd, "at"); px, py = float(pa[1]), float(pa[2])
            net = kid(pd, "net"); nn = net[-1] if net else ""
            gx = x0 + px * math.cos(a) - py * math.sin(a); gy = y0 + px * math.sin(a) + py * math.cos(a)
            pads.setdefault(pd[1], (gx, gy, nn))
        fps[ref] = dict(value=val, footprint=fp[1], pads=pads)
    nets = defaultdict(list)
    for r, f in fps.items():
        for p, (_, _, n) in f["pads"].items():
            if n: nets[n].append((r, p))
    return fps, nets

def load_sch_pin_types(path):
    """lib_id -> {pin_number: (electrical_type, pin_name)}; ref -> lib_id."""
    root = sparse(open(path, encoding="utf-8").read())
    libs = {}
    ls = kid(root, "lib_symbols")
    for sym in kids(ls, "symbol") if ls else []:
        pins = {}
        def walk(n):
            for c in n[1:]:
                if isinstance(c, list) and c:
                    if c[0] == "pin":
                        name = kid(c, "name"); num = kid(c, "number")
                        if num: pins[num[1]] = (c[1], name[1] if name else "")
                    elif c[0] == "symbol":
                        walk(c)
        walk(sym)
        libs[sym[1]] = pins
    ref_lib = {}
    for s in kids(root, "symbol"):
        lid = kid(s, "lib_id"); ref = None
        for p in kids(s, "property"):
            if p[1] == "Reference": ref = p[2]
        if lid and ref and not ref.startswith("#"):
            ref_lib[ref] = lid[1]
    return libs, ref_lib

# ------------------------------------------------------------------ flag container
class Flags:
    def __init__(self, waivers):
        self.items, self.waivers = [], waivers
    def add(self, rule, sev, where, msg, basis, evidence="", fix=""):
        key = f"{rule.split(' ')[0]}:{where}"
        if key in self.waivers:
            sev, msg = "info", msg + f" (WAIVED: {self.waivers[key]})"
        self.items.append(dict(rule=rule, sev=sev, where=where, msg=msg, basis=basis, evidence=evidence, fix=fix))

def btype(basis):
    b = basis.split(":")[0]
    return {"ds": "cited", "web": "web (not page-verified)", "calc": "computed", "assumed": "ASSUMED",
            "netlist": "netlist fact"}.get(b, b)

# ------------------------------------------------------------------ checks
def chk_pin_expect(F, R, fps):
    for rp, spec in R.PIN_EXPECT.items():
        exp, name, basis = spec[:3]; sev_override = spec[3] if len(spec) > 3 else None
        ref, pin = rp.split(".")
        if ref not in fps or pin not in fps[ref]["pads"]:
            F.add("R-B2 pinout", "error", rp, f"{name}: pad not found on PCB", basis); continue
        net = fps[ref]["pads"][pin][2]
        if exp.startswith("="):
            r2, p2 = exp[1:].split("."); exp_net = fps[r2]["pads"][p2][2]
        else:
            exp_net = exp
        if net != exp_net:
            sev = sev_override or ("error" if net.startswith("unconnected") or exp_net in ("VCC", "+5V") else "warn")
            F.add("R-B2 pinout", sev, rp, f"{name} is on '{net}', datasheet expects '{exp_net}'", basis,
                  evidence=f"PCB pad {rp} net = {net}")

def rail_of(net, R):
    return R.RAILS.get(net)

def chk_rails(F, R, fps):
    for rp, (rec, absmax, basis) in R.PIN_LIMITS.items():
        ref, pin = rp.split(".")
        net = fps.get(ref, {}).get("pads", {}).get(pin, (0, 0, ""))[2]
        rail = rail_of(net, R)
        if not rail:
            F.add("R-C1 ratings", "info", rp, f"net '{net}' has no rail voltage defined -- cannot check", basis); continue
        nom, hi, rbasis = rail
        if hi > absmax:
            F.add("R-C1 ratings", "error", rp, f"{net} can reach {hi} V > abs max {absmax} V", basis, f"rail basis: {rbasis}")
        elif hi > rec:
            F.add("R-C1 ratings", "warn", rp, f"{net} up to {hi} V exceeds recommended max {rec} V (abs {absmax} V)", basis, f"rail basis: {rbasis}")

def chk_decap(F, R, fps):
    gnds = {"GND", "GNDA"}
    for rp, (cmin, dmax, basis) in R.DECAP.items():
        ref, pin = rp.split(".")
        px, py, net = fps[ref]["pads"][pin]
        best = []
        for cref, f in fps.items():
            if not cref.startswith("C"): continue
            pn = {p: v for p, v in f["pads"].items()}
            nets = {v[2] for v in pn.values()}
            if net in nets and nets & gnds:
                d = min(math.hypot(v[0] - px, v[1] - py) for v in pn.values() if v[2] == net)
                best.append((d, cref, parse_value(f["value"]) or 0, f["value"]))
        best.sort()
        near = [b for b in best if b[0] <= dmax]
        total = sum(b[2] for b in near)
        if not near:
            F.add("R-E1 decoupling", "warn", rp, f"no cap to ground within {dmax} mm of {net}", basis,
                  f"nearest: {best[0][1]} at {best[0][0]:.1f} mm" if best else "none")
        elif total < cmin * 0.99:
            F.add("R-C2 required parts", "warn", rp,
                  f"{' + '.join(b[1] + ' ' + b[3] for b in near)} within {dmax} mm = {total*1e6:.2f} µF < required {cmin*1e6:.2f} µF",
                  basis, "calc: sum of caps on the pin's net to GND/GNDA within distance")

def chk_undriven(F, fps, nets, libs, ref_lib):
    drivers = {"output", "bidirectional", "tri_state", "power_out", "open_collector", "open_emitter"}
    for net, members in nets.items():
        if net.startswith("unconnected") or net in ("GND", "GNDA"): continue
        if len(members) == 1:
            r, p = members[0]
            F.add("R-B3 floating", "warn", f"{r}.{p}", f"net '{net}' has a single pad", "netlist"); continue
        driven, desc = False, []
        for r, p in members:
            pref = re.match(r"[A-Z]+", r).group(0)
            if pref in ("C", "TP", "JP", "H"):
                desc.append(f"{r}(cap/tp)"); continue
            if pref in ("R", "L", "D", "Q", "J", "SW", "FB"):
                driven = True; break
            ptype = libs.get(ref_lib.get(r, ""), {}).get(p, ("unknown", ""))[0]
            desc.append(f"{r}.{p}({ptype})")
            if ptype in drivers or ptype in ("passive", "unspecified", "unknown", "power_in"):
                if ptype != "power_in":
                    driven = True; break
        if not driven:
            F.add("R-B3 floating", "error", net, f"nothing drives '{net}': only {', '.join(desc)}", "netlist",
                  fix="connect a source, or disable the input in firmware and document it")

def chk_power_pins(F, fps, libs, ref_lib, R):
    ok = getattr(R, "POWER_PIN_OK_UNCONNECTED", {})
    for ref, lid in ref_lib.items():
        if ref not in fps: continue
        for num, (ptype, name) in libs.get(lid, {}).items():
            if ptype == "power_in":
                net = fps[ref]["pads"].get(num, (0, 0, "MISSING"))[2]
                if (not net or net.startswith("unconnected") or net == "MISSING") and f"{ref}.{num}" in ok:
                    F.add("R-B3 floating", "info", f"{ref}.{num}", f"{name} unconnected by design: {ok[f'{ref}.{num}']}", "netlist"); continue
                if not net or net.startswith("unconnected") or net == "MISSING":
                    F.add("R-B3 floating", "error", f"{ref}.{num}", f"power pin {name} not connected ({net})", "netlist")

def chk_mcu(F, R, fps):
    a1 = fps.get(R.MCU_REF)
    if not a1: return
    net_gpio = {}
    for pin, (_, _, net) in a1["pads"].items():
        if pin.isdigit() and int(pin) in R.PICO_PIN_GPIO:
            net_gpio[net] = R.PICO_PIN_GPIO[int(pin)]
    slices = defaultdict(list)
    for net, note in R.EDGE_COUNT_NETS.items():
        g = net_gpio.get(net)
        if g is None:
            F.add("R-C5 MCU pins", "error", net, "edge-count net not on any Pico GPIO", "ds:rp2350 p.980"); continue
        slices[(g % 16) // 2].append(net)
        if g % 2 == 0:
            F.add("R-C5 MCU pins", "warn" if note.startswith("mitigated") else "error", net,
                  f"GPIO{g} is even (PWM A): no hardware edge counting. {note}", "ds:rp2350 p.980")
    for s, ns in slices.items():
        if len(ns) > 1:
            F.add("R-C5 MCU pins", "error", ",".join(ns), f"share PWM slice {s}: inputs are OR'd", "ds:rp2350 p.976")
    for net in R.PICO_ADC_NETS:
        g = net_gpio.get(net)
        if g not in (26, 27, 28):
            F.add("R-C5 MCU pins", "error", net, f"analog net on GPIO{g}, not an ADC pin", "ds:pico2 p.15")

def chk_gate(F, R, fps, nets):
    for rp, gnd in R.GATE_PULLDOWN.items():
        ref, pin = rp.split(".")
        net = fps[ref]["pads"][pin][2]
        ok = any(r.startswith("R") and gnd in {v[2] for v in fps[r]["pads"].values()} for r, _ in nets[net])
        if not ok:
            F.add("R-B5 polarity/boot", "warn", rp, f"gate net {net} has no resistor to {gnd}: undefined at boot", "calc")

def chk_drift(F, R, fps, capstone):
    cfgp = os.path.join(capstone, R.FIRMWARE_CONFIG)
    if not os.path.exists(cfgp):
        F.add("R-D3 drift", "info", R.FIRMWARE_CONFIG, "firmware config not found -- drift check skipped", "-"); return
    cfg = runpy.run_path(cfgp)      # config.py is pure constants by design (no machine import)
    vals = {r: parse_value(f["value"]) for r, f in fps.items()}
    for const, expr in R.DRIFT.items():
        if const not in cfg:
            F.add("R-D3 drift", "warn", const, "constant missing from firmware config", "netlist"); continue
        try:
            sch = eval(re.sub(r"\b([RC]\d+)\b", lambda m: repr(vals[m.group(1)]), expr), {"__builtins__": {}})
        except Exception as e:  # noqa
            F.add("R-D3 drift", "info", const, f"could not evaluate {expr}: {e}", "-"); continue
        fw = cfg[const]
        if not math.isclose(float(fw), float(sch), rel_tol=0.01):
            F.add("R-D3 drift", "error", const, f"firmware {const} = {fw} but schematic {expr} = {sch:g}", "calc",
                  f"{R.FIRMWARE_CONFIG}")
    for doc in R.LIVING_DOCS:
        p = os.path.join(capstone, doc)
        if not os.path.exists(p): continue
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            for pat, why in R.STALE_TERMS:
                if re.search(pat, line) and not re.search(r"not\s+(82|9\.2|2\.1)|\(not |old brief|superseded|stale|still says|brief assumed|was \d", line, re.I):
                    F.add("R-D3 drift", "warn", f"{doc}:{i}", f"stale value: {why}", "calc", line.strip()[:120])

def chk_rpower(F, R, fps):
    rating = {"R_0805": (0.125, "ds:yageo_rc_l p.5"), "R_1206": (0.25, "ds:yageo_rc_l p.6"), "R_0603": (0.1, "assumed")}
    for ref, (vrms, vbasis, note) in getattr(R, "RESISTOR_STRESS", {}).items():
        f = fps.get(ref); r = parse_value(f["value"]) if f else None
        if not r: continue
        pr = next((v for k, v in rating.items() if k in f["footprint"]), None)
        if not pr: continue
        p = vrms ** 2 / r
        sev = "warn" if p > pr[0] else ("info" if p > 0.5 * pr[0] else None)
        if sev:
            F.add("R-C4 derating", sev, ref, f"P = ({vrms} V)^2 / {f['value']} = {p:.3f} W vs rated {pr[0]} W at 70 °C. {note}",
                  pr[1], f"calc; voltage basis: {vbasis}")

def chk_package(F, R, fps):
    for ref, (mpn, fpsub, basis) in R.PACKAGE.items():
        f = fps.get(ref)
        if not f: continue
        if fpsub not in f["footprint"]:
            F.add("R-E3 footprint", "error", ref, f"ordered {mpn} needs '{fpsub}', footprint is {f['footprint']}", basis)

def chk_orders(F, R, fps):
    short = defaultdict(list)
    for ref in sorted(fps):
        pref = re.match(r"[A-Z]+", ref).group(0)
        st = R.ORDER_STATUS.get(ref, R.ORDER_STATUS.get(pref, R.ORDER_DEFAULT))
        if st in ("in_transit", "unconfirmed"):
            short[st].append(ref)
    for st, refs in short.items():
        F.add("R-F1 procurement", "warn" if st == "in_transit" else "error", st, f"{len(refs)} parts {st}: {', '.join(refs)}",
              "BOM-vs-orders.md", fix="see REWORK.md step A for stand-ins")
    for ref, why in R.SINGLE_QTY_CRITICAL.items():
        F.add("R-F2 spares", "info", ref, why, "BOM-vs-orders.md")

def chk_citations(F, dsdir):
    spec = os.path.join(dsdir, "specs.csv")
    if not os.path.exists(spec): return 0, 0, 0
    pages_cache = {}
    def page(part, pg):
        if part not in pages_cache:
            tp = os.path.join(dsdir, "text", part + ".txt")
            if not os.path.exists(tp): pages_cache[part] = None
            else:
                ch = re.split(r"^=== \S+ p\.(\d+) ===$", open(tp, encoding="utf-8", errors="replace").read(), flags=re.M)
                pages_cache[part] = {int(ch[i]): ch[i + 1] for i in range(1, len(ch), 2)}
        d = pages_cache[part]
        return None if d is None else d.get(int(pg), "")
    ok = bad = web = 0
    words = {"1/8": "0.125", "1/4": "0.25"}
    for r in csv.DictReader(open(spec, encoding="utf-8")):
        txt = page(r["part"], r["pdf_page"])
        if txt is None:
            web += 1; continue
        t = txt.replace("−", "-").replace("–", "-").replace(" ", "")
        for k, v in words.items():
            t += v if k in t else ""
        nums = [n for f in ("min", "typ", "max") for n in re.findall(r"-?\d+(?:\.\d+)?", r[f].replace("−", "-"))]
        def found(n):
            v = n.lstrip("-")
            alts = {v, v.rstrip("0").rstrip(".") if "." in v else v}
            try:
                f = float(v); alts |= {f"{f*1000:g}", f"{f/1000:g}"}
            except ValueError:
                pass
            return any(a and a in t for a in alts)
        miss = [n for n in nums if not found(n)]
        if miss:
            bad += 1
            F.add("R-A2 citation", "warn", f"{r['part']} p.{r['pdf_page']}", f"'{r['parameter']}' value(s) {miss} not found on cited page",
                  f"ds:{r['part']} p.{r['pdf_page']}", fix="open the page and correct value or page")
        else:
            ok += 1
    if web:
        F.add("R-A2 citation", "info", "specs.csv", f"{web} spec rows come from web-fetched datasheets (no local text): not page-verifiable",
              "web", fix="download the PDFs into pdf/ and re-index")
    return ok, bad, web

TAG = re.compile(r"\(\w+ p\.\d+|\bp\.\d+|\[(calc|inferred|assumed|measured|web|netlist)[^\]]*\]|\bDC-\d+|\$[^$]+\$|ds:\w+|datasheet", re.I)
NUMUNIT = re.compile(r"\b\d+(?:\.\d+)?\s?(?:mV|V|mA|µA|uA|A|Ω|kΩ|MΩ|pF|nF|µF|uF|MHz|kHz|Hz|ns|µs|us|ms|°C|W|mW)\b")

def chk_claims(F, docs):
    stats = {}
    for p in docs:
        if not os.path.exists(p): continue
        total = tagged = 0; untagged = []
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            if line.lstrip().startswith(("|---", "#", "```")): continue
            if NUMUNIT.search(line):
                total += 1
                if TAG.search(line): tagged += 1
                else: untagged.append((i, line.strip()[:100]))
        stats[os.path.basename(p)] = (tagged, total)
        if untagged:
            F.add("R-A1 provenance", "info", os.path.basename(p),
                  f"{len(untagged)}/{total} lines with numeric claims carry no source tag", "calc",
                  "; ".join(f"L{i}: {t}" for i, t in untagged[:3]), fix="tag as (part p.N), [calc], [assumed], [measured] or [web]")
    return stats

def chk_tools(F, R, kdir, kicad_cli):
    if not kicad_cli:
        F.add("R-E2 tools", "info", "ERC/DRC", "kicad-cli not found: ERC/DRC not run this time", "-"); return
    sch = os.path.join(kdir, R.PROJECT + ".kicad_sch"); pcb = os.path.join(kdir, R.PROJECT + ".kicad_pcb")
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_reports"); os.makedirs(tmp, exist_ok=True)
    erc = os.path.join(tmp, "erc.json"); drc = os.path.join(tmp, "drc.json")
    subprocess.run([kicad_cli, "sch", "erc", "--format", "json", "--severity-error", "-o", erc, sch], capture_output=True)
    subprocess.run([kicad_cli, "pcb", "drc", "--format", "json", "--schematic-parity", "--severity-error", "-o", drc, pcb], capture_output=True)
    for name, path in (("ERC", erc), ("DRC", drc)):
        if not os.path.exists(path):
            F.add("R-E2 tools", "warn", name, "report not produced", "-"); continue
        j = json.load(open(path))
        viol = [v for s in j.get("sheets", [{}]) for v in s.get("violations", [])] + j.get("violations", [])
        viol = [v for v in viol if "library" not in v.get("description", "").lower()]
        unc = j.get("unconnected_items", [])
        par = j.get("schematic_parity", [])
        for v in viol:
            F.add("R-E2 tools", "error", name, v.get("description", "?"), "netlist")
        for u in unc:
            items = u.get("items", [])
            where = items[0].get("description", "?") if items else "?"
            m = re.search(r"Pad (\S+) .*? of (\S+)", where)
            key = f"{m.group(2)}.{m.group(1)}" if m else where
            F.add("R-E2 tools", "error", key, f"unrouted: {where}", "netlist")
        for v in par:
            F.add("R-E2 tools", "error", "parity", v.get("description", "?"), "netlist")
        if not viol and not unc and not par:
            F.add("R-E2 tools", "info", name, "0 errors", "netlist")
    # map waiver keys for DRC unconnected
    for it in F.items:
        if it["rule"].startswith("R-E2") and it["where"] in [k.split(":", 1)[1] for k in F.waivers if k.startswith("DRC:")]:
            it["sev"] = "info"; it["msg"] += f" (WAIVED: {F.waivers['DRC:' + it['where']]})"

# ------------------------------------------------------------------ report
def write_report(F, outdir, meta, cite_stats, claim_stats):
    items = sorted(F.items, key=lambda x: (SEV_ORDER[x["sev"]], x["rule"], x["where"]))
    n = {s: sum(1 for i in items if i["sev"] == s) for s in SEV_ORDER}
    L = ["# FLAGS: automated design check", "",
         f"Board: `{meta['board']}` · checked {meta['when']} · rules: [RULES.md](RULES.md) · tool: `flagcheck.py`", "",
         f"**{n['error']} error · {n['warn']} warn · {n['info']} info**", "",
         "Basis column: **netlist fact** (read from KiCad files) · **cited** (datasheet page, number verified on that page) · "
         "**computed** (calculated here) · **web** (secondary source, not page-verified) · **ASSUMED** (engineering assumption, needs confirmation).", "",
         "| # | Sev | Rule | Where | Finding | Basis | Evidence / fix |", "|---|---|---|---|---|---|---|"]
    for k, i in enumerate(items, 1):
        ev = " · ".join(x for x in (i["evidence"], ("fix: " + i["fix"]) if i["fix"] else "") if x)
        L.append(f"| {k} | {i['sev']} | {i['rule']} | `{i['where']}` | {i['msg']} | {btype(i['basis'])} ({i['basis']}) | {ev} |".replace("\n", " "))
    ok, bad, web = cite_stats
    L += ["", "## Transparency ledger", "",
          f"- **Cited spec rows:** {ok} verified on their page · {bad} mismatched · {web} web-only (not verifiable locally)."]
    for d, (t, tot) in claim_stats.items():
        L.append(f"- **{d}:** {t}/{tot} numeric lines carry a source tag ({(100*t/tot if tot else 100):.0f} %).")
    L += ["- **Assumptions this run depends on** (from board_rules.py):"]
    for a in meta["assumptions"]:
        L.append(f"  - {a}")
    open(os.path.join(outdir, "FLAGS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(dict(meta=meta, flags=items), open(os.path.join(outdir, "FLAGS.json"), "w"), indent=1, ensure_ascii=False)
    return n

def find_kicad_cli(explicit):
    for c in [explicit, shutil.which("kicad-cli"), "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"]:
        if c and os.path.exists(c): return c
    return None

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--capstone", required=True, help="folder containing Microcontroller-PCB/ and pico-firmware/")
    ap.add_argument("--rules", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "board_rules.py"))
    ap.add_argument("--kicad-cli", default=None)
    ap.add_argument("--no-tools", action="store_true", help="skip kicad-cli ERC/DRC")
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("board_rules", a.rules); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
    kdir = os.path.join(a.capstone, R.PROJECT); dsdir = os.path.join(kdir, "datasheets")
    fps, nets = load_pcb(os.path.join(kdir, R.PROJECT + ".kicad_pcb"))
    libs, ref_lib = load_sch_pin_types(os.path.join(kdir, R.PROJECT + ".kicad_sch"))
    F = Flags(R.WAIVERS)
    chk_pin_expect(F, R, fps); chk_rails(F, R, fps); chk_decap(F, R, fps)
    chk_undriven(F, fps, nets, libs, ref_lib); chk_power_pins(F, fps, libs, ref_lib, R)
    chk_mcu(F, R, fps); chk_gate(F, R, fps, nets); chk_drift(F, R, fps, a.capstone)
    chk_package(F, R, fps); chk_orders(F, R, fps); chk_rpower(F, R, fps)
    cite = chk_citations(F, dsdir)
    claims = chk_claims(F, [os.path.join(dsdir, d) for d in ("design-requirements.md", "ISSUES.md", "REWORK.md")])
    if not a.no_tools:
        chk_tools(F, R, kdir, find_kicad_cli(a.kicad_cli))
    import datetime
    assumptions = sorted({v[-1] for d in (R.RAILS, R.PIN_LIMITS, R.DECAP) for v in d.values()
                          if isinstance(v[-1], str) and v[-1].startswith("assumed")})
    meta = dict(board=R.PROJECT, when=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), assumptions=assumptions)
    outdir = os.path.dirname(os.path.abspath(__file__))
    n = write_report(F, outdir, meta, cite, claims)
    print(f"{n['error']} error, {n['warn']} warn, {n['info']} info -> {os.path.join(outdir, 'FLAGS.md')}")
    sys.exit(1 if n["error"] else 0)

if __name__ == "__main__":
    main()
