# picoadc.py -- burst sampling of the RP2350's own ADC (GPIO26/27/28). ISSUES #8.
# Why: the RP2350 ADC input impedance is only >= 100 k (DS Table 1685, p.1339). Sampling
# continuously from the 9.1 k VDD dividers would read up to 8.3 % low. A short burst draws its
# charge from C22/C23/C38 (0.1 uF) instead; they recover with tau ~ 0.9 ms, so bursts are
# spaced >= PICO_ADC_MIN_GAP_MS apart per channel.
import time
from machine import ADC, Pin

import config as C

_CH_PIN = {C.ADC_CH_VDD_A: C.PIN_VDD_TAP_A, C.ADC_CH_VDD_B: C.PIN_VDD_TAP_B,
           C.ADC_CH_PASSIVE: C.PIN_PASSIVE_LEVEL}


class PicoADC:
    def __init__(self):
        self._adc = {ch: ADC(pin) for ch, pin in _CH_PIN.items()}
        self._last = {ch: time.ticks_add(time.ticks_ms(), -1000) for ch in _CH_PIN}
        self._cache = {ch: None for ch in _CH_PIN}
        # pico2 p.15: driving GPIO23 (SMPS PS) high forces PWM mode and "can greatly reduce the inherent
        # ripple of the SMPS at light load, and therefore the ripple on the ADC supply".
        self._ps = Pin(C.PIN_SMPS_PS, Pin.OUT, value=0) if C.SMPS_PWM_DURING_ADC else None

    def read12(self, ch):
        """Average of a short burst, as a 12-bit code. Returns the cached value if the channel
        was read less than PICO_ADC_MIN_GAP_MS ago (lets the hold cap recharge)."""
        now = time.ticks_ms()
        if self._cache[ch] is not None and time.ticks_diff(now, self._last[ch]) < C.PICO_ADC_MIN_GAP_MS:
            return self._cache[ch]
        a = self._adc[ch]
        total = 0
        if self._ps:
            self._ps(1)
            time.sleep_us(50)                  # let the SMPS settle in PWM mode [assumed settle time]
        for _ in range(C.PICO_ADC_BURST):
            total += a.read_u16() >> 4
        if self._ps:
            self._ps(0)                        # back to low-power PFM
        val = total // C.PICO_ADC_BURST
        self._last[ch] = now
        self._cache[ch] = val
        return val
