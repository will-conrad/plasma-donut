/* Step 2 - buttons. Shows each press on the LCD and over USB serial.
 * Checks: a quick tap gives one "short", holding past 0.8 s gives one "long",
 * and the raw level reads 1 when released, 0 when pressed (active low,
 * R16/R17 10k external pull-ups). One tap must never count twice. */
#include "hw_common.h"
#include "config/pins.h"
#include "config/config.h"
#include "drivers/st7565.h"
#include "ui/gfx.h"
#include "ui/backlight.h"
#include "ui/buttons.h"

static const uint pin[2] = { PIN_BTN_1, PIN_BTN_2 };
static btn_t btn[2];
static unsigned n_short[2], n_long[2];
static char last[22] = "press a button";

static void draw(void)
{
    char line[24];
    gfx_clear();
    gfx_text(0, 0, "Step 2: buttons");
    gfx_invert_line(0);
    for (int i = 0; i < 2; i++) {
        snprintf(line, sizeof line, "BTN%d raw %d %s", i + 1, gpio_get(pin[i]),
                 btn[i].stable ? "DOWN" : "up");
        gfx_text(0, 2 + 3 * i, line);
        snprintf(line, sizeof line, "  short %3u long %3u", n_short[i], n_long[i]);
        gfx_text(0, 3 + 3 * i, line);
    }
    gfx_text(0, 7, last);
    st7565_flush(gfx_fb);
}

int main(void)
{
    hw_start("Step 2: buttons");
    for (int i = 0; i < 2; i++) {
        gpio_init(pin[i]);
        gpio_set_dir(pin[i], GPIO_IN);
        gpio_pull_up(pin[i]);       /* external 10k already; internal pull-up is harmless and avoids E9 pull-down issues */
        btn_init(&btn[i]);
    }
    backlight_init();
    backlight_set_pct(50);
    st7565_init();
    draw();

    uint32_t next_draw = 0;
    for (;;) {
        uint32_t now = to_ms_since_boot(get_absolute_time());
        for (int i = 0; i < 2; i++) {
            bool pressed = !gpio_get(pin[i]);          /* active low */
            btn_event_t e = btn_update(&btn[i], pressed, now);
            if (e == BTN_EV_NONE) continue;
            if (e == BTN_EV_SHORT) n_short[i]++; else n_long[i]++;
            snprintf(last, sizeof last, "BTN%d %s @%lu.%02lus", i + 1, btn_event_str(e),
                     (unsigned long)(now / 1000), (unsigned long)(now % 1000 / 10));
            printf("%8lu ms  BTN%d %-5s  (short %u, long %u)\n", (unsigned long)now, i + 1,
                   btn_event_str(e), n_short[i], n_long[i]);
            next_draw = 0;
        }
        if (now >= next_draw) { draw(); next_draw = now + 200; }   /* 5 Hz, raw level stays live */
        sleep_ms(BTN_POLL_MS);
    }
}
