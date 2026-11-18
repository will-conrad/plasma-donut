/* adc_live - every ADC reading on the LCD, refreshed at 5 Hz.
 * Either button switches page:
 *   page 1, values: temperatures, VDD A/B, phase and spare volts, passive, VSYS
 *   page 2, raw:    MCP3208 CH0-7 and Pico ADC0-3 mean codes, worst burst spread
 * Also prints one line over USB serial twice a second. */
#include "hw_common.h"
#include "config/pins.h"
#include "config/config.h"
#include "drivers/mcp3208.h"
#include "drivers/picoadc.h"
#include "drivers/st7565.h"
#include "sensors/convert.h"
#include "ui/gfx.h"
#include "ui/backlight.h"
#include "ui/buttons.h"

static adc_burst_t mcp[8], pico[4];

static void sample(void)
{
    for (uint8_t ch = 0; ch < 8; ch++) {
        if (MCP_CH_ENABLED_MASK & (1u << ch)) mcp[ch] = mcp3208_read_burst(ch, ADC_OVERSAMPLE);
        else mcp[ch] = (adc_burst_t){ 0.0f, 0, 0 };     /* CH4/5 not driven: never read */
    }
    for (unsigned in = 0; in < 4; in++) pico[in] = picoadc_read_burst(in, ADC_OVERSAMPLE);
}

static void fmt_temp(char *buf, size_t n, const char *name, float code)
{
    reading_t t = ntc_temp_c(code);
    if (t.status == RD_OK) snprintf(buf, n, "%-7s %7.2f C%s", name, (double)t.value,
                                    t.value >= TEMP_WARN_C ? " !" : "");
    else                   snprintf(buf, n, "%-7s %7s", name, rd_status_str(t.status));
}

static void draw_values(void)
{
    static const char *const name[4] = { "MOS A", "MOS B", "Coil A", "Coil B" };
    char line[32];
    gfx_text(0, 0, "ADC live  values  1/2");
    gfx_invert_line(0);
    for (int i = 0; i < 4; i++) {
        fmt_temp(line, sizeof line, name[i], mcp[i].mean);
        gfx_text(0, 1 + i, line);
    }
    reading_t va = vdd_volts(pico[PICOADC_IN_VDD_A].mean, VDD_GAIN_DEFAULT);
    reading_t vb = vdd_volts(pico[PICOADC_IN_VDD_B].mean, VDD_GAIN_DEFAULT);
    snprintf(line, sizeof line, "VDD A%5.2f%s B%5.2f%s", (double)va.value,
             va.status == RD_OK ? "" : "!", (double)vb.value, vb.status == RD_OK ? "" : "!");
    gfx_text(0, 5, line);
    snprintf(line, sizeof line, "Ph %5.3fV Spr %5.3fV",
             (double)adc_code_to_volts(mcp[MCP_CH_PHASE].mean, VREF_NOMINAL_V),
             (double)adc_code_to_volts(mcp[MCP_CH_SPARE].mean, VREF_NOMINAL_V));
    gfx_text(0, 6, line);
    snprintf(line, sizeof line, "Pas %5.3fV VSYS %4.2f",
             (double)adc_code_to_volts(pico[PICOADC_IN_PASSIVE].mean, VREF_NOMINAL_V),
             (double)vsys_volts(pico[PICOADC_IN_VSYS].mean));
    gfx_text(0, 7, line);
}

static void draw_raw(void)
{
    char line[32];
    unsigned worst = 0;
    gfx_text(0, 0, "ADC live  raw     2/2");
    gfx_invert_line(0);
    for (int r = 0; r < 4; r++) {
        int a = 2 * r, b = a + 1;
        char sa[10], sb[10];
        if (MCP_CH_ENABLED_MASK & (1u << a)) snprintf(sa, sizeof sa, "%6.1f", (double)mcp[a].mean); else snprintf(sa, sizeof sa, "   off");
        if (MCP_CH_ENABLED_MASK & (1u << b)) snprintf(sb, sizeof sb, "%6.1f", (double)mcp[b].mean); else snprintf(sb, sizeof sb, "   off");
        snprintf(line, sizeof line, "%d %s  %d %s", a, sa, b, sb);
        gfx_text(0, 1 + r, line);
    }
    for (int ch = 0; ch < 8; ch++)
        if ((MCP_CH_ENABLED_MASK & (1u << ch)) && (unsigned)(mcp[ch].max - mcp[ch].min) > worst) worst = (unsigned)(mcp[ch].max - mcp[ch].min);
    snprintf(line, sizeof line, "A0%6.1f  A1%6.1f", (double)pico[0].mean, (double)pico[1].mean);
    gfx_text(0, 5, line);
    snprintf(line, sizeof line, "A2%6.1f  A3%6.1f", (double)pico[2].mean, (double)pico[3].mean);
    gfx_text(0, 6, line);
    snprintf(line, sizeof line, "MCP spread %3u LSB", worst);
    gfx_text(0, 7, line);
}

int main(void)
{
    hw_start("adc_live");
    const uint pin[2] = { PIN_BTN_1, PIN_BTN_2 };
    btn_t btn[2];
    for (int i = 0; i < 2; i++) {
        gpio_init(pin[i]);
        gpio_set_dir(pin[i], GPIO_IN);
        gpio_pull_up(pin[i]);
        btn_init(&btn[i]);
    }
    mcp3208_init();
    picoadc_init();
    backlight_init();
    backlight_set_pct(50);
    st7565_init();
    sample();                         /* first sweep after boot reads low: discard */

    int page = 0;
    uint32_t next_draw = 0, next_log = 0, next_reinit = 5000;
    for (;;) {
        uint32_t now = to_ms_since_boot(get_absolute_time());
        bool redraw = false;
        for (int i = 0; i < 2; i++)
            if (btn_update(&btn[i], !gpio_get(pin[i]), now) == BTN_EV_SHORT) { page ^= 1; redraw = true; }

        if (now >= next_draw || redraw) {
            sample();
            gfx_clear();
            if (page == 0) draw_values(); else draw_raw();
            st7565_flush(gfx_fb);
            next_draw = now + 200;
        }
        if (now >= next_reinit) { st7565_reinit(); next_reinit = now + 5000; }   /* RF recovery */
        if (now >= next_log) {
            printf("%lu ms  mcp", (unsigned long)now);
            for (int ch = 0; ch < 8; ch++) printf(" %.1f", (double)mcp[ch].mean);
            printf("  pico %.1f %.1f %.1f %.1f\n", (double)pico[0].mean, (double)pico[1].mean,
                   (double)pico[2].mean, (double)pico[3].mean);
            next_log = now + 500;
        }
        sleep_ms(BTN_POLL_MS);
    }
}
