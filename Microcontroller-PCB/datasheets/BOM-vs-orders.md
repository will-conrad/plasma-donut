# BOM vs parts orders

**Inputs:**
- BOM: `kicad-cli sch export bom` on `Microcontroller-PCB.kicad_sch` (2026-10-22)
- Order sheets in `CAPSTONE/Parts Orders/`:
  - **O4** = `PlasmaDonut-PartsOrder3.xlsx` (submitted for the Sep 29 order 4; Digi-Key week-04 parts arrived around Oct 8)
  - **ADD** = `PlasmaDonut-PartsOrder-Additions.xlsx` (Sep 29). It has **no stock or price columns filled**, so it's unclear whether it was ever submitted.
  - **O8** = `Plasma Bagel-PartsOrder8.xlsx` (Oct 27–28). Course email on 10/30: "The Digikey order from last week is very delayed".
- Course email 10/28 (Prof. Crockett): BAT54WS-7-F was back-ordered, so O8 lists the MCC **BAT54WS-TP** instead.

**Status key:** ✅ ordered and should be in hand · 🚚 on order 8 (in transit, delayed) · ❓ only on the Additions sheet, check the bin · — no part needed

| Ref | Qty | Value / function | Ordered MPN | Sheet | Ordered qty | Status | Notes |
|---|---|---|---|---|---|---|---|
| A1 | 1 | Raspberry Pi Pico 2 | SC1631 | O4 | 2 | ✅ | 1 spare |
| U1 | 1 | MCP3208 SOIC-16 | MCP3208-CI/SL | O4 | 2 | ✅ | + 1× MCP3208-CI/P (DIP) spare; C grade (INL ±2 LSB) |
| U2 | 1 | LM66100 | LM66100DCKR | O4 | 2 | ✅ | |
| U3 | 1 | XOR | 74LVC1G86GV,125 (Nexperia) | O4 | 3 | ✅ | 2 spare |
| U4, U5 | 2 | Schmitt buffer | 74LVC1G17GV-Q100,1 (Nexperia) | O4 | 3 | ✅ | 1 spare |
| Q1 | 1 | AO3400A | AO3400A | O4 | 2 | ✅ | |
| DS1 | 1 | LCD | NHD-C12864LZ-FSW-FBW-3V3 | O4 | 1 | ✅ | **no spare** |
| D1 | 1 | Schottky | BAT54WS-TP (MCC) | O8 | 10 | 🚚 | -7-F back-ordered; 9 spare once here |
| C1, C4–C13 | 11 | 1 µF X7R 25 V 0805 | C0805C105K3RACTU | O4 | 50 | ✅ | |
| C2, C17 | 2 | 10 µF X7R 35 V 1206 | CL31B106KLHNNNE | O4 | 10 | ✅ | |
| C3, C15, C16, C18–C27, C32, C33, C35, C38, C28, C29 | 19 | 0.1 µF X7R 0805 | CL21B104KBCNNNC | O4 | 50 | ✅ | + 10× C0805C104J5RACTU (Brennan, O8) |
| C30, C34 | 2 | 1 nF C0G 0805 | C0805C102J5GACTU | ADD | 10 | ❓ | Fallbacks: C323C102KAG5TA 1 nF radial (O8), GRM1885C1H103JA01D 10 nF 0603 (O8) |
| C36 | 1 | 10 pF C0G (≥250 V) | C0805C100JCGACTU (500 V) | O8 | 5 | 🚚 | |
| C37 | 1 | 330 pF C0G | C0805C331G5GACTU | O8 | 5 | 🚚 | |
| R1 | 1 | 24 Ω 1206 | RC1206FR-0724RL | O4 | 10 | ✅ | |
| R2, R23, R24, R30 | 4 | 100k | RC0805FR-07100KL | O4 | 25 | ✅ | 82k (RC0805FR-0782KL, ADD) not needed: the schematic now uses 100k (÷11) |
| R3 | 1 | 10 Ω | RC0805FR-0710RL | ADD | 10 | ❓ | Fallback: solder bridge (DC-04) |
| R4–R9, R16–R18, R20, R21, R25, R27, R31 | 14 | 10k | RC0805FR-0710KL | O4 | 50 | ✅ | + 10× SG73P1JTTD1002F (O8) |
| R13, R29 | 2 | 1k | RC0805FR-071KL | O4 | 15 | ✅ | 13 spare (useful for ISSUES #4/#6) |
| R14, R26, R28 | 3 | 330 Ω | RC0805FR-07330RL | O4 | 25 | ✅ | |
| R19, R22 | 2 | 7.15k | RC0805FR-077K15L | O8 | 10 | 🚚 | Fallback: 10k (bias 1.65 V) |
| J1, J3–J6, J9–J12, J14, J16, J17 | 12 | 2-pos 5.0 mm screw terminal | 1715022 (Phoenix MKDS 1,5/2) | O8 | 14 | 🚚 | Footprint is MKDS-1,5-2 P5.00 ✅. The JST XH parts on ADD **don't fit** this footprint |
| J15 | 1 | 1×14 2.54 mm header | PRPC014SAAN-RC | ADD | 2 | ❓ | Any 0.1" header strip works |
| SW1, SW2 | 2 | 6 mm tactile | B3F-1000 | ADD | 4 | ❓ | |
| TP1–TP8 | 8 | THT test pads (Ø1.0 mm drill) | (Keystone 4952 hooks on O8, Brennan) | O8 | 10 | 🚚/— | Pads also work bare or with a wire loop |
| JP1–JP4 | 4 | solder jumpers | — | — | — | — | copper only |
| (holes) | 2 | M3 mounting holes | hardware | — | — | — | |
| (off-board) | 4 | NTC 10k | NTCS0603E3103FLT | O4 | 10 | ✅ | 6 spare |
| (tool) | 1 | Pi Debug Probe | SC0889 | O4 | 1 | ✅ | for J15 SWD |

## Ordered but not on the control board
- **HV boards (Brennan / Alexis):** IPB17N25S3100ATMA1, UCC27614DR, LFSPXO025876 (13.56 MHz **5 V** HCMOS oscillator, which drives J9, see ISSUES #6), Si5351 board, LM2576S-12, MBR360, IRF530N, NE555, HV caps, AJ20-4 trimmer, and others
- **O4:** 105-0752/0753 barrel jacks (the board uses a screw terminal for J1), ZS1052/ATB322524 (spark board)
- **ADD:** JST XH headers, housings and crimps (superseded by the screw terminals), and 82k resistors (superseded by 100k)

## What this means right now
- If order 8 is still in transit, you can't populate the screw terminals, the 7.15k resistors or the passive-coil detector. Every one has a stop-gap in ISSUES #1.
- Before soldering, check the parts bin for the four ❓ lines (1 nF C0G, 10 Ω, B3F switches, header).
