/* st7565.h - NHD-C12864LZ (ST7565R controller), write-only 4-wire SPI. */
#ifndef ST7565_H
#define ST7565_H
#include <stdint.h>
#include <stdbool.h>

void    st7565_init(void);                 /* pins, SPI1, hardware reset, vendor init */
void    st7565_reinit(void);               /* resend the init commands (RF recovery), keeps contrast */
void    st7565_set_contrast(uint8_t vol);  /* electronic volume 0-63 */
uint8_t st7565_get_contrast(void);
/* Orientation 0-3: bit 0 = mirror left-right (A1), bit 1 = flip top-bottom (C8).
 * 3 = rotated 180 degrees. Takes effect at once; redraw after. */
void    st7565_set_orientation(unsigned o);
unsigned st7565_get_orientation(void);
void    st7565_all_points(bool on);        /* every pixel on: panel test, ignores RAM */
void    st7565_flush(const uint8_t fb[8][128]);

#endif
