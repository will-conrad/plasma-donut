/* Step 6b - thermistors in degrees C, twice a second.
 * Checks: a 10k resistor in place of an NTC reads 25.0 C (code 2048).
 * Unplugged reads OPEN, a wire across the terminals reads SHORT.
 * A finger on the sensor should raise it a few degrees within seconds. */
#include "hw_common.h"
#include "config/pins.h"
#include "config/config.h"
#include "drivers/mcp3208.h"
#include "sensors/convert.h"

static const char *const name[4] = { "MOS A", "MOS B", "Coil A", "Coil B" };

int main(void)
{
    hw_start("Step 6b: thermistor temperatures");
    mcp3208_init();

    for (;;) {
        printf("\n");
        for (uint8_t ch = MCP_CH_TEMP_MOS_A; ch <= MCP_CH_TEMP_COIL_B; ch++) {
            adc_burst_t b = mcp3208_read_burst(ch, ADC_OVERSAMPLE);
            reading_t   t = ntc_temp_c(b.mean);
            if (t.status == RD_OK)
                printf("%-7s code %7.1f (%4u-%4u)  R %8.0f ohm  %7.2f C%s\n",
                       name[ch], (double)b.mean, b.min, b.max,
                       (double)ntc_resistance_ohm(b.mean), (double)t.value,
                       t.value >= TEMP_WARN_C ? "  HOT" : "");
            else
                printf("%-7s code %7.1f (%4u-%4u)  %s\n",
                       name[ch], (double)b.mean, b.min, b.max, rd_status_str(t.status));
        }
        sleep_ms(500);
    }
}
