# board_rules.py -- project-specific expectations for flagcheck.py (Plasma Donut control board, Rev A).
# Every expectation carries its basis:  "ds:<part> p.N"  (cited, verified page)  |  "calc"  |  "assumed"  |  "web:<url>"
# Edit THIS file when the design changes; flagcheck.py itself stays generic.

PROJECT = "Microcontroller-PCB"

# ---------------------------------------------------------------- rails (R-C1)
# net: (nominal V, worst-case high V, basis)
RAILS = {
    "+5V": (5.0, 5.5, "ds:lm66100 p.4 (VIN rec. max 5.5 V caps what can pass to +5V)"),
    "VCC": (3.3, 3.4, "assumed: Pico 2 SMPS tolerance not given in pico2 DS; 3 % high allowance"),
    "/VREF_ADC": (3.3, 3.4, "calc: VCC through R3 10 R"),
    "GND": (0.0, 0.0, "-"), "GNDA": (0.0, 0.0, "-"),
}

# ---------------------------------------------------------------- pin limits (R-C1)
# "REF.PIN": (recommended max V, absolute max V, basis)
PIN_LIMITS = {
    "DS1.14": (3.3, 3.6, "ds:nhd_c12864lz p.7 (VDD 2.7-3.3 V); ds:st7565r p.56 (abs 3.6 V)"),
    "U1.16":  (5.5, 7.0, "ds:mcp3208 p.3 (VDD 2.7-5.5 V); p.2 (abs 7.0 V)"),
    "U1.15":  (5.5, 7.0, "ds:mcp3208 p.2 (VREF <= VDD)"),
    "U3.5":   (5.5, 6.5, "web:Nexperia 74LVC1G86 Table 6 / Table 5"),
    "U4.5":   (5.5, 6.5, "web:Nexperia 74LVC1G17 Table 6 / Table 5"),
    "U5.5":   (5.5, 6.5, "web:Nexperia 74LVC1G17 Table 6 / Table 5"),
    "U2.6":   (5.5, 6.0, "ds:lm66100 p.4"),
    "A1.39":  (5.5, 5.5, "ds:pico2 p.13 (VSYS 1.8-5.5 V)"),
}

# ---------------------------------------------------------------- pinout expectations (R-B2)
# "REF.PIN": (expected net, pin name, basis).  "=REF.PIN" means "same net as that pin".
PIN_EXPECT = {
    "U1.16": ("VCC", "VDD", "ds:mcp3208 p.15"),
    "U1.15": ("/VREF_ADC", "VREF", "ds:mcp3208 p.15"),
    "U1.14": ("GNDA", "AGND", "ds:mcp3208 p.15"),
    "U1.9":  ("GNDA", "DGND", "ds:mcp3208 p.24 ('both ... connected to the analog ground plane')"),
    "U2.3":  ("=U2.6", "CE", "ds:lm66100 p.9 (CE to VOUT = always-on reverse-current blocking)"),
    "U2.5":  ("GND", "ST", "ds:lm66100 p.3 ('Connect to GND if not required'); open-drain output, floating is benign", "warn"),
    "U2.2":  ("GND", "GND", "ds:lm66100 p.3"),
    "U3.5":  ("VCC", "VCC", "web:Nexperia 74LVC1G86 Table 3"), "U3.3": ("GND", "GND", "web:Nexperia 74LVC1G86 Table 3"),
    "U4.5":  ("VCC", "VCC", "web:Nexperia 74LVC1G17 Table 3"), "U4.3": ("GND", "GND", "web:Nexperia 74LVC1G17 Table 3"),
    "U5.5":  ("VCC", "VCC", "web:Nexperia 74LVC1G17 Table 3"), "U5.3": ("GND", "GND", "web:Nexperia 74LVC1G17 Table 3"),
    "Q1.2":  ("GND", "S", "ds:ao3400a p.1"),
    "DS1.14": ("VCC", "VDD", "ds:nhd_c12864lz p.6"), "DS1.15": ("GND", "VSS", "ds:nhd_c12864lz p.6"),
    "DS1.28": ("GND", "PS (L = serial)", "ds:nhd_c12864lz p.6"),
    "A1.36": ("VCC", "3V3", "ds:pico2 p.9"), "A1.39": ("+5V", "VSYS", "ds:pico2 p.9"),
    "A1.33": ("GNDA", "AGND", "ds:pico2 p.9"),
    "D1.1":  ("/PASSIVE_PEAK", "K (cathode)", "ds:bat54ws_mcc p.1 + KiCad D_Schottky pin 1 = K"),
}

# power-type pins that are deliberately left open
POWER_PIN_OK_UNCONNECTED = {
    "A1.35": "ADC_VREF is the Pico's filtered 3V3 output/optional reference input (ds:pico2 p.10)",
    "A1.37": "3V3_EN has an on-module 100k pull-up to VSYS (ds:pico2 p.10)",
    "A1.40": "VBUS unused: USB power enters VSYS through the on-module Schottky (ds:pico2 p.16)",
}

# ---------------------------------------------------------------- resistor stress (R-C4)
# ref: (worst-case V rms across it, basis of that voltage, note)
RESISTOR_STRESS = {
    "R1":  (2.8, "calc: 5.5 V (+5V max) - 2.7 V (VLED min, ds:nhd_c12864lz p.7)", "Firmware caps PWM duty at 75 % -> average 0.25 W."),
    "R25": (33.0, "assumed: pickup at top of design window 47 V pk (DC-08)", "Rescale per REWORK.md D if the pickup is larger."),
    "R27": (33.0, "assumed: pickup at top of design window 47 V pk (DC-08)", "Rescale per REWORK.md D if the pickup is larger."),
    "R23": (36.3, "calc: VDD tap full scale 36.3 V across ~100k", ""),
}

# ---------------------------------------------------------------- decoupling (R-C2, R-E1)
# "REF.PIN": (min capacitance F, max distance mm, basis)
DECAP = {
    "U1.16": (1e-6, 5.0, "ds:mcp3208 p.23 ('A bypass capacitor value of 1 uF is recommended')"),
    "U2.1":  (1e-6, 5.0, "ds:lm66100 p.13 (CIN 1 uF)"),
    "U3.5":  (0.1e-6, 5.0, "assumed: standard 0.1 uF logic decoupling"),
    "U4.5":  (0.1e-6, 5.0, "assumed: standard 0.1 uF logic decoupling"),
    "U5.5":  (0.1e-6, 5.0, "assumed: standard 0.1 uF logic decoupling"),
    "DS1.14": (1e-6, 5.0, "ds:nhd_c12864lz p.6 wiring diagram"),
}

# ---------------------------------------------------------------- MCU pin capabilities (R-C5)
# Raspberry Pi Pico header pin -> GPIO (ds:pico2 p.9 pinout figure; standard Pico footprint)
PICO_PIN_GPIO = {1: 0, 2: 1, 4: 2, 5: 3, 6: 4, 7: 5, 9: 6, 10: 7, 11: 8, 12: 9, 14: 10, 15: 11, 16: 12,
                 17: 13, 19: 14, 20: 15, 21: 16, 22: 17, 24: 18, 25: 19, 26: 20, 27: 21, 29: 22,
                 31: 26, 32: 27, 34: 28}
MCU_REF = "A1"
# nets that need hardware edge counting -> must be on an odd GPIO (PWM B), one per slice (ds:rp2350 p.976, p.980)
EDGE_COUNT_NETS = {"/FREQ_QUARTZ": "mitigated: GPIO22 = GPIN1 -> FC0 counter (ds:rp2350 p.19, p.476); see freq.py"}
# nets that are analog inputs to the Pico ADC -> must be GPIO26-28 (ds:pico2 p.15)
PICO_ADC_NETS = ["/VDD_TAP_A", "/VDD_TAP_B", "/PASSIVE_LEVEL"]

# ---------------------------------------------------------------- MOSFET gate hygiene (R-B5)
GATE_PULLDOWN = {"Q1.1": "GND"}      # gate must see a resistor to this net (boot-state off)

# ---------------------------------------------------------------- firmware / doc drift (R-D3)
FIRMWARE_CONFIG = "pico-firmware/src/config.py"     # relative to the CAPSTONE folder
# config constant -> expression over schematic values (calc)
DRIFT = {
    "VDD_DIV_TOP": "R23", "VDD_DIV_BOT": "R8", "VDD_DIV_RATIO": "(R23 + R8) / R8",
    "NTC_R_FIX": "R4", "PHASE_R_FILTER": "R20", "PHASE_C_FILTER": "C26",
    "PHASE_TAU_S": "R20 * C26", "SCHMITT_BIAS_V": "3.3 * R19 / (R18 + R19)",
}
# stale phrases that must not appear in living docs once the schematic changed (pattern, why)
STALE_TERMS = [
    (r"\b82\s?k", "VDD divider top is 100k (R23/R24), not 82k"),
    (r"\b9\.2\b", "VDD divider ratio is 11, not 9.2"),
    (r"2\.1\s?ms", "phase filter tau = R20*C26 = 1.0 ms, not 2.1 ms"),
]
LIVING_DOCS = ["pico-firmware/CLAUDE.md", "pico-firmware/PINMAP.md", "pico-firmware/FIXES.md",
               "Microcontroller-PCB/datasheets/design-requirements.md", "Microcontroller-PCB/datasheets/ISSUES.md",
               "Microcontroller-PCB/datasheets/REWORK.md"]

# ---------------------------------------------------------------- footprint vs ordered package (R-E3)
# ref prefix or ref -> (ordered MPN, required footprint substring, basis)
PACKAGE = {
    "U1": ("MCP3208-CI/SL", "SOIC-16", "Digi-Key order 4: /SL = 150 mil SOIC-16"),
    "U2": ("LM66100DCKR", "SC-70-6", "ds:lm66100 p.3 DCK = SC-70-6"),
    "U3": ("74LVC1G86GV,125", "74LVC1G86GV", "GV = SOT753 (SC-74A)"),
    "U4": ("74LVC1G17GV-Q100", "SOT95P275", "GV = SOT753: 0.95 pitch, 2.75 span"),
    "U5": ("74LVC1G17GV-Q100", "SOT95P275", "GV = SOT753"),
    "Q1": ("AO3400A", "SOT-23", "ds:ao3400a p.1"),
    "D1": ("BAT54WS-TP", "SOD-323", "ds:bat54ws_mcc p.1"),
    "J1": ("1715022", "MKDS-1,5-2_1x02_P5.00", "Phoenix MKDS 1,5/2 = 5.0 mm"),
    "R1": ("RC1206FR-0724RL", "R_1206", "Yageo RC1206"),
}

# ---------------------------------------------------------------- procurement status (R-F1)
# status: in_hand | in_transit | unconfirmed | none_needed
ORDER_STATUS = {
    "D1": "in_transit", "C36": "in_transit", "C37": "in_transit", "R19": "in_transit", "R22": "in_transit",
    "J1": "in_transit", "J3": "in_transit", "J4": "in_transit", "J5": "in_transit", "J6": "in_transit",
    "J9": "in_transit", "J10": "in_transit", "J11": "in_transit", "J12": "in_transit", "J14": "in_transit",
    "J16": "in_transit", "J17": "in_transit",
    "C30": "unconfirmed", "C34": "unconfirmed", "R3": "unconfirmed", "SW1": "unconfirmed", "SW2": "unconfirmed",
    "J15": "unconfirmed",
    "TP": "none_needed", "JP": "none_needed", "H": "none_needed",
}
ORDER_DEFAULT = "in_hand"
SINGLE_QTY_CRITICAL = {"DS1": "only 1 LCD bought"}

# ---------------------------------------------------------------- waivers (documented, deliberate)
WAIVERS = {
    "DRC:A1.D2": "Will deleted the A1.D2 GND trace on 2026-10-08; D2 is grounded inside the Pico",
}
