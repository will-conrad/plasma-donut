# mcp3208.py -- MCP3208 (U1) driver. Datasheet: Microchip DS21298E (Microcontroller-PCB/datasheets/pdf/mcp3208.pdf)
#   SPI mode 0,0 (mcp3208 p.1; Figure 6-1 p.21) . clock 1 MHz at 3.3 V (p.3) . CS high >= 500 ns (p.3)
#   3-byte frame, single-ended: start bit, SGL=1, D2 | D1 D0 | don't care (config bits p.19, Fig 6-1 p.21)
# The two pure functions below are unit-tested on the host (tests/host/test_drivers.py).
import config as C


def frame(ch):
    """Bytes to send for a single-ended read of channel 0..7."""
    if not 0 <= ch <= 7:
        raise ValueError("MCP3208 channel 0..7")
    return bytes((0x06 | (ch >> 2), (ch & 0x03) << 6, 0x00))


def parse(rx):
    """12-bit result from the 3 received bytes (null bit + B11..B8 in rx[1] low nibble, B7..B0 in rx[2])."""
    return ((rx[1] & 0x0F) << 8) | rx[2]


class MCP3208:
    def __init__(self, oversample=16):
        from machine import SPI, Pin          # imported here so the pure functions work on a PC
        self.spi = SPI(C.ADC_SPI_ID, baudrate=C.MCP_SPI_BAUD, polarity=C.MCP_SPI_POLARITY,
                       phase=C.MCP_SPI_PHASE, bits=8, firstbit=SPI.MSB,
                       sck=Pin(C.PIN_ADC_SCK), mosi=Pin(C.PIN_ADC_MOSI), miso=Pin(C.PIN_ADC_MISO))
        self.cs = Pin(C.PIN_ADC_CS, Pin.OUT, value=1)
        self.n = oversample
        self._rx = bytearray(3)

    def read(self, ch):
        """Averaged 12-bit code. Refuses channels not in MCP_CH_ENABLED (CH4/5 are undriven: ISSUES #5)."""
        if ch not in C.MCP_CH_ENABLED:
            raise ValueError(f"MCP3208 CH{ch} is not driven on this board")
        import time
        tx = frame(ch)
        total = 0
        for _ in range(self.n):
            self.cs(0)
            self.spi.write_readinto(tx, self._rx)
            self.cs(1)
            time.sleep_us(C.MCP_TCSH_US)       # t_CSH >= 500 ns (mcp3208 p.3)
            total += parse(self._rx)
        return total // self.n

    def read_all(self):
        return {ch: self.read(ch) for ch in C.MCP_CH_ENABLED}
