/* Step 5 - MCP3208 raw codes, all 8 channels, twice a second.
 * Sanity checks: a channel tied to VCC reads about 4095, to GND about 0.
 * With JP1-JP4 bridged and no thermistor plugged in, CH0-CH3 read about 4095.
 * CH4/CH5 are not driven on Rev A: they are printed here only to see what a
 * floating input looks like. The real firmware never shows them. */
#include "hw_common.h"
#include "config/pins.h"
#include "config/config.h"
#include "drivers/mcp3208.h"
#include "sensors/convert.h"

static const char *const name[8] = {
    "MOS A", "MOS B", "Coil A", "Coil B", "(float)", "(float)", "Phase", "Spare"
};

int main(void)
{
    hw_start("Step 5: MCP3208 raw codes");
    mcp3208_init();

    for (;;) {
        printf("\nCH name     mean     min   max  spread   volts\n");
        for (uint8_t ch = 0; ch < 8; ch++) {
            adc_burst_t b = mcp3208_read_burst(ch, ADC_OVERSAMPLE);
            printf("%u  %-7s %7.1f  %4u  %4u  %4u   %6.4f\n",
                   ch, name[ch], (double)b.mean, b.min, b.max, b.max - b.min,
                   (double)adc_code_to_volts(b.mean, VREF_NOMINAL_V));
        }
        sleep_ms(500);
    }
}
