/* Step 6a - Pico internal ADC against a multimeter.
 * Feed a bench supply into a VDD tap (J11 = A, J12 = B) and compare the
 * printed VDD with the meter. Full scale is 36.3 V: stay below that.
 * gain = V_meter / V_printed is the calibration factor to store later. */
#include "hw_common.h"
#include "config/pins.h"
#include "config/config.h"
#include "drivers/picoadc.h"
#include "sensors/convert.h"

static void show_vdd(const char *label, unsigned input)
{
    adc_burst_t b = picoadc_read_burst(input, ADC_OVERSAMPLE);
    reading_t   v = vdd_volts(b.mean, VDD_GAIN_DEFAULT);
    printf("%-8s code %7.1f (%4u-%4u)  pin %6.4f V  VDD %6.2f V  %s\n",
           label, (double)b.mean, b.min, b.max,
           (double)adc_code_to_volts(b.mean, VREF_NOMINAL_V),
           (double)v.value, rd_status_str(v.status));
}

int main(void)
{
    hw_start("Step 6a: Pico ADC (VDD taps, passive level)");
    picoadc_init();

    for (;;) {
        printf("\n");
        show_vdd("VDD A", PICOADC_IN_VDD_A);
        show_vdd("VDD B", PICOADC_IN_VDD_B);
        adc_burst_t p = picoadc_read_burst(PICOADC_IN_PASSIVE, ADC_OVERSAMPLE);
        printf("%-8s code %7.1f (%4u-%4u)  pin %6.4f V\n", "Passive",
               (double)p.mean, p.min, p.max,
               (double)adc_code_to_volts(p.mean, VREF_NOMINAL_V));
        adc_burst_t s = picoadc_read_burst(PICOADC_IN_VSYS, ADC_OVERSAMPLE);
        printf("%-8s %5.2f V\n", "VSYS", (double)vsys_volts(s.mean));
        sleep_ms(500);
    }
}
