/* Step 3 - LCD: init, "Hello Donut", contrast tuning. Backlight at 50 %.
 * Keys over USB serial:
 *   + / -   contrast up / down (electronic volume 0-63)
 *   b / d   backlight brighter / dimmer (5 % steps, capped at 75 %)
 *   p       next pattern: text, checkerboard, all pixels on
 *   r       resend the init sequence (the RF-recovery path)
 *   o       next orientation (0 normal, 1 mirror L-R, 2 flip T-B, 3 rotate 180) */
#include "hw_common.h"
#include "config/config.h"
#include "drivers/st7565.h"
#include "ui/gfx.h"
#include "ui/backlight.h"

static void draw(int pattern)
{
    char line[24];
    st7565_all_points(pattern == 2);
    if (pattern == 1) {
        for (int p = 0; p < GFX_PAGES; p++)
            for (int x = 0; x < GFX_W; x++)
                gfx_fb[p][x] = ((x >> 3) + p) & 1 ? 0xFF : 0x00;   /* 8x8 squares */
    } else {
        gfx_clear();
        gfx_rect(0, 0, GFX_W - 1, GFX_H_PX - 1);   /* shows all four edges */
        gfx_text(2, 0, "TL");                      /* corner tags: TL must be top left */
        gfx_text(GFX_W - 14, 7, "BR");
        gfx_text(31, 1, "Hello Donut");
        gfx_text(4, 3, "ABCDEFGHIJKLMNOPQRST");
        gfx_text(4, 4, "abcdefghijklmnopqrst");
        gfx_text(4, 5, "0123456789 +-.:/%?<>");
        snprintf(line, sizeof line, "contrast %2u orient %u", st7565_get_contrast(), st7565_get_orientation());
        gfx_text(4, 6, line);
    }
    st7565_flush(gfx_fb);
}

int main(void)
{
    hw_start("Step 3: LCD");
    backlight_init();
    unsigned bl = backlight_set_pct(50);
    st7565_init();
    int pattern = 0;
    draw(pattern);
    printf("keys: +/- contrast, b/d backlight, p pattern, r re-init, o orientation\n");

    for (;;) {
        int c = getchar_timeout_us(100 * 1000);
        if (c == PICO_ERROR_TIMEOUT) continue;
        uint8_t v = st7565_get_contrast();
        switch (c) {
        case '+': case '=': if (v < 63) st7565_set_contrast(v + 1); break;
        case '-': case '_': if (v > 0)  st7565_set_contrast(v - 1); break;
        case 'b': bl = backlight_set_pct(bl + 5); break;
        case 'd': bl = backlight_set_pct(bl >= 5 ? bl - 5 : 0); break;
        case 'p': pattern = (pattern + 1) % 3; break;
        case 'r': st7565_reinit(); break;
        case 'o': st7565_set_orientation((st7565_get_orientation() + 1u) % 4u); break;
        default:  continue;
        }
        draw(pattern);
        printf("contrast=%u (0x%02X)  backlight=%u %%  pattern=%d  orientation=%u\n",
               st7565_get_contrast(), st7565_get_contrast(), bl, pattern, st7565_get_orientation());
    }
}
