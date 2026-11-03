# freq.py -- frequency measurement. ISSUES #5 and #6.
#
# Oscillator tap (/FREQ_QUARTZ, GPIO22): GPIO22 is an even pin, so the PWM edge counter can't
# use it (RP2350 DS p.980). But GPIO22's function 9 is clocks_gpin_1 (DS GPIO22_CTRL, FUNCSEL),
# and the clocks block's frequency counter FC0 can measure clksrc_gpin1 (FC0_SRC = 7, DS Table 616).
# Register offsets from the RP2350 datasheet, CLOCKS block (base 0x40010000, DS p.499 list):
#   FC0_REF_KHZ 0x08c, FC0_MIN_KHZ 0x090, FC0_MAX_KHZ 0x094, FC0_DELAY 0x098,
#   FC0_INTERVAL 0x09c, FC0_SRC 0x0a0, FC0_STATUS 0x0a4, FC0_RESULT 0x0a8 (KHZ in bits 29:5).
# Accuracy vs interval: Table 574 (p.476): interval 15 (32 ms) -> 62.5 Hz.
#
# Fallback / coil A-B counters: a PIO edge counter (3 instructions per edge at 150 MHz =
# 20 ns << 73.7 ns period at 13.56 MHz).
import time
import machine
from machine import Pin, mem32
import rp2

import config as C

CLOCKS_BASE = 0x40010000
FC0_REF_KHZ = CLOCKS_BASE + 0x08C
FC0_MIN_KHZ = CLOCKS_BASE + 0x090
FC0_MAX_KHZ = CLOCKS_BASE + 0x094
FC0_DELAY = CLOCKS_BASE + 0x098
FC0_INTERVAL = CLOCKS_BASE + 0x09C
FC0_SRC = CLOCKS_BASE + 0x0A0
FC0_STATUS = CLOCKS_BASE + 0x0A4
FC0_RESULT = CLOCKS_BASE + 0x0A8
ST_RUNNING = 1 << 8
ST_DONE = 1 << 4
ST_DIED = 1 << 28
SRC_GPIN1 = 7
SRC_CLK_SYS = 9

IO_BANK0_BASE = 0x40028000
GPIO22_CTRL = IO_BANK0_BASE + 0x0B4
FUNCSEL_GPIN1 = 9


def _fc0_khz(src, interval=C.FC0_INTERVAL, timeout_ms=200):
    t0 = time.ticks_ms()
    while mem32[FC0_STATUS] & ST_RUNNING:
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            return None
    mem32[FC0_REF_KHZ] = C.CLK_REF_KHZ
    mem32[FC0_INTERVAL] = interval
    mem32[FC0_MIN_KHZ] = 0
    mem32[FC0_MAX_KHZ] = 0x1FFFFFF
    mem32[FC0_SRC] = src                      # writing SRC starts the count
    while not (mem32[FC0_STATUS] & ST_DONE):
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            mem32[FC0_SRC] = 0
            return None
    st = mem32[FC0_STATUS]
    res = mem32[FC0_RESULT]
    mem32[FC0_SRC] = 0
    if st & ST_DIED:
        return None                           # no clock on the pin (oscillator off)
    return ((res >> 5) & 0x1FFFFFF) + (res & 0x1F) / 32


def self_test():
    """Sanity check that CLK_REF_KHZ is right: FC0 on clk_sys should equal machine.freq()."""
    khz = _fc0_khz(SRC_CLK_SYS, interval=10)
    expect = machine.freq() / 1000
    ok = khz is not None and abs(khz - expect) < 0.01 * expect
    return ok, khz, expect


class OscFC0:
    """f_osc on GPIO22 via GPIN1 + FC0. No hardware change needed."""
    def __init__(self):
        Pin(C.PIN_FREQ_OSC, Pin.IN)           # clears pad isolation, enables the input buffer
        v = mem32[GPIO22_CTRL]
        mem32[GPIO22_CTRL] = (v & ~0x1F) | FUNCSEL_GPIN1

    def read_hz(self):
        khz = _fc0_khz(SRC_GPIN1)
        return None if khz is None else khz * 1000


@rp2.asm_pio()
def _edge_counter():
    label("loop")
    wait(0, pin, 0)
    wait(1, pin, 0)
    jmp(x_dec, "loop")


class PioCounter:
    """Counts rising edges on `pin` over PIO_GATE_MS. Used for GPIO22 if FREQ_METHOD == 'pio',
    and for SQ_A/SQ_B on GP5/GP7 after the docs/REWORK.md R5a bodge."""
    def __init__(self, sm_id, pin):
        self.sm = rp2.StateMachine(sm_id, _edge_counter, freq=machine.freq(), in_base=Pin(pin, Pin.IN))

    def read_hz(self, gate_ms=C.PIO_GATE_MS):
        sm = self.sm
        sm.active(0)
        sm.restart()
        sm.put(0xFFFFFFFF)
        sm.exec("pull()")
        sm.exec("mov(x, osr)")
        t0 = time.ticks_us()
        sm.active(1)
        time.sleep_ms(gate_ms)
        sm.active(0)
        dt = time.ticks_diff(time.ticks_us(), t0)
        sm.exec("mov(isr, x)")
        sm.exec("push()")
        edges = (0xFFFFFFFF - sm.get()) & 0xFFFFFFFF
        return edges * 1_000_000 / dt if dt > 0 else None


def make_osc_counter():
    if C.FREQ_METHOD == "fc0":
        return OscFC0()
    return PioCounter(0, C.PIN_FREQ_OSC)


def make_coil_counters():
    """Returns (counter_A, counter_B) or (None, None) if the SQ bodge isn't fitted."""
    if not C.BODGE_SQ_TO_GP5_GP7:
        return None, None
    return PioCounter(1, C.PIN_SQ_A), PioCounter(2, C.PIN_SQ_B)
