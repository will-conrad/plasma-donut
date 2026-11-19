/* convert.h - raw ADC codes to real units. Pure C: builds on the Mac for host tests.
 * Codes are passed as float so an averaged burst keeps its sub-LSB resolution. */
#ifndef CONVERT_H
#define CONVERT_H

typedef enum {
    RD_OK = 0,
    RD_OPEN,        /* thermistor cable open */
    RD_SHORT,       /* thermistor cable shorted */
    RD_OVER_RANGE,  /* input at ADC full scale */
    RD_NO_SIGNAL
} rd_status_t;

typedef struct {
    float       value;
    rd_status_t status;
} reading_t;

const char *rd_status_str(rd_status_t s);

/* Volts at an ADC pin: V = code / 4096 * Vref */
float adc_code_to_volts(float code, float vref);

/* NTC on the bottom, Rfix on top, both fed from Vref, so Vref cancels:
 * R = Rfix * N / (4096 - N) */
float ntc_resistance_ohm(float code);

/* Beta model: 1/T = 1/T0 + ln(R/R0)/B. Returns degrees C, or OPEN / SHORT. */
reading_t ntc_temp_c(float code);

/* Full conversion for sensor 0-3: subtracts TEMP_SERIES_OHM, applies the Beta
 * model, then TEMP_CAL_GAIN / TEMP_CAL_OFFSET. OPEN / SHORT as ntc_temp_c. */
reading_t ntc_temp_c_sensor(float code, unsigned sensor);

/* Apply the TEMP_CAL_* correction for sensor 0-3. Passes OPEN/SHORT through. */
reading_t ntc_apply_cal(reading_t t, unsigned sensor);

/* Coil supply: VDD = 11 * Vpin * gain. OVER_RANGE at full scale. */
reading_t vdd_volts(float code, float gain);

/* XOR phase detector: phi = 180 * code/4096 - phi0. Magnitude only, no sign. */
float phase_deg(float code, float phi0_deg);

/* Pico 2 housekeeping */
float vsys_volts(float code);          /* ADC3 = VSYS/3 */
float chip_temp_c(float code);         /* RP2350 internal sensor */

#endif
