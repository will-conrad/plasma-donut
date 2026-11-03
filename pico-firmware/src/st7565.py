# st7565.py -- NHD-C12864LZ-FSW-FBW-3V3 (DS1, ST7565R controller), 4-wire SPI, write-only.
# Sources (Microcontroller-PCB/datasheets/pdf):
#   init sequence ........ nhd_c12864lz p.13          command codes ...... st7565r p.50 (Table 16)
#   SPI: rising edge, MSB first, A0 sampled every 8th clock, no reads ...... st7565r p.24
#   SPI clock <= 20 MHz @3.3 V / 10 MHz @2.7 V ... st7565r p.64   /RES >= 1 us ... st7565r p.65
#   RAM: 8 pages x 128 columns, 1 byte = 8 vertical pixels -> framebuf.MONO_VLSB
import config as C

W, H, PAGES = 128, 64, 8
CMD_PAGE = 0xB0          # | page (0..7)          (st7565r p.50, (3))
CMD_COL_HI = 0x10        # | column >> 4          (st7565r p.50, (4))
CMD_COL_LO = 0x00        # | column & 0x0F        (st7565r p.50, (4))
CMD_VOLUME = 0x81        # + 6-bit value          (st7565r p.50, (18))
CMD_ALL_ON = 0xA5        # all points on (test)   (st7565r p.50, (10))
CMD_NORMAL = 0xA4


def page_cmds(page, col=0):
    """Command bytes to address (page, column). Pure: unit-tested on the host."""
    return bytes((CMD_PAGE | (page & 0x07), CMD_COL_HI | ((col >> 4) & 0x0F), CMD_COL_LO | (col & 0x0F)))


class ST7565:
    def __init__(self):
        import framebuf
        from machine import SPI, Pin
        self.spi = SPI(C.LCD_SPI_ID, baudrate=C.LCD_SPI_BAUD, polarity=0, phase=0, bits=8, firstbit=SPI.MSB,
                       sck=Pin(C.PIN_LCD_SCL), mosi=Pin(C.PIN_LCD_SI))      # no MISO: write-only (st7565r p.24)
        self.cs = Pin(C.PIN_LCD_CS, Pin.OUT, value=1)
        self.a0 = Pin(C.PIN_LCD_A0, Pin.OUT, value=0)
        self.rst = Pin(C.PIN_LCD_RST, Pin.OUT, value=1)
        self.buf = bytearray(W * PAGES)
        self.fb = framebuf.FrameBuffer(self.buf, W, H, framebuf.MONO_VLSB)
        self.contrast = C.LCD_CONTRAST_DEFAULT
        self.init(hard=True)

    def _cmd(self, data):
        self.a0(0); self.cs(0); self.spi.write(bytes(data)); self.cs(1)

    def _data(self, data):
        self.a0(1); self.cs(0); self.spi.write(data); self.cs(1)

    def init(self, hard=False):
        """Vendor init (nhd_c12864lz p.13). Called again every LCD_REINIT_S for RF immunity."""
        import time
        if hard:
            self.rst(0); time.sleep_us(C.LCD_RESET_LOW_US)     # >= 1 us (st7565r p.65)
            self.rst(1); time.sleep_us(C.LCD_RESET_WAIT_US)
        seq = list(C.LCD_INIT)
        seq[seq.index(0x81) + 1] = self.contrast & 0x3F         # keep the tuned contrast on re-init
        self._cmd(seq)

    def set_contrast(self, v):
        self.contrast = v & 0x3F
        self._cmd((CMD_VOLUME, self.contrast))

    def show(self):
        for p in range(PAGES):
            self._cmd(page_cmds(p, 0))
            self._data(memoryview(self.buf)[p * W:(p + 1) * W])

    def test_pattern(self, on=True):
        self._cmd((CMD_ALL_ON if on else CMD_NORMAL,))
