#include "mcp3208.h"
#include "../config/pins.h"
#include "../config/config.h"
#include "pico/stdlib.h"
#include "hardware/spi.h"

void mcp3208_init(void)
{
    /* CS is a plain GPIO so it frames exactly one 3-byte conversion. */
    gpio_init(PIN_ADC_CS);
    gpio_put(PIN_ADC_CS, 1);
    gpio_set_dir(PIN_ADC_CS, GPIO_OUT);

    spi_init(ADC_SPI_INSTANCE, MCP3208_SPI_HZ);
    /* Mode 0,0, MSB first (mcp3208 p.21) */
    spi_set_format(ADC_SPI_INSTANCE, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
    gpio_set_function(PIN_ADC_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_ADC_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(PIN_ADC_MISO, GPIO_FUNC_SPI);
}

uint16_t mcp3208_read(uint8_t ch)
{
    uint8_t tx[3], rx[3];
    mcp3208_build_frame(ch, tx);

    gpio_put(PIN_ADC_CS, 0);
    busy_wait_us_32(1);                 /* t_SUCS >= 100 ns (mcp3208 p.3) */
    spi_write_read_blocking(ADC_SPI_INSTANCE, tx, rx, 3);
    gpio_put(PIN_ADC_CS, 1);
    busy_wait_us_32(1);                 /* t_CSH >= 500 ns (mcp3208 p.3) */

    return mcp3208_parse_frame(rx);
}

adc_burst_t mcp3208_read_burst(uint8_t ch, unsigned n)
{
    adc_burst_t b = { 0.0f, 4095, 0 };
    uint32_t sum = 0;
    if (n == 0) n = 1;
    for (unsigned i = 0; i < n; i++) {
        uint16_t c = mcp3208_read(ch);
        sum += c;
        if (c < b.min) b.min = c;
        if (c > b.max) b.max = c;
    }
    b.mean = (float)sum / (float)n;
    return b;
}
