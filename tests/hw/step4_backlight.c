/* Step 4 - backlight dimmer on the two buttons.
 *   up button tap:   5 % brighter   hold: ramps up until released
 *   down button tap: 5 % dimmer     hold: ramps down until released
 * Which button is up is BTN_IDX_UP in config.h (BTN1 on Rev A).
 * Range 0 to BL_MAX_DUTY_PCT (75 %, ISSUES #7); the driver enforces the cap.
 * PWM is 1 kHz on GP14 (Q1 gate), so no flicker should be visible. */
#include "hw_common.h"
#include "config/pins.h"
#include "config/config.h"
#include "drivers/st7565.h"
#include "ui/gfx.h"
#include "ui/backlight.h"
#include "ui/buttons.h"

#define STEP_PCT     5
#define RAMP_MS      40     /* while held: 1 % every 40 ms, so 0 to 75 % in 3 s */

static const uint pin[2] = { PIN_BTN_1, PIN_BTN_2 };

static void draw(unsigned pct)
{
    char line[24];
    gfx_clear();
    gfx_text(0, 0, "Step 4: backlight");
    gfx_invert_line(0);
    snprintf(line, sizeof line, "%3u %%  (max %u %%)", pct, BL_MAX_DUTY_PCT);
    gfx_text(16, 2, line);

    /* bar: the outline spans 0 to 75 %, the fill is the current level */
    const int x0 = 4, x1 = GFX_W - 5, y0 = 30, y1 = 41;
    gfx_rect(x0, y0, x1, y1);
    int fill = x0 + 2 + (int)((x1 - x0 - 4) * pct / BL_MAX_DUTY_PCT);
    for (int x = x0 + 2; x < fill; x++) gfx_vline(x, y0 + 2, y1 - 2);

    gfx_text(0, 6, BTN_IDX_UP == 0 ? "BTN1 up  BTN2 down" : "BTN2 up  BTN1 down");
    gfx_text(0, 7, "tap = 5%  hold = ramp");
    st7565_flush(gfx_fb);
}

int main(void)
{
    hw_start("Step 4: backlight dimmer");
    btn_t btn[2];
    for (int i = 0; i < 2; i++) {
        gpio_init(pin[i]);
        gpio_set_dir(pin[i], GPIO_IN);
        gpio_pull_up(pin[i]);
        btn_init(&btn[i]);
    }
    backlight_init();
    unsigned pct = backlight_set_pct(50);
    st7565_init();
    draw(pct);

    uint32_t next_ramp = 0;
    for (;;) {
        uint32_t now = to_ms_since_boot(get_absolute_time());
        int delta = 0;

        for (int i = 0; i < 2; i++) {
            int dir = (i == BTN_IDX_UP) ? +1 : -1;
            btn_event_t e = btn_update(&btn[i], !gpio_get(pin[i]), now);
            if (e == BTN_EV_SHORT) delta += dir * STEP_PCT;
            /* held past the long-press time: keep ramping until release */
            if (btn[i].stable && btn[i].long_fired && now >= next_ramp) {
                delta += dir;
                next_ramp = now + RAMP_MS;
            }
        }

        if (delta != 0) {
            int want = (int)pct + delta;
            if (want < 0) want = 0;
            unsigned got = backlight_set_pct((unsigned)want);   /* clamps to 75 % */
            if (got != pct) {
                pct = got;
                draw(pct);
                printf("backlight %u %%\n", pct);
            }
        }
        sleep_ms(BTN_POLL_MS);
    }
}
