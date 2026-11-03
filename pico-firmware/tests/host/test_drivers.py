# Host tests for the datasheet-derived pure parts of the drivers. Run: python3 -m pytest tests/host
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import config as C          # noqa: E402
import mcp3208              # noqa: E402
import st7565               # noqa: E402


def test_mcp3208_frame_matches_datasheet():
    # mcp3208 p.19/p.21: start=1, SGL=1, then D2 D1 D0
    assert mcp3208.frame(0) == bytes((0x06, 0x00, 0x00))
    assert mcp3208.frame(5) == bytes((0x07, 0x40, 0x00))
    assert mcp3208.frame(7) == bytes((0x07, 0xC0, 0x00))


def test_mcp3208_parse():
    assert mcp3208.parse(bytes((0x00, 0x0F, 0xFF))) == 4095
    assert mcp3208.parse(bytes((0xFF, 0xF8, 0x00))) == 0x800   # high nibble of rx[1] ignored


def test_mcp3208_limits():
    assert C.MCP_SPI_MIN_HZ <= C.MCP_SPI_BAUD <= 1_000_000      # mcp3208 p.3
    assert 4 not in C.MCP_CH_ENABLED and 5 not in C.MCP_CH_ENABLED


def test_lcd_limits_and_init():
    assert C.LCD_SPI_BAUD <= 10_000_000                         # st7565r p.64 (2.7 V row)
    assert C.LCD_RESET_LOW_US >= 2                              # st7565r p.65 (2.7 V row)
    assert C.LCD_INIT[0] == 0xA2 and C.LCD_INIT[-1] == 0xAF     # nhd_c12864lz p.13
    assert 0 <= C.LCD_CONTRAST_DEFAULT <= 0x3F                  # 6-bit volume, st7565r p.50


def test_lcd_page_cmds():
    assert st7565.page_cmds(0, 0) == bytes((0xB0, 0x10, 0x00))
    assert st7565.page_cmds(7, 0x7F) == bytes((0xB7, 0x17, 0x0F))


def test_schmitt_bias_inside_window():
    lo = (C.SCHMITT_VT_POS[0] + C.SCHMITT_VT_NEG[0]) / 2
    hi = (C.SCHMITT_VT_POS[1] + C.SCHMITT_VT_NEG[1]) / 2
    assert lo <= C.SCHMITT_BIAS_V <= hi
