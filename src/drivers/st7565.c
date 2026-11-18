#include "st7565.h"
#include "../config/pins.h"
#include "../config/config.h"
#include "pico/stdlib.h"
#include "hardware/spi.h"

/* Command codes: st7565r p.50, Table 16 */
#define CMD_DISPLAY_OFF     0xAE
#define CMD_DISPLAY_ON      0xAF
#define CMD_START_LINE      0x40
#define CMD_PAGE            0xB0
#define CMD_COL_HIGH        0x10
#define CMD_COL_LOW         0x00
#define CMD_ALL_POINTS_OFF  0xA4
#define CMD_ALL_POINTS_ON   0xA5
#define CMD_BIAS_1_9        0xA2
#define CMD_POWER_ALL_ON    0x2F
#define CMD_RESISTOR_RATIO  0x20   /* | 0-7 */
#define CMD_VOLUME          0x81   /* followed by the volume byte */

static uint8_t contrast = LCD_CONTRAST_DEFAULT;
static uint8_t seg_dir  = LCD_CMD_SEG_DIR;
static uint8_t com_dir  = LCD_CMD_COM_DIR;
static uint8_t col_off  = LCD_COL_OFFSET;

static void write_bytes(bool is_data, const uint8_t *buf, size_t len)
{
    gpio_put(PIN_LCD_A0, is_data);
    gpio_put(PIN_LCD_CS, 0);
    spi_write_blocking(LCD_SPI_INSTANCE, buf, len);
    gpio_put(PIN_LCD_CS, 1);
}

static void cmd(uint8_t c) { write_bytes(false, &c, 1); }

static void send_init_commands(void)
{
    /* Vendor sequence (nhd_c12864lz p.13). The vendor sends C8 then C0; the
     * second wins, so only the final direction is sent here. */
    cmd(CMD_BIAS_1_9);
    cmd(seg_dir);
    cmd(com_dir);
    cmd(CMD_START_LINE | 0);
    cmd(CMD_RESISTOR_RATIO | 5);
    cmd(CMD_VOLUME);
    cmd(contrast & 0x3F);
    cmd(CMD_POWER_ALL_ON);
    cmd(CMD_ALL_POINTS_OFF);
    cmd(CMD_DISPLAY_ON);
}

void st7565_init(void)
{
    const uint outs[] = { PIN_LCD_CS, PIN_LCD_A0, PIN_LCD_RST };
    for (unsigned i = 0; i < 3; i++) {
        gpio_init(outs[i]);
        gpio_put(outs[i], 1);
        gpio_set_dir(outs[i], GPIO_OUT);
    }

    spi_init(LCD_SPI_INSTANCE, LCD_SPI_HZ);
    /* SI is sampled on the rising edge of SCL, MSB first: mode 0 (st7565r p.24) */
    spi_set_format(LCD_SPI_INSTANCE, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
    gpio_set_function(PIN_LCD_SCL, GPIO_FUNC_SPI);
    gpio_set_function(PIN_LCD_SI,  GPIO_FUNC_SPI);

    /* Hardware reset: /RES low >= 1 us at 3.3 V (st7565r p.65). Use far more. */
    gpio_put(PIN_LCD_RST, 0);
    sleep_ms(10);
    gpio_put(PIN_LCD_RST, 1);
    sleep_ms(10);

    send_init_commands();
    sleep_ms(50);                       /* let the charge pump settle */
}

void st7565_reinit(void) { send_init_commands(); }

void st7565_set_contrast(uint8_t vol)
{
    contrast = vol & 0x3F;
    cmd(CMD_VOLUME);
    cmd(contrast);
}

uint8_t st7565_get_contrast(void) { return contrast; }

void st7565_set_orientation(unsigned o)
{
    seg_dir = (o & 1u) ? 0xA1 : 0xA0;
    com_dir = (o & 2u) ? 0xC8 : 0xC0;
    col_off = (o & 1u) ? 4 : 0;   /* with A1, RAM column 0 is the 4th column past the glass */
    cmd(seg_dir);
    cmd(com_dir);
}

unsigned st7565_get_orientation(void)
{
    return (seg_dir == 0xA1 ? 1u : 0u) | (com_dir == 0xC8 ? 2u : 0u);
}

void st7565_all_points(bool on) { cmd(on ? CMD_ALL_POINTS_ON : CMD_ALL_POINTS_OFF); }

void st7565_flush(const uint8_t fb[8][128])
{
    for (unsigned page = 0; page < 8; page++) {
        cmd((uint8_t)(CMD_PAGE | page));
        cmd((uint8_t)(CMD_COL_HIGH | (col_off >> 4)));
        cmd((uint8_t)(CMD_COL_LOW  | (col_off & 0x0F)));
        write_bytes(true, fb[page], 128);
    }
}
