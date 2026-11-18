/* demo_frames - plays 128x64 frames streamed over USB serial from the Mac
 * (tools/stream_frames.py). Not part of the bring-up order: a display demo.
 *
 * Protocol, one frame: the 3 bytes "FRM", then 1024 bytes in the ST7565R
 * page layout (8 pages x 128 columns, bit 0 = top pixel of the page).
 * USB flow control paces the Mac, so nothing here needs a buffer. */
#include "hw_common.h"
#include "config/config.h"
#include "drivers/st7565.h"
#include "ui/gfx.h"
#include "ui/backlight.h"

static int get_byte(void)
{
    int c;
    while ((c = getchar_timeout_us(1000000)) == PICO_ERROR_TIMEOUT) { }
    return c;
}

int main(void)
{
    hw_start("demo_frames");
    backlight_init();
    backlight_set_pct(50);
    st7565_init();
    gfx_clear();
    gfx_text(16, 3, "waiting for frames");
    st7565_flush(gfx_fb);
    printf("ready\n");

    unsigned frames = 0;
    uint32_t t_reinit = to_ms_since_boot(get_absolute_time());
    for (;;) {
        /* find the sync bytes, so a dropped byte only costs one frame */
        if (get_byte() != 'F') continue;
        if (get_byte() != 'R') continue;
        if (get_byte() != 'M') continue;

        uint8_t *p = &gfx_fb[0][0];
        for (unsigned i = 0; i < sizeof gfx_fb; i++) p[i] = (uint8_t)get_byte();
        st7565_flush(gfx_fb);
        frames++;

        /* RF-recovery re-init every 5 s, same as the real firmware will do */
        uint32_t now = to_ms_since_boot(get_absolute_time());
        if (now - t_reinit >= 5000) { st7565_reinit(); t_reinit = now; }
        if (frames % 300 == 0) printf("frames %u\n", frames);
    }
}
