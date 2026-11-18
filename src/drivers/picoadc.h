/* picoadc.h - RP2350 internal ADC: VDD taps, passive level, VSYS, chip temperature. */
#ifndef PICOADC_H
#define PICOADC_H
#include "adc_burst.h"

void        picoadc_init(void);
/* input: PICOADC_IN_* from pins.h (0-4). Discards one conversion after
 * switching the mux, then averages n. */
adc_burst_t picoadc_read_burst(unsigned input, unsigned n);

#endif
