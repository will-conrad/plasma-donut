# config.py -- pin map and board constants for the Plasma Donut control board.
#
# Source of truth: Microcontroller-PCB.kicad_sch (saved 2026-10-22 13:43),
# netlist exported with kicad-cli 10.0.6. Do not edit pins here without
# re-checking the schematic. Pure constants, no `machine` import, so pytest
# can import this on the host.
#
# STATUS: Step 0 draft. Waiting for Will to confirm PINMAP.md.

# ---------------------------------------------------------------- GPIO map
# Buttons (active low; external 10k pull-ups R16/R17 to VCC, 100 nF to GND)
PIN_BTN_1 = 2          # /BTN_1   -> SW1
PIN_BTN_2 = 3          # /BTN_2   -> SW2

# LCD, ST7565R, 4-wire SPI on SPI1 (write-only, no MISO)
LCD_SPI_ID = 1
PIN_LCD_SCL = 10       # /LCD_SCL -> DS1 pin 12 (DB6 = SCL in serial mode), SPI1 SCK
PIN_LCD_SI = 11        # /LCD_SI  -> DS1 pin 13 (DB7 = SI),                SPI1 TX
PIN_LCD_A0 = 12        # /LCD_A0  -> DS1 pin 3  (data / command)
PIN_LCD_CS = 13        # /LCD_CS  -> DS1 pin 1  (/CS1), driven as plain GPIO
PIN_LCD_BL = 14        # /LCD_BL_PWM -> Q1 gate (AO3400A), PWM7 channel A
PIN_LCD_RST = 15       # /LCD_RST -> DS1 pin 2  (/RES)

# MCP3208 on SPI0 (separate bus from the LCD)
ADC_SPI_ID = 0
PIN_ADC_MISO = 16      # /ADC_MISO -> U1 Dout
PIN_ADC_CS = 17        # /ADC_CS   -> U1 /CS, driven as plain GPIO
PIN_ADC_SCK = 18       # /ADC_SCK  -> U1 CLK
PIN_ADC_MOSI = 19      # /ADC_MOSI -> U1 Din

# Frequency input. GPIO22 is EVEN => PWM channel A => no hardware edge
# counting. Needs a PIO edge counter.
PIN_FREQ_OSC = 22      # /FREQ_QUARTZ <- R14 (330 R) <- J9 "QUARTZ OSC"

# Pico internal ADC (RP2350, 12-bit, reference = ADC_VREF pin, not VREF_ADC)
PIN_VDD_TAP_A = 26     # ADC0  /VDD_TAP_A      (J11 via 100k / 10k divider)
PIN_VDD_TAP_B = 27     # ADC1  /VDD_TAP_B      (J12 via 100k / 10k divider)
PIN_PASSIVE_LEVEL = 28 # ADC2  /PASSIVE_LEVEL  (peak-detected passive coil, also on J15.13)
ADC_CH_VDD_A = 0
ADC_CH_VDD_B = 1
ADC_CH_PASSIVE = 2

# Debug header J15 (no HV connection). Leave as high-impedance inputs.
PIN_DBG_UART_TX = 0    # J15.4
PIN_DBG_UART_RX = 1    # J15.5
PINS_J15_SPARE = (4, 5, 6, 7, 8, 20, 21)   # J15.6..J15.12; 4/5 labelled I2C SDA/SCL
# GPIO9 is unconnected.

# Every GPIO that is NOT driven by firmware stays a high-impedance input.
# No Pico output reaches an HV board (checked 2026-10-26, see PINMAP.md).

# ---------------------------------------------------------------- MCP3208
# channel -> net (U1). VREF = /VREF_ADC.
MCP_CH_TEMP_MOS_A = 0
MCP_CH_TEMP_MOS_B = 1
MCP_CH_TEMP_COIL_A = 2
MCP_CH_TEMP_COIL_B = 3
MCP_CH_PICKUP_A = 4    # NOT DRIVEN: net /PICKUP_A has only C24 on it
MCP_CH_PICKUP_B = 5    # NOT DRIVEN: net /PICKUP_B has only C25 on it
MCP_CH_PHASE = 6       # XOR output after R20 / C26
MCP_CH_SPARE = 7       # J14 "SPARE" via R13 (1k) / C27
MCP_SPI_BAUD = 1_000_000   # max 1.0 MHz at 2.7 V / 2.0 MHz at 5 V (mcp3208 p.3); 3.3 V not specified -> stay at 1 MHz

# ---------------------------------------------------------------- Analog front ends (from schematic values)
V_LOGIC = 3.3          # VCC rail; U3 (XOR), U4, U5 and U1 Vdd all run from it
V_REF_NOM = 3.3        # /VREF_ADC = VCC through R3 (10 R), C16 0.1 uF + C17 10 uF

# Coil VDD taps: R23/R24 = 100k on top, R8/R9 = 10k to GNDA
VDD_DIV_TOP = 100_000
VDD_DIV_BOT = 10_000
VDD_DIV_RATIO = (VDD_DIV_TOP + VDD_DIV_BOT) / VDD_DIV_BOT   # 11.0, NOT 9.2

# Thermistors: R4..R7 = 10k from /VREF_ADC (through bridged JP1..JP4) on TOP,
# NTC on the BOTTOM to GNDA (off-board, screw terminals J3..J6).
NTC_R_FIX = 10_000
NTC_TOP_FIXED = True
NTC_R0 = 10_000
NTC_T0_K = 298.15
NTC_BETA = 3435        # B25/85 = 3435 K +/-1 % CONFIRMED: Vishay NTCS0603E3 doc 29056 p.1 ('...103FLT': F = R25 1 %, L = 3435 K)

# Phase detector: U3 = 74LVC1G86 (XOR), VCC = 3.3 V. R20 = 10k, C26 = 0.1 uF.
PHASE_R_FILTER = 10_000
PHASE_C_FILTER = 100e-9
PHASE_TAU_S = PHASE_R_FILTER * PHASE_C_FILTER   # 1.0 ms (brief assumed 2.1 ms)
# Squarers: R19 = R22 = 7.15k, R18 = R21 = 10k (bias ~1.38 V). Fix IS applied in schematic.

# ---------------------------------------------------------------- Oscillator flag
OSC_NOMINAL_HZ = 13_560_000
OSC_TOL = 0.05         # "oscillating" if within +/-5 %

# ---------------------------------------------------------------- Warnings
T_WARN_C = 80.0        # PLACEHOLDER until Brennan confirms real limits


# ================================================================ Fixes from docs/ISSUES.md (2026-11-01)
# Each constant names the issue it implements. Nothing here needs new parts.

# ISSUES #5 -- MCP3208 CH4/CH5 (/PICKUP_A/B) have nothing driving them. Never display them,
# unless the optional amplitude bodge (BAT54WS + 100k from TAP_SENSE) has been fitted.
MCP_CH_ENABLED = (0, 1, 2, 3, 6, 7)
BODGE_PICKUP_AMPLITUDE = False      # set True only after the docs/REWORK.md step R5b is done
if BODGE_PICKUP_AMPLITUDE:
    MCP_CH_ENABLED = (0, 1, 2, 3, 4, 5, 6, 7)

# ISSUES #5 -- optional bodge: TP3 (SQ_A) -> J15.7 (GP5), TP4 (SQ_B) -> J15.9 (GP7), each via 330 R.
BODGE_SQ_TO_GP5_GP7 = False         # set True only after docs/REWORK.md step R5a
PIN_SQ_A = 5
PIN_SQ_B = 7

# ISSUES #6 -- GPIO22 is an even pin (no PWM edge count). It is GPIN1 (RP2350 DS p.19), so the
# on-chip frequency counter FC0 can measure it. "fc0" = FC0 on GPIN1, "pio" = PIO edge counter.
FREQ_METHOD = "fc0"
FC0_INTERVAL = 15                   # 2**15 us ~ 32 ms -> +/-62.5 Hz (RP2350 DS Table 574, p.476)
CLK_REF_KHZ = 12_000                # Pico 2 clk_ref = 12 MHz XOSC. freq.self_test() checks this.
PIO_GATE_MS = 250                   # gate time for the PIO fallback / SQ counters

# ISSUES #7 -- backlight current/R1 power corners. Cap PWM duty at 75 %.
BL_PWM_HZ = 1_000
BL_MAX_DUTY = 0.75
BL_DEFAULT_DUTY = 0.75

# ISSUES #8 -- RP2350 ADC input impedance (>= 100 k, DS p.1339) vs 9.1 k dividers.
# Read in short bursts, never continuously; let C22/C23/C38 recover (tau ~ 0.9 ms) between bursts.
PICO_ADC_BURST = 16
PICO_ADC_MIN_GAP_MS = 5
PICO_ADC_VREF = 3.3                 # nominal; real ADC_AVDD is ~30 mV lower (Pico 2 DS p.15) -> calibrate
# Per-channel gain calibration (multiply), set from a multimeter reading via cal.py; stored in cal.json.
CAL_DEFAULTS = {"vdd_a_gain": 1.0, "vdd_b_gain": 1.0, "passive_gain": 1.0, "phase_zero_deg": 0.0}

# Passive-coil peak detector (DC-12): k = C36/(C36+C37+CJ) ~ 10/350; D1 VF ~ 0.24 V @ 0.1 mA.
PASSIVE_DIV_K = 10 / 350
PASSIVE_D1_VF = 0.24
PASSIVE_MIN_VALID_V = 0.05          # below this at the pin, report "< ~10 V pk"

# ISSUES #15 -- thermistor fault detection (open cable reads ~4095, short ~0).
NTC_OPEN_CODE = 4090
NTC_SHORT_CODE = 5

# ISSUES #11 -- phase calibration is required (U4/U5 skew up to ~23 deg, DC-09).
PHASE_REQUIRE_CAL = True

# ISSUES #16 -- unused GPIOs: enable pull-ups so they never float in the RP2350-E9 region.
PINS_UNUSED_PULLUP = tuple(p for p in (4, 5, 6, 7, 8, 9, 20, 21)
                           if not (BODGE_SQ_TO_GP5_GP7 and p in (PIN_SQ_A, PIN_SQ_B)))


# ================================================================ Datasheet-derived limits (2026-11-02)
# Tags: (part p.N) = page in Microcontroller-PCB/datasheets/pdf, verified by flagcheck R-A2;
#       [web] = fetched, PDF not cached; [calc] = computed from the values shown; [netlist] = KiCad fact.

# MCP3208 (U1), DS21298E
MCP_SPI_MIN_HZ = 10_000          # below this the sample cap droops (mcp3208 p.3, note 3)
MCP_TCSH_US = 1                  # CS high >= 500 ns between conversions (mcp3208 p.3); 1 us used
MCP_SPI_POLARITY = 0             # modes 0,0 or 1,1 (mcp3208 p.1, Fig 6-1 p.21)
MCP_SPI_PHASE = 0

# LCD: NHD-C12864LZ-FSW-FBW-3V3 (DS1) + ST7565R
LCD_SPI_BAUD = 10_000_000        # tSCYC >= 50 ns @3.3 V, >= 100 ns @2.7 V (st7565r p.64) -> 10 MHz
LCD_RESET_LOW_US = 10            # /RES low >= 1 us @3.3 V, >= 2 us @2.7 V (st7565r p.65)
LCD_RESET_WAIT_US = 10           # reset completes within 1-2 us (st7565r p.65)
# Vendor init sequence (nhd_c12864lz p.13). C8 is immediately overridden by C0 in the vendor code;
# both are kept for fidelity. Command meanings from st7565r p.50, Table 16.
LCD_INIT = (0xA2,                # LCD bias 1/9
            0xA0,                # ADC select: normal
            0xC8, 0xC0,          # COM output scan: reverse, then normal (second wins)
            0x40,                # display start line 0
            0x25,                # V0 regulator resistor ratio = 5
            0x81, 0x19,          # electronic volume mode + value 0x19 (tune contrast here)
            0x2F,                # power control: booster + regulator + follower on
            0xAF)                # display ON
LCD_CONTRAST_DEFAULT = 0x19      # 6-bit electronic volume (st7565r p.50)
LCD_REINIT_S = 5                 # RF-immunity re-init period (brief); SCL is noise sensitive (st7565r p.24)
LCD_VDD_MAX = 3.3                # (nhd_c12864lz p.7); VCC is at this limit -> measure TP2 at bring-up
LCD_TEMP_MAX_C = 70              # (nhd_c12864lz p.7)
BL_LED_MAX_MA = 100              # (nhd_c12864lz p.7) -> enforced via BL_MAX_DUTY above

# NTC (Vishay NTCS0603E3103FLT)
NTC_R25_TOL = 0.01               # F suffix (ntcs0603e3 p.1)
NTC_TAU_S = 4                    # thermal time constant < 4 s (ntcs0603e3 p.1): readings lag by seconds
NTC_BETA_VALID_MAX_C = 85        # B25/85 fit; beyond 85 C use the Vishay R-T table [calc reasoning]

# RP2350 / Pico 2
PICO_ADC_ENOB = 9.0              # 9-9.5 bits (rp2350 p.1339)
PICO_ADC_RIN_MIN = 100_000       # (rp2350 p.1339) -> burst sampling (ISSUES #8)
PIN_SMPS_PS = 23                 # high = SMPS PWM mode, lower ripple on 3V3/ADC_VREF (pico2 p.15)
SMPS_PWM_DURING_ADC = True       # drive GPIO23 high around Pico ADC bursts
GPIO_VIH_MIN = 2.0               # IOVDD 3.3 V (rp2350 p.1337)
GPIO_VIL_MAX = 0.8               # (rp2350 p.1337)
# Erratum E9 (rp2350 p.1359): never rely on internal pull-downs -> buttons use external pull-ups [netlist]

# Schmitt / XOR (Nexperia, PDFs not cached locally)
SCHMITT_VT_POS = (1.29, 1.71)    # VCC = 3.0 V row [web: Nexperia 74LVC1G17 Table 8]
SCHMITT_VT_NEG = (0.88, 1.24)    # [web: Nexperia 74LVC1G17 Table 8]
SCHMITT_BIAS_V = 3.3 * 7.15 / 17.15   # R18 10k / R19 7.15k [netlist][calc] = 1.376 V
PICKUP_WINDOW_VPK = (17, 47)     # at J16/J17 with R25 10k / R26 330 [calc, design-requirements DC-08]
