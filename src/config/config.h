/* config.h - limits and constants. Pure C, no SDK headers.
 * Each number carries its source: (part p.N) datasheet page, [netlist], [calc]. */
#ifndef CONFIG_H
#define CONFIG_H

/* ---- ADC scaling ---- */
#define ADC_FULL_SCALE        4096.0f  /* both ADCs are 12-bit */
#define VREF_NOMINAL_V        3.3f     /* /VREF_ADC and Pico ADC_VREF, nominal */
#define ADC_OVERSAMPLE        16       /* conversions averaged per reading */

/* ---- MCP3208 ---- */
#define MCP3208_SPI_HZ        1000000  /* 1 MHz max at 2.7 V, 2 MHz at 5 V (mcp3208 p.3) */
/* Channels the firmware may show: CH0-3, CH6, CH7. CH4/CH5 float [netlist]. */
#define MCP_CH_ENABLED_MASK   0xCFu

/* ---- Thermistors: NTCS0603E3103FLT (ntcs0603e3 p.1) ---- */
#define NTC_R0_OHM            10000.0f /* R25, +-1 % */
#define NTC_T0_K              298.15f
#define NTC_BETA_K            3435.0f  /* B25/85, +-1 % */
#define NTC_RFIX_OHM          10000.0f /* R4-R7 on top, from /VREF_ADC [netlist] */
#define NTC_CODE_OPEN         4070.0f  /* at or above: open cable. Board reads 4080-4094 open (bench 2026-11-17); -55 C is code 4037 [calc] */
#define NTC_CODE_SHORT        5.0f     /* at or below: shorted cable */
/* Per-sensor correction, T_true = gain * T_board + offset, in the order
 * MOS A, MOS B, Coil A, Coil B. Set by tools/cal_thermistors.py. */
#define TEMP_CAL_GAIN    { 1.0000f, 1.0000f, 1.0000f, 1.0000f }
#define TEMP_CAL_OFFSET  { +0.00f, +0.00f, +0.00f, +0.00f }
/* Resistance in series with each NTC on the far board, subtracted before the
 * Beta model. MOS A: about 10k fits camera 60 C / board 20 C and camera 36 C /
 * board 17.0k (2026-11-18) [assumed: a 10k resistor on Brennan's board, to confirm]. */
#define TEMP_SERIES_OHM  { 10000.0f, 0.0f, 0.0f, 0.0f }
#define TEMP_WARN_C           80.0f    /* PLACEHOLDER until Brennan gives real limits */

/* ---- Coil VDD taps: 100k / 10k [netlist] ---- */
#define VDD_DIVIDER_RATIO     11.0f
#define VDD_CODE_OVER         4090.0f  /* at or above: input is past full scale */
#define VDD_GAIN_DEFAULT      1.0f     /* per-channel gain cal goes in flash later */

/* ---- Pico 2 module ---- */
#define VSYS_DIVIDER_RATIO    3.0f     /* ADC3 = VSYS/3 (pico2 p.9) */
#define CHIPTEMP_V_AT_27C     0.706f   /* (rp2350 p.970) */
#define CHIPTEMP_SLOPE_V_PER_C 0.001721f

/* ---- LCD ---- */
#define LCD_SPI_HZ            4000000  /* limit is 20 MHz at 3.3 V (st7565r p.64); brief says <= 10 MHz */
#define LCD_CONTRAST_DEFAULT  0x13     /* electronic volume. Vendor 0x19 (nhd_c12864lz p.13) gave vertical streaks on Rev A; 0x13 confirmed by Will 2026-11-17 */
#define LCD_CMD_SEG_DIR       0xA0     /* 0xA0 normal, 0xA1 mirrored left-right */
#define LCD_CMD_COM_DIR       0xC8     /* 0xC0 normal, 0xC8 flipped top-bottom. A0+C8 confirmed by Will on Rev A, 2026-11-17 */
#define LCD_COL_OFFSET        0        /* 4 with 0xA1, 0 with 0xA0: the RAM is 132 columns wide */

/* ---- Backlight (ISSUES #7) ---- */
#define BL_PWM_HZ             1000
#define BL_MAX_DUTY_PCT       75       /* LED max 100 mA (nhd_c12864lz p.7), R1 0.25 W */

/* ---- Buttons (CLAUDE.md UI section) ---- */
#define BTN_POLL_MS           10
#define BTN_DEBOUNCE_MS       20       /* input must hold steady this long */
#define BTN_LONG_MS           800      /* held this long = long press */
/* Which button means "up" and which "down" for level controls. Set from how
 * SW1/SW2 sit on the Rev A board (Will, 2026-11-17): BTN1 = up, BTN2 = down. */
#define BTN_IDX_UP            0        /* index 0 = BTN1 (GP2) */
#define BTN_IDX_DOWN          1        /* index 1 = BTN2 (GP3) */

#endif
