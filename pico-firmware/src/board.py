# board.py -- pin hygiene + backlight. ISSUES #7 and #16.
from machine import Pin, PWM

import config as C


def init_unused_pins():
    """ISSUES #16: unused GPIOs get pull-ups so they never sit mid-rail, where RP2350 erratum E9
    makes an enabled input leak ~120 uA (DS Appendix D.5.1, p.1359). Pull-ups are unaffected by E9."""
    for p in C.PINS_UNUSED_PULLUP:
        Pin(p, Pin.IN, Pin.PULL_UP)


class Backlight:
    """ISSUES #7: AO3400A gate on GP14 (R2 100k pull-down). Duty is capped at BL_MAX_DUTY so the
    LED (100 mA max, NHD DS p.7) and R1 (1206, 0.25 W, Yageo RC_L p.6) stay in spec even with a
    high 5 V supply."""
    def __init__(self):
        self._pwm = PWM(Pin(C.PIN_LCD_BL))
        self._pwm.freq(C.BL_PWM_HZ)
        self.set(C.BL_DEFAULT_DUTY)

    def set(self, duty):
        duty = max(0.0, min(C.BL_MAX_DUTY, duty))
        self.duty = duty
        self._pwm.duty_u16(int(duty * 65535))
        return duty

    def off(self):
        self._pwm.duty_u16(0)
