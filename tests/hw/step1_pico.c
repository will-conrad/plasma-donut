/* Step 1 - is the Pico 2 alive?
 * Blinks the onboard LED at 2 Hz and prints once a second:
 *   clk_sys (expect 150000 kHz), VSYS (expect about 4.6-5.0 V on USB),
 *   chip temperature (expect a little above room temperature).
 * Uses nothing on the control board, so it also runs on a bare Pico 2. */
#include "hw_common.h"
#include "hardware/clocks.h"
#include "config/pins.h"
#include "config/config.h"
#include "drivers/picoadc.h"
#include "sensors/convert.h"

int main(void)
{
    hw_start("Step 1: Pico 2 alive");
    gpio_init(PIN_LED);
    gpio_set_dir(PIN_LED, GPIO_OUT);
    picoadc_init();

    for (unsigned tick = 0;; tick++) {
        gpio_put(PIN_LED, tick & 1);
        if (tick % 4 == 0) {
            adc_burst_t vs = picoadc_read_burst(PICOADC_IN_VSYS, ADC_OVERSAMPLE);
            adc_burst_t ct = picoadc_read_burst(PICOADC_IN_CHIPTEMP, ADC_OVERSAMPLE);
            printf("t=%lu s  clk_sys=%lu kHz  VSYS=%.2f V (code %.1f)  chip=%.1f C (code %.1f)\n",
                   (unsigned long)(to_ms_since_boot(get_absolute_time()) / 1000),
                   (unsigned long)(clock_get_hz(clk_sys) / 1000),
                   (double)vsys_volts(vs.mean), (double)vs.mean,
                   (double)chip_temp_c(ct.mean), (double)ct.mean);
        }
        sleep_ms(250);
    }
}
