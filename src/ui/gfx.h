/* gfx.h - 128x64 1-bit framebuffer and 5x7 text. Pure C, host-testable.
 * Layout matches the ST7565R: 8 pages x 128 columns, one byte = 8 vertical
 * pixels with bit 0 at the top. */
#ifndef GFX_H
#define GFX_H
#include <stdint.h>
#include <stdbool.h>

#define GFX_W      128
#define GFX_H_PX   64
#define GFX_PAGES  8
#define GFX_CHAR_W 6     /* 5 px glyph + 1 px gap: 21 characters per line */

extern uint8_t gfx_fb[GFX_PAGES][GFX_W];

void gfx_clear(void);
void gfx_fill(uint8_t pattern);
void gfx_pixel(int x, int y, bool on);
bool gfx_get(int x, int y);
void gfx_hline(int x0, int x1, int y);
void gfx_vline(int x, int y0, int y1);
void gfx_rect(int x0, int y0, int x1, int y1);
/* Text on a page-aligned line: line 0-7, x in pixels. Returns the next x. */
int  gfx_text(int x, int line, const char *s);
void gfx_invert_line(int line);

#endif
