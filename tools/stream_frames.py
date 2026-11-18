#!/usr/bin/env python3
"""Stream a folder of images to the LCD through tests/hw/demo_frames.

    python3 tools/stream_frames.py FOLDER [--fps 30] [--invert] [--threshold 128]

Images are sorted by name, scaled to fit 128x64 keeping their aspect ratio,
centred, and thresholded to 1 bit. A dark source pixel turns the LCD pixel on.
Frames are converted in memory first, then sent on a fixed clock; if the link
falls behind, frames are skipped to keep time. Needs Pillow."""
import argparse, glob, os, select, sys, termios, time
from PIL import Image

W, H = 128, 64

def to_pages(img, threshold, invert):
    g = img.convert("L")
    scale = min(W / g.width, H / g.height)
    w, h = max(1, round(g.width * scale)), max(1, round(g.height * scale))
    g = g.resize((w, h), Image.LANCZOS)
    canvas = Image.new("L", (W, H), 0)            # bars: dark (pixel on)
    canvas.paste(g, ((W - w) // 2, (H - h) // 2))
    px = canvas.load()
    out = bytearray(1024)
    for page in range(8):
        for x in range(W):
            b = 0
            for bit in range(8):
                on = px[x, page * 8 + bit] < threshold
                if invert: on = not on
                if on: b |= 1 << bit
            out[page * W + x] = b
    return bytes(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--threshold", type=int, default=128)
    ap.add_argument("--invert", action="store_true")
    ap.add_argument("--port", default=None)
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.folder)
                   if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")))
    if not files: sys.exit("no images in " + a.folder)
    print(f"converting {len(files)} frames...", flush=True)
    frames = [to_pages(Image.open(os.path.join(a.folder, f)), a.threshold, a.invert)
              for f in files]

    port = a.port or sorted(glob.glob("/dev/cu.usbmodem*"))[0]
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
    t = termios.tcgetattr(fd)
    t[0] = t[1] = t[3] = 0                         # raw: no translation, no echo
    t[2] |= termios.CS8 | termios.CREAD | termios.CLOCAL
    termios.tcsetattr(fd, termios.TCSANOW, t)

    period = 1.0 / a.fps
    start, sent, skipped = time.monotonic(), 0, 0
    i = 0
    while i < len(frames):
        os.write(fd, b"FRM" + frames[i]); sent += 1
        # drain anything the Pico printed, so its buffer never fills
        while select.select([fd], [], [], 0)[0]:
            os.read(fd, 4096)
        due = start + (i + 1) * period
        now = time.monotonic()
        if now < due:
            time.sleep(due - now); i += 1
        else:
            nxt = int((now - start) / period)      # behind: jump to the frame for now
            skipped += max(0, nxt - i - 1); i = max(i + 1, nxt)
    dt = time.monotonic() - start
    print(f"done: {sent} sent, {skipped} skipped, {dt:.1f} s ({sent / dt:.1f} fps shown)")

if __name__ == "__main__":
    main()
