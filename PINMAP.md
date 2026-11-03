# Pico 2 pin map (Step 0)

Source: `Microcontroller-PCB.kicad_sch`, saved 2026-10-22 13:43, netlist from kicad-cli 10.0.6.
The PCB file (saved 2026-10-22 18:46) agrees on the parts that differ from the brief. ERC reports 0 errors (4 library-symbol-mismatch warnings only). Nothing in the KiCad folder was modified.

## GPIO -> net -> function

| GPIO | Pico pin | Net | Function |
|---|---|---|---|
| 0 | 1 | /DBG_UART_TX | J15.4 debug header |
| 1 | 2 | /DBG_UART_RX | J15.5 debug header |
| 2 | 4 | /BTN_1 | Button 1 (SW1), active low, R16 10k pull-up to VCC, C28 100 nF |
| 3 | 5 | /BTN_2 | Button 2 (SW2), active low, R17 10k pull-up to VCC, C29 100 nF |
| 4 | 6 | /GP4_I2C_SDA | J15.6 only |
| 5 | 7 | /GP5_I2C_SCL | J15.7 only |
| 6 | 9 | /GP6 | J15.8 only |
| 7 | 10 | /GP7 | J15.9 only |
| 8 | 11 | /GP8 | J15.10 only |
| 9 | 12 | unconnected | -- |
| 10 | 14 | /LCD_SCL | LCD DB6 = SCL, SPI1 SCK |
| 11 | 15 | /LCD_SI | LCD DB7 = SI, SPI1 TX |
| 12 | 16 | /LCD_A0 | LCD A0 (data/command) |
| 13 | 17 | /LCD_CS | LCD /CS1 |
| 14 | 19 | /LCD_BL_PWM | Q1 (AO3400A) gate, R2 100k pull-down. PWM7 A |
| 15 | 20 | /LCD_RST | LCD /RES |
| 16 | 21 | /ADC_MISO | MCP3208 Dout, SPI0 RX |
| 17 | 22 | /ADC_CS | MCP3208 /CS |
| 18 | 24 | /ADC_SCK | MCP3208 CLK, SPI0 SCK |
| 19 | 25 | /ADC_MOSI | MCP3208 Din, SPI0 TX |
| 20 | 26 | /GP20 | J15.11 only |
| 21 | 27 | /GP21 | J15.12 only |
| **22** | 29 | /FREQ_QUARTZ | J9 "QUARTZ OSC" via R14 330 R. **Even GPIO** |
| 26 | 31 | /VDD_TAP_A | Pico ADC0, J11 via 100k/10k divider |
| 27 | 32 | /VDD_TAP_B | Pico ADC1, J12 via 100k/10k divider |
| 28 | 34 | /PASSIVE_LEVEL | Pico ADC2, peak-detected passive coil (also J15.13) |

## MCP3208 (U1) channels

| CH | Net | What is on it |
|---|---|---|
| 0 | /TEMP_MOSFET_A | J3 NTC, R4 10k on top, C18 |
| 1 | /TEMP_MOSFET_B | J4 NTC, R5 10k on top, C19 |
| 2 | /TEMP_COIL_A | J5 NTC, R6 10k on top, C20 |
| 3 | /TEMP_COIL_B | J6 NTC, R7 10k on top, C21 |
| 4 | /PICKUP_A | **nothing but C24 to GNDA** |
| 5 | /PICKUP_B | **nothing but C25 to GNDA** |
| 6 | /PHASE | XOR output (U3) through R20 10k, C26 0.1 uF |
| 7 | /ANALOG_SPARE | J14 SPARE through R13 1k, C27 |

SPI0: SCK GP18, MOSI GP19, MISO GP16, CS GP17. U1 Vdd = VCC, AGND = GNDA, DGND = GND, Vref = /VREF_ADC.

## Answers to the brief's checklist

- **Frequency inputs:** only one, GPIO22 (even, PWM 3A). Hardware PWM counting does not work on it, so it needs a PIO edge counter. Coil A and B squared signals (SQ_A, SQ_B) go to U3 and test points TP3/TP4 only. They do not reach any GPIO.
- **LCD:** SCL GP10, SI GP11 (SPI1), A0 GP12, /CS1 GP13, /RES GP15, backlight gate GP14. Separate SPI bus from the ADC. LCD P/S and C86 are tied to GND (serial mode), WR and RD tied to VCC.
- **Buttons:** external 10k pull-ups to VCC, active low. Not wired for pull-down, so erratum E9 does not affect them.
- **/VREF_ADC:** VCC (Pico 3V3) through R3 = 10 R, with C16 0.1 uF and C17 10 uF to GNDA. About 3.3 V, less the drop across 10 R (a few mV with the four thermistor dividers loading it). JP1..JP4 (bridged "PU CUT") connect it to the thermistor pull-ups.
- **Thermistors:** R_fix = 10k on top (to /VREF_ADC), NTC on the bottom (to GNDA). Ratiometric: $R = R_{fix}\,\frac{N}{4096-N}$.
- **Phase detector:** U3 = 74LVC1G86 (XOR) from VCC = 3.3 V. **R19 = R22 = 7.15k in the schematic** (R18 = R21 = 10k), so the bias is about 1.38 V. R20 = 10k, C26 = 0.1 uF, so $\tau = 1.0$ ms (the brief assumed 2.1 ms).
- **HV connectors:** every connector except J1 (power in) and J15 (debug) is an input to an analog or logic front end. No GPIO is an output to an HV board. No enable, gate or relay line exists.

## Differences from the brief

1. **VDD taps are on the Pico's internal ADC, not the MCP3208.** The divider is 100k/10k, so $V_{DD} = 11\,V_{pin}$ (not 9.2) and full scale is $3.3 \times 11 = 36.3$ V.
2. **Pickup coils A/B have no ADC path and no frequency path.** MCP3208 CH4/CH5 are floating. Older schematic revisions had R10/R11 (1k) feeding them, and a passive-coil frequency input R15 on GPIO9; all removed in the current revision.
3. **Passive coil:** amplitude only (peak detector into GPIO28/ADC2), no frequency.
4. **Phase filter:** $\tau = 1$ ms, so 1 LSB settling is about 8.3 ms.
5. **Pickup attenuation:** J16/J17 go through R25/R27 (10k) into R26/R28 (330 R) to GND, about 1:31 to 1:34 before the AC coupling cap and the Schmitt input.
