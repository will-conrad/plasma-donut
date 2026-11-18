/* Host tests for the MCP3208 frame helpers (mcp3208 p.19, p.21). */
#include <assert.h>
#include <stdio.h>
#include "drivers/mcp3208.h"

int main(void)
{
    uint8_t tx[3];

    mcp3208_build_frame(0, tx);   /* start, SGL, D2 D1 D0 = 000 */
    assert(tx[0] == 0x06 && tx[1] == 0x00 && tx[2] == 0x00);
    mcp3208_build_frame(3, tx);
    assert(tx[0] == 0x06 && tx[1] == 0xC0);
    mcp3208_build_frame(6, tx);   /* D2 = 1 lands in byte 0, D1 D0 = 10 in byte 1 */
    assert(tx[0] == 0x07 && tx[1] == 0x80);
    mcp3208_build_frame(7, tx);
    assert(tx[0] == 0x07 && tx[1] == 0xC0);

    /* every channel: start bit and SGL always set, 5 leading zeros */
    for (uint8_t ch = 0; ch < 8; ch++) {
        mcp3208_build_frame(ch, tx);
        assert((tx[0] & 0xFE) == 0x06);
        assert((uint8_t)(((tx[0] & 1) << 2) | (tx[1] >> 6)) == ch);
    }

    /* result: low nibble of byte 1 is B11..B8; the high nibble is junk */
    const uint8_t full[3] = { 0xFF, 0xFF, 0xFF };
    const uint8_t zero[3] = { 0xFF, 0xE0, 0x00 };
    const uint8_t mid[3]  = { 0x00, 0x08, 0x00 };
    const uint8_t mix[3]  = { 0x00, 0xFA, 0x5C };
    assert(mcp3208_parse_frame(full) == 4095);
    assert(mcp3208_parse_frame(zero) == 0);
    assert(mcp3208_parse_frame(mid)  == 2048);
    assert(mcp3208_parse_frame(mix)  == 0xA5C);

    printf("test_mcp3208_frame: all passed\n");
    return 0;
}
