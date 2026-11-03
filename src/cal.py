# cal.py -- calibration store (cal.json on the Pico filesystem). ISSUES #8 and #11.
import json

import config as C

CAL_FILE = "cal.json"


def load():
    cal = dict(C.CAL_DEFAULTS)
    try:
        with open(CAL_FILE) as f:
            cal.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cal


def save(cal):
    with open(CAL_FILE, "w") as f:
        json.dump(cal, f)


def gain_from_reference(measured, reference, old_gain=1.0):
    """One-point gain cal: put a known voltage on the input, read it with a multimeter (reference)
    and with the firmware (measured, computed with old_gain). Returns the new gain."""
    if not measured:
        raise ValueError("measured reading is zero")
    return old_gain * reference / measured


def phase_zero(samples_deg):
    """Zero-phase cal (same signal into J16 and J17, at the real operating amplitude):
    phi0 = mean of the raw readings."""
    return sum(samples_deg) / len(samples_deg)
