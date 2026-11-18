#include "backlight.h"
#include "../config/pins.h"
#include "../config/config.h"
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/clocks.h"

#define BL_WRAP 9999u   /* 10000 counts per period: duty in 0.01 % steps */

void backlight_init(void)
{
    uint slice = pwm_gpio_to_slice_num(PIN_LCD_BL_PWM);
    /* f_pwm = f_sys / (div * (wrap + 1)); at 150 MHz, div = 15 gives 1 kHz */
    float div = (float)clock_get_hz(clk_sys) / ((float)BL_PWM_HZ * (float)(BL_WRAP + 1u));
    pwm_set_clkdiv(slice, div);
    pwm_set_wrap(slice, BL_WRAP);
    pwm_set_gpio_level(PIN_LCD_BL_PWM, 0);
    gpio_set_function(PIN_LCD_BL_PWM, GPIO_FUNC_PWM);
    pwm_set_enabled(slice, true);
}

unsigned backlight_set_pct(unsigned pct)
{
    if (pct > BL_MAX_DUTY_PCT) pct = BL_MAX_DUTY_PCT;   /* ISSUES #7 */
    pwm_set_gpio_level(PIN_LCD_BL_PWM, (uint16_t)(pct * (BL_WRAP + 1u) / 100u));
    return pct;
}
