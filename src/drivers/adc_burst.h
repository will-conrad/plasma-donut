/* adc_burst.h - result of an oversampled read. Pure C. */
#ifndef ADC_BURST_H
#define ADC_BURST_H
#include <stdint.h>

typedef struct {
    float    mean;  /* average code, keeps sub-LSB resolution */
    uint16_t min;   /* lowest single conversion in the burst */
    uint16_t max;   /* highest; (max - min) shows noise or RF pickup */
} adc_burst_t;

#endif
