#!/usr/bin/env python3
"""Calibrate the four thermistors against a thermal camera.

The board must be running tests/hw/adc_live (it prints the raw MCP3208 codes).

    python3 tools/cal_thermistors.py [--seconds 10] [--port /dev/cu.usbmodemXXXX]

1. Let the sensors settle at a steady temperature (the NTC time constant is < 4 s).
2. The script averages each sensor for --seconds, then asks for the camera
   reading of each one. Press Enter to skip a sensor.
3. Optionally repeat at a second, clearly different temperature.
   One point fixes an offset; two points fix offset and gain:
       T_true = gain * T_board + offset
4. Paste the printed lines into src/config/config.h.

Aim the camera at a bit of matte tape on the sensor (emissivity about 0.95): bare
copper or solder reads far too cold."""
import argparse, glob, math, os, select, statistics, sys, termios, time

NAMES = ["MOS A", "MOS B", "Coil A", "Coil B"]
# Same constants and model as src/config/config.h and src/sensors/convert.c
R0, T0, BETA, RFIX, FS = 10000.0, 298.15, 3435.0, 10000.0, 4096.0
OPEN, SHORT = 4070.0, 5.0
SERIES = [10000.0, 0.0, 0.0, 0.0]   # keep equal to TEMP_SERIES_OHM in config.h

def code_to_c(n, sensor=None):
    if n >= OPEN or n <= SHORT: return None
    r = RFIX * n / (FS - n) - (SERIES[sensor] if sensor is not None else 0.0)
    if r <= 1.0: return None
    return 1.0 / (1.0 / T0 + math.log(r / R0) / BETA) - 273.15

def open_port(path):
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    t = termios.tcgetattr(fd)
    t[3] &= ~(termios.ICANON | termios.ECHO)
    termios.tcsetattr(fd, termios.TCSANOW, t)
    return fd

def measure(fd, seconds):
    """Average board temperatures from the adc_live log for `seconds`."""
    temps, buf, end = [[] for _ in NAMES], b"", time.time() + seconds
    while time.time() < end:
        if select.select([fd], [], [], 0.2)[0]:
            try: buf += os.read(fd, 4096)
            except BlockingIOError: pass
        *lines, buf = buf.split(b"\n")
        for ln in lines:
            parts = ln.decode(errors="replace").split()
            if "mcp" not in parts: continue
            i = parts.index("mcp")
            for k in range(4):
                c = code_to_c(float(parts[i + 1 + k]), k)
                if c is not None: temps[k].append(c)
    if not any(temps):
        sys.exit("no readings: is the board running adc_live?")
    out = []
    for k, ts in enumerate(temps):
        if len(ts) < 3:
            print(f"  {NAMES[k]:7s} OPEN/SHORT or no data, skipped"); out.append(None); continue
        drift = ts[-1] - ts[0]
        flag = "  (still drifting: wait and redo)" if abs(drift) > 0.3 else ""
        print(f"  {NAMES[k]:7s} {statistics.mean(ts):7.2f} C  (+-{statistics.pstdev(ts):.2f}, drift {drift:+.2f}){flag}")
        out.append(statistics.mean(ts))
    return out

def ask_camera(board):
    cam = []
    for k, b in enumerate(board):
        if b is None: cam.append(None); continue
        s = input(f"  camera reading for {NAMES[k]} (C, Enter to skip): ").strip()
        cam.append(float(s) if s else None)
    return cam

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--port", default=None)
    a = ap.parse_args()
    ports = sorted(glob.glob("/dev/cu.usbmodem*"))
    if not a.port and not ports: sys.exit("no Pico serial port found")
    fd = open_port(a.port or ports[0])

    points = []
    for p in (1, 2):
        if p == 2 and input("\nAdd a second point at a different temperature? [y/N] ").strip().lower() != "y":
            break
        input(f"\nPoint {p}: let the sensors settle, then press Enter to measure for {a.seconds:.0f} s...")
        board = measure(fd, a.seconds)
        points.append((board, ask_camera(board)))

    offset, gain = [0.0] * 4, [1.0] * 4
    print("\nResult (T_true = gain * T_board + offset):")
    for k in range(4):
        pts = [(b[k], c[k]) for b, c in points if b[k] is not None and c[k] is not None]
        if len(pts) >= 2 and abs(pts[1][0] - pts[0][0]) >= 5.0:
            (b1, c1), (b2, c2) = pts[:2]
            gain[k] = (c2 - c1) / (b2 - b1)
            offset[k] = c1 - gain[k] * b1
        elif pts:
            if len(pts) >= 2: print(f"  {NAMES[k]}: points under 5 C apart, using offset only")
            offset[k] = pts[0][1] - pts[0][0]
        else:
            print(f"  {NAMES[k]}: no camera reading, left uncalibrated")
        print(f"  {NAMES[k]:7s} gain {gain[k]:.4f}  offset {offset[k]:+.2f} C")

    big = [NAMES[k] for k in range(4) if abs(offset[k]) > 3 or abs(gain[k] - 1) > 0.1]
    if big:
        print(f"\nCheck {', '.join(big)}: a correction this large usually means the camera "
              "was reading something else (emissivity, spot size), not a bad sensor.")
    print("\nPaste into src/config/config.h:")
    print("#define TEMP_CAL_GAIN    { " + ", ".join(f"{g:.4f}f" for g in gain) + " }")
    print("#define TEMP_CAL_OFFSET  { " + ", ".join(f"{o:+.2f}f" for o in offset) + " }")

if __name__ == "__main__":
    main()
