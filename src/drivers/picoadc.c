#include "picoadc.h"
#include "../config/pins.h"
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "hardware/structs/pads_bank0.h"

/* Analog pin setup. adc_gpio_init() selects FUNC_NULL, removes the pulls and
 * turns the digital input buffer off. Input-off matters here: erratum
 * RP2350-E9 leaks about 120 uA while the input buffer is on (rp2350 p.1359),
 * which would be a ~1.1 V error through the 9.1k VDD divider [calc].
 * The datasheet also asks for output-disable set on ADC pins (rp2350 p.966). */
static void analog_pin(uint gpio)
{
    adc_gpio_init(gpio);
    hw_set_bits(&pads_bank0_hw->io[gpio], PADS_BANK0_GPIO0_OD_BITS);
}

void picoadc_init(void)
{
    /* Regulator into PWM mode: lower ripple on the ADC supply (pico2 p.15-16). */
    gpio_init(PIN_SMPS_PS);
    gpio_put(PIN_SMPS_PS, 1);
    gpio_set_dir(PIN_SMPS_PS, GPIO_OUT);

    adc_init();
    analog_pin(PIN_VDD_TAP_A);
    analog_pin(PIN_VDD_TAP_B);
    analog_pin(PIN_PASSIVE_LEVEL);
    analog_pin(PIN_VSYS_SENSE);
    adc_set_temp_sensor_enabled(true);
}

adc_burst_t picoadc_read_burst(unsigned input, unsigned n)
{
    adc_burst_t b = { 0.0f, 4095, 0 };
    uint32_t sum = 0;
    if (n == 0) n = 1;

    adc_select_input(input);
    (void)adc_read();                   /* first conversion after a mux change */
    for (unsigned i = 0; i < n; i++) {
        uint16_t c = adc_read();        /* 2 us each at 500 kS/s (rp2350 p.968) */
        sum += c;
        if (c < b.min) b.min = c;
        if (c > b.max) b.max = c;
    }
    b.mean = (float)sum / (float)n;
    return b;
}
