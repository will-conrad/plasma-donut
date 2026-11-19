/* Host tests for src/sensors/convert.c. Build and run: make -C tests/host */
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "sensors/convert.h"
#include "config/config.h"

static int near(float a, float b, float tol) { return fabsf(a - b) <= tol; }

/* Forward model: temperature -> ADC code, to round-trip the conversion. */
static float code_for_temp(float t_c)
{
    float r = NTC_R0_OHM * expf(NTC_BETA_K * (1.0f / (t_c + 273.15f) - 1.0f / NTC_T0_K));
    return ADC_FULL_SCALE * r / (r + NTC_RFIX_OHM);
}

int main(void)
{
    /* mid-scale: R = Rfix = 10k, which is 25 C by definition */
    assert(near(ntc_resistance_ohm(2048.0f), 10000.0f, 0.5f));
    assert(ntc_temp_c(2048.0f).status == RD_OK);
    assert(near(ntc_temp_c(2048.0f).value, 25.0f, 0.01f));

    /* table from the plan: 0 C -> code 3038, 85 C -> 519, 100 C -> 368 */
    assert(near(ntc_temp_c(3038.0f).value, 0.0f, 0.1f));
    assert(near(ntc_temp_c(519.0f).value, 85.0f, 0.1f));
    assert(near(ntc_temp_c(368.0f).value, 100.0f, 0.2f));

    /* round trip over the sensor's whole range */
    for (float t = -40.0f; t <= 150.0f; t += 5.0f)
        assert(near(ntc_temp_c(code_for_temp(t)).value, t, 0.02f));

    /* hotter means a lower code */
    assert(ntc_temp_c(1000.0f).value > ntc_temp_c(2000.0f).value);

    /* cable faults */
    assert(ntc_temp_c(4095.0f).status == RD_OPEN);
    assert(ntc_temp_c(4070.0f).status == RD_OPEN);
    assert(ntc_temp_c(4080.0f).status == RD_OPEN);   /* seen on the bench, open input */
    assert(ntc_temp_c(4069.0f).status == RD_OK);
    assert(ntc_temp_c(0.0f).status == RD_SHORT);
    assert(ntc_temp_c(5.0f).status == RD_SHORT);
    assert(ntc_temp_c(6.0f).status == RD_OK);
    /* the fault limits sit outside -55..150 C, so they cost no real range */
    assert(code_for_temp(-55.0f) < NTC_CODE_OPEN);
    assert(code_for_temp(150.0f) > NTC_CODE_SHORT);

    /* calibration applies gain * T + offset from config.h; faults pass through */
    {
        const float g[4] = TEMP_CAL_GAIN, o[4] = TEMP_CAL_OFFSET;
        for (unsigned k = 0; k < 4; k++)
            assert(near(ntc_apply_cal(ntc_temp_c(2048.0f), k).value, g[k] * 25.0f + o[k], 0.01f));
        assert(near(ntc_apply_cal(ntc_temp_c(2048.0f), 4).value, 25.0f, 0.01f));   /* out of range: untouched */
    }
    assert(ntc_apply_cal(ntc_temp_c(4095.0f), 0).status == RD_OPEN);

    /* series compensation: NTC at 36 C (6637 ohm) behind the configured series R */
    {
        const float rs[4] = TEMP_SERIES_OHM, g[4] = TEMP_CAL_GAIN, o[4] = TEMP_CAL_OFFSET;
        for (unsigned k = 0; k < 4; k++) {
            float r = 6637.0f + rs[k];
            float code = ADC_FULL_SCALE * r / (r + NTC_RFIX_OHM);
            assert(near(ntc_temp_c_sensor(code, k).value, g[k] * 36.0f + o[k], 0.05f));
        }
        /* reading below the series resistance means the NTC itself is shorted */
        if (rs[0] > 100.0f) {
            float r = rs[0] * 0.5f;
            assert(ntc_temp_c_sensor(ADC_FULL_SCALE * r / (r + NTC_RFIX_OHM), 0).status == RD_SHORT);
        }
        assert(ntc_temp_c_sensor(4095.0f, 0).status == RD_OPEN);
    }

    /* VDD: 12 V on the tap -> 1.0909 V at the pin -> code 1354.0 */
    assert(near(vdd_volts(1354.0f, 1.0f).value, 12.0f, 0.01f));
    assert(near(vdd_volts(4096.0f, 1.0f).value, 36.3f, 0.001f));
    assert(near(vdd_volts(1354.0f, 1.02f).value, 12.24f, 0.01f));
    assert(vdd_volts(1354.0f, 1.0f).status == RD_OK);
    assert(vdd_volts(4092.0f, 1.0f).status == RD_OVER_RANGE);

    /* phase: mid-scale is 90 degrees; phi0 subtracts */
    assert(near(phase_deg(2048.0f, 0.0f), 90.0f, 0.001f));
    assert(near(phase_deg(2048.0f, 12.5f), 77.5f, 0.001f));

    /* Pico housekeeping: 0.706 V is 27 C; VSYS 5 V -> 1.667 V -> code 2068.7 */
    assert(near(chip_temp_c(0.706f / 3.3f * 4096.0f), 27.0f, 0.01f));
    assert(near(vsys_volts(2068.7f), 5.0f, 0.01f));

    printf("test_convert: all passed\n");
    return 0;
}
