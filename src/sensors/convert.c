#include "convert.h"
#include "../config/config.h"
#include <math.h>

const char *rd_status_str(rd_status_t s)
{
    switch (s) {
    case RD_OK:         return "ok";
    case RD_OPEN:       return "OPEN";
    case RD_SHORT:      return "SHORT";
    case RD_OVER_RANGE: return "OVER";
    case RD_NO_SIGNAL:  return "NOSIG";
    }
    return "?";
}

float adc_code_to_volts(float code, float vref)
{
    return code / ADC_FULL_SCALE * vref;
}

float ntc_resistance_ohm(float code)
{
    return NTC_RFIX_OHM * code / (ADC_FULL_SCALE - code);
}

reading_t ntc_temp_c(float code)
{
    reading_t r = { 0.0f, RD_OK };
    if (code >= NTC_CODE_OPEN)  { r.status = RD_OPEN;  return r; }
    if (code <= NTC_CODE_SHORT) { r.status = RD_SHORT; return r; }

    float res   = ntc_resistance_ohm(code);
    float inv_t = 1.0f / NTC_T0_K + logf(res / NTC_R0_OHM) / NTC_BETA_K;
    r.value = 1.0f / inv_t - 273.15f;
    return r;
}

reading_t vdd_volts(float code, float gain)
{
    reading_t r;
    r.value  = adc_code_to_volts(code, VREF_NOMINAL_V) * VDD_DIVIDER_RATIO * gain;
    r.status = (code >= VDD_CODE_OVER) ? RD_OVER_RANGE : RD_OK;
    return r;
}

float phase_deg(float code, float phi0_deg)
{
    return 180.0f * code / ADC_FULL_SCALE - phi0_deg;
}

float vsys_volts(float code)
{
    return adc_code_to_volts(code, VREF_NOMINAL_V) * VSYS_DIVIDER_RATIO;
}

float chip_temp_c(float code)
{
    float v = adc_code_to_volts(code, VREF_NOMINAL_V);
    return 27.0f - (v - CHIPTEMP_V_AT_27C) / CHIPTEMP_SLOPE_V_PER_C;
}
