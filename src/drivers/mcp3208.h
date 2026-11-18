/* mcp3208.h - MCP3208 12-bit SPI ADC (Microchip DS21298E).
 * The frame helpers are pure C so host tests can check them. */
#ifndef MCP3208_H
#define MCP3208_H
#include <stdint.h>
#include "adc_burst.h"

/* Single-ended 3-byte frame (mcp3208 p.21 Fig 6-1, config bits p.19):
 *   byte 0: 0 0 0 0 0 START SGL D2
 *   byte 1: D1 D0 x x x x x x
 *   byte 2: don't care
 * The chip answers with a null bit, then B11..B0 in the last 12 bit times. */
static inline void mcp3208_build_frame(uint8_t ch, uint8_t tx[3])
{
    tx[0] = (uint8_t)(0x06u | ((ch & 0x07u) >> 2));
    tx[1] = (uint8_t)((ch & 0x03u) << 6);
    tx[2] = 0x00u;
}

static inline uint16_t mcp3208_parse_frame(const uint8_t rx[3])
{
    return (uint16_t)(((rx[1] & 0x0Fu) << 8) | rx[2]);
}

void        mcp3208_init(void);
uint16_t    mcp3208_read(uint8_t ch);                 /* one conversion, ch 0-7 */
adc_burst_t mcp3208_read_burst(uint8_t ch, unsigned n);

#endif
