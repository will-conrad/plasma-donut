#!/usr/bin/env python3
"""selftest.py -- checks the checker (rule R-G3: verify the verifier).
Copies the project into a temp folder, injects known faults, and confirms flagcheck.py catches each one.
Usage (from the CAPSTONE folder):  python3 Microcontroller-PCB/datasheets/flagcheck/selftest.py --capstone .
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))

FAULTS = [
    # (description, file relative to CAPSTONE, find, replace, expected rule, expected 'where' substring)
    ("U4 VCC pin moved to GND", "Microcontroller-PCB/Microcontroller-PCB.kicad_pcb", None, None, "R-B2", "U4.5"),
    ("firmware divider drift (82k)", "pico-firmware/src/config.py", "VDD_DIV_TOP = 100_000", "VDD_DIV_TOP = 82_000", "R-D3", "VDD_DIV_TOP"),
    ("wrong datasheet value in specs.csv", "Microcontroller-PCB/datasheets/specs.csv",
     "Reset low pulse width,tRW,1.0", "Reset low pulse width,tRW,7.5", "R-A2", "st7565r p.65"),
]

def inject_pad_net(path, ref, pad, net_name):
    t = open(path, encoding="utf-8").read()
    i = t.find(f'(property "Reference" "{ref}"'); j = t.find(f'(pad "{pad}"', i); k = t.find("(net ", j); e = t.find(")", k)
    open(path, "w", encoding="utf-8").write(t[:k] + f'(net 1 "{net_name}"' + t[e:])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--capstone", required=True); a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="flagselftest_")
    for sub in ("Microcontroller-PCB", "pico-firmware"):
        shutil.copytree(os.path.join(a.capstone, sub), os.path.join(tmp, sub),
                        ignore=shutil.ignore_patterns("pdf", "backups-*", "*-backups", "*.bak*", "__pycache__", ".history"))
    for desc, rel, find, rep, _, _ in FAULTS:
        p = os.path.join(tmp, rel)
        if find is None:
            inject_pad_net(p, "U4", "5", "GND")
        else:
            s = open(p, encoding="utf-8").read()
            assert find in s, f"selftest setup: '{find}' not found in {rel}"
            open(p, "w", encoding="utf-8").write(s.replace(find, rep))
    fc = os.path.join(tmp, "Microcontroller-PCB", "datasheets", "flagcheck", "flagcheck.py")
    subprocess.run([sys.executable, fc, "--capstone", tmp, "--no-tools"], capture_output=True)
    flags = json.load(open(os.path.join(os.path.dirname(fc), "FLAGS.json")))["flags"]
    ok = True
    for desc, _, _, _, rule, where in FAULTS:
        hit = any(f["rule"].startswith(rule) and where in f["where"] for f in flags)
        print(("PASS" if hit else "FAIL") + f"  {desc}  -> expects {rule} at {where}")
        ok &= hit
    shutil.rmtree(tmp, ignore_errors=True)
    print("selftest", "passed" if ok else "FAILED")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
