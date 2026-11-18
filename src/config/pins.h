/* pins.h - one #define per GPIO, taken from PINMAP.md (Rev A netlist).
 * Never edit a pin here without checking the KiCad schematic.
 * Pure C, no SDK headers, so host tests can include it. */
#ifndef PINS_H
#define PINS_H

/* Buttons: active low, external 10k pull-ups R16/R17 [netlist] */
#define PIN_BTN_1          2
#define PIN_BTN_2          3

/* LCD (ST7565R) on SPI1 [netlist] */
#define LCD_SPI_INSTANCE   spi1
#define PIN_LCD_SCL        10   /* SPI1 SCK */
#define PIN_LCD_SI         11   /* SPI1 TX  */
#define PIN_LCD_A0         12   /* low = command, high = data */
#define PIN_LCD_CS         13   /* /CS1, active low */
#define PIN_LCD_BL_PWM     14   /* Q1 gate, PWM7 A, R2 100k pull-down */
#define PIN_LCD_RST        15   /* /RES, active low */

/* MCP3208 on SPI0 [netlist] */
#define ADC_SPI_INSTANCE   spi0
#define PIN_ADC_MISO       16   /* SPI0 RX  */
#define PIN_ADC_CS         17   /* /CS, active low */
#define PIN_ADC_SCK        18   /* SPI0 SCK */
#define PIN_ADC_MOSI       19   /* SPI0 TX  */

/* Oscillator tap, J9 through R14 330R. Even GPIO: no PWM counting (rp2350 p.980) */
#define PIN_FREQ_QUARTZ    22

/* Pico 2 on-module pins (pico2 p.9, p.16) */
#define PIN_SMPS_PS        23   /* high = regulator PWM mode, lower ADC ripple */
#define PIN_VBUS_SENSE     24
#define PIN_LED            25
#define PIN_VSYS_SENSE     29   /* ADC3 = VSYS/3 */

/* Pico internal ADC inputs [netlist] */
#define PIN_VDD_TAP_A      26   /* ADC0, J11 through 100k/10k */
#define PIN_VDD_TAP_B      27   /* ADC1, J12 through 100k/10k */
#define PIN_PASSIVE_LEVEL  28   /* ADC2, passive-coil peak detector */

#define PICOADC_IN_VDD_A    0
#define PICOADC_IN_VDD_B    1
#define PICOADC_IN_PASSIVE  2
#define PICOADC_IN_VSYS     3
#define PICOADC_IN_CHIPTEMP 4   /* RP2350A (QFN-60): AINSEL = 4 (rp2350 p.970) */

/* MCP3208 channels [netlist] */
#define MCP_CH_TEMP_MOS_A   0
#define MCP_CH_TEMP_MOS_B   1
#define MCP_CH_TEMP_COIL_A  2
#define MCP_CH_TEMP_COIL_B  3
#define MCP_CH_PICKUP_A     4   /* NOT DRIVEN on Rev A: never display */
#define MCP_CH_PICKUP_B     5   /* NOT DRIVEN on Rev A: never display */
#define MCP_CH_PHASE        6
#define MCP_CH_SPARE        7   /* J14 through R13 1k */

#endif
