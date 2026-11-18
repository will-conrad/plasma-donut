/* backlight.h - LCD backlight PWM on the AO3400A gate (GP14). */
#ifndef BACKLIGHT_H
#define BACKLIGHT_H

void     backlight_init(void);            /* starts at 0 % (off) */
unsigned backlight_set_pct(unsigned pct); /* clamps to BL_MAX_DUTY_PCT, returns the value used */

#endif
