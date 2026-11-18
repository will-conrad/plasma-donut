/* Host test for the framebuffer and font. Prints the screen as ASCII art so
 * the glyphs can be checked by eye:  ./test_gfx show */
#include <assert.h>
#include <stdio.h>
#include "ui/gfx.h"

static void show(int y0, int y1)
{
    for (int y = y0; y <= y1; y++) {
        for (int x = 0; x < GFX_W; x++) putchar(gfx_get(x, y) ? '#' : '.');
        putchar('\n');
    }
}

int main(int argc, char **argv)
{
    (void)argv;
    gfx_clear();
    gfx_pixel(0, 0, true);
    gfx_pixel(127, 63, true);
    assert(gfx_fb[0][0] == 0x01);          /* bit 0 is the top row of a page */
    assert(gfx_fb[7][127] == 0x80);
    gfx_pixel(0, 0, false);
    assert(gfx_fb[0][0] == 0x00);
    gfx_pixel(-1, 0, true); gfx_pixel(128, 0, true); gfx_pixel(0, 64, true);  /* clipped */

    gfx_clear();
    assert(gfx_text(0, 0, "AB") == 12);    /* 6 px per character */
    /* 'A' left stroke is rows 2-6 of column 0 (0x7C) */
    assert(!gfx_get(0, 1) && gfx_get(0, 2) && gfx_get(0, 6) && !gfx_get(0, 7));
    assert(gfx_fb[0][5] == 0x00);          /* gap column */
    gfx_text(120, 0, "WXYZ");              /* runs off the right edge: no crash */
    gfx_text(0, 9, "x");                   /* bad line: ignored */

    gfx_clear();
    gfx_rect(0, 0, 127, 63);
    assert(gfx_get(0, 0) && gfx_get(127, 0) && gfx_get(0, 63) && gfx_get(127, 63));
    assert(gfx_get(64, 0) && gfx_get(0, 32) && !gfx_get(64, 32));

    gfx_clear();
    gfx_invert_line(2);
    assert(gfx_fb[2][0] == 0xFF && gfx_fb[1][0] == 0x00);

    if (argc > 1) {
        const char *rows[] = {
            " !\"#$%&'()*+,-./01234", "56789:;<=>?@ABCDEFGHI", "JKLMNOPQRSTUVWXYZ[\\]^",
            "_`abcdefghijklmnopqrs", "tuvwxyz{|}~", "Hello Donut 25.0 C"
        };
        gfx_clear();
        for (int i = 0; i < 6; i++) gfx_text(0, i, rows[i]);
        show(0, 47);
    }
    printf("test_gfx: all passed\n");
    return 0;
}
