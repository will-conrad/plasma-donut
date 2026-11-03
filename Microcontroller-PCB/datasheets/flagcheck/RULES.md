# Internal rules for AI-assisted circuit work (Plasma Donut)

These rules apply to every future iteration of the control board and its firmware: schematic, layout, BOM, docs and code. Most of them come from documented failure modes of AI tools in hardware design (sources at the bottom), and the rest from mistakes made in this project. The checkable ones are automated in `flagcheck.py`, and `selftest.py` confirms the checker still catches planted faults.

**How to use**
1. Before and after each design pass, from the CAPSTONE folder:
   ```bash
   python3 Microcontroller-PCB/datasheets/flagcheck/flagcheck.py --capstone .
   python3 Microcontroller-PCB/datasheets/flagcheck/selftest.py --capstone .
   ```
   Then read `FLAGS.md`.
2. When the design changes, edit `board_rules.py`. It holds the expectations, and each one carries its source.
3. Work through the manual rules (marked **M** below) yourself.

---

## 0 · Claim tags: say where every number came from
Every number in a doc, review or chat answer carries exactly one tag:

| Tag | Meaning | Example |
|---|---|---|
| `(part p.N)` | **Cited.** Read from that datasheet page, and the page was opened | `VIH ≥ 2.0 V (rp2350 p.1337)` |
| `[netlist]` | **Design fact.** Read from the KiCad files or the BOM | `R23 = 100k [netlist]` |
| `[calc]` | **Computed.** The formula and inputs are shown, and the arithmetic was run in code | `I = (5.0−3.0)/24 = 83 mA [calc]` |
| `[measured]` | **Bench data.** Include instrument and date | `TP2 = 3.31 V [measured, DMM, 11/05]` |
| `[web]` | **Secondary source.** Not page-verified, so it needs confirming | Nexperia values fetched without the PDF |
| `[assumed]` | **Engineering assumption.** Must say what would confirm it | `VCC ≤ 3.4 V [assumed: SMPS tolerance not in DS]` |
| `[inferred]` | **Reasoned, not checked.** Lowest confidence | `AGND probably tied inside the Pico [inferred]` |

`flagcheck.py` reports, for each doc, what fraction of numeric lines carry a tag (rule R-A1).

---

## Rules

### A · Provenance and honesty
| ID | Rule | Why | Check |
|---|---|---|---|
| **R-A1** | Tag every number (section 0). Never present `[assumed]` or `[inferred]` as fact. | LLMs state invented values confidently (HN: "hallucinating a value that does not actually exist in the datasheet") | auto: coverage report |
| **R-A2** | A citation must point to the page where the number actually appears. Re-verify the page whenever the PDF changes. | ChatGPT "cited the datasheet" for wire colours the datasheet doesn't contain (LessWrong) | auto: each specs.csv number is checked against its page text |
| **R-A3** | Never say "per the datasheet" without having opened that PDF this session. If it's from memory, tag it `[inferred]`. | Same LessWrong transcript: it claimed a datasheet review it never did | M |
| **R-A4** | Use the **exact ordered part number**, including manufacturer and suffix (GV vs DBV, -Q100, CI/SL), and only that part's datasheet. Never a "similar" part's. | HN: LLMs insist "some related but much more common component satisfied the requirement"; they "conflate two parts". **Here:** I first used TI's SN74LVC1G17 sheet; the board has Nexperia GV parts with different thresholds | auto (package) + M |
| **R-A5** | Units and PDF-extraction sanity. Re-derive unit conversions in code. Distrust symbol-font glyphs (pdftotext turns mΩ into "mW" and µA into "mA"). | HN: "1234 µA is sub-milliampere: True". **Here:** the AO3400A text read 26.5 "mW" for 26.5 mΩ | M |

### B · Netlist and pinout
| ID | Rule | Why | Check |
|---|---|---|---|
| **R-B1** | Pin numbers and names come from structured data (KiCad netlist export, datasheet pin table), **never from memory**. | HN: Claude "happily invented pin numbers that didn't exist"; structured JSON mostly fixed it. dev.to: SCL on PB1 instead of PB2 | M + R-B2 |
| **R-B2** | Check every IC power, ground and mode pin against the datasheet pin table. | dev.to six-board review: unconnected VIN, wrong reset pin, USB connector "not wired to anything" | auto: `PIN_EXPECT` |
| **R-B3** | No floating nets. Every input has a driver, and every power pin is connected or documented as intentionally open. | **Here:** MCP3208 CH4/CH5 are fed only by a capacitor | auto |
| **R-B4** | After **any** edit, diff the netlist and confirm only the intended nets changed. | dev.to: moving SCL silently pulled ISP MISO onto the button net | M (kicad-cli netlist diff) |
| **R-B5** | Check polarity, direction and boot state: diode orientation, LED anode/cathode, inverting vs non-inverting input, MOSFET gate pull-downs, DIR pins. | tinycomputers: an LLM wrote a wrong-direction pulldown plus a misleading comment. dev.to: LED cathode on GND, "always on". JITX: "labeled non-inverting" but fed the inverting input | auto (gate pull-down) + M |

### C · Ratings and datasheet compliance
| ID | Rule | Why | Check |
|---|---|---|---|
| **R-C1** | Every pin's worst-case rail must be within recommended max (warning) and absolute max (error). Use worst-case rails, not nominal. | dev.to: a 6–12 V motor supply against the DRV8833's 10.8 V max went unflagged | auto: `RAILS` × `PIN_LIMITS` |
| **R-C2** | External parts the datasheet requires must be present with the stated value: decoupling, bias, charge-pump caps, CE/ST/EN ties. | dev.to: 1 µF used where the datasheet calls for 2.2 µF. **Here:** MCP3208 has 0.1 µF where 1 µF is recommended | auto: `DECAP` |
| **R-C3** | Don't confuse coupling and decoupling caps. Don't reflexively add a cap. | JITX: "LLMs loved to give naive advice about decoupling"; used a decoupling cap where coupling was needed | M |
| **R-C4** | Derate resistors and caps for power and voltage at worst case, against the ordered part's datasheet. | **Here:** R1 can hit 0.33 W in a 0.25 W 1206; R25 limits pickup amplitude | auto: `RESISTOR_STRESS` |
| **R-C5** | Check MCU pin capabilities and errata: which pins count edges, the ADC pins, PWM slice sharing, pull-down errata, 5 V tolerance. | dev.to: the RP2040's GPIO26_ADC0 names were unrecognised, so the pins were left unconnected. HN: Claude "circles on wrong MCU pins". **Here:** GPIO22 is even; RP2350-E9 | auto: `EDGE_COUNT_NETS`, `PICO_ADC_NETS` |

### D · Math
| ID | Rule | Why | Check |
|---|---|---|---|
| **R-D1** | Run every calculation in code (Python or ngspice). Show the formula, inputs and units. No mental arithmetic. | HN: it's "not too bad at showing you how" but "doesn't do well at actually running the calculations". dev.to: 555 values gave 0.69 Hz, not 1 Hz. **Here:** I wrote 0.26 W × 0.8 for a corner that was really 0.33 W × 0.8 | M |
| **R-D2** | Evaluate tolerance corners: supply ±10 %, part tolerances, temperature, min/max thresholds. Don't use typical values only. | JITX: models give "the 'average' application" | M |
| **R-D3** | Keep a single source of truth. Firmware constants and docs must match the schematic, and stale values are flagged. | **Here:** the brief still says 82k/÷9.2 and τ = 2.1 ms, but the schematic is 100k/÷11 and τ = 1.0 ms | auto: `DRIFT`, `STALE_TERMS` |

### E · Layout and fabrication
| ID | Rule | Why | Check |
|---|---|---|---|
| **R-E1** | Decoupling caps sit within 5 mm of their pin and are placed physically. A net label alone doesn't count. | Will's rule; diode reviewer checks decoupling placement | auto: distance from the PCB |
| **R-E2** | Zero DRC errors is necessary but **not sufficient**. Treat unrouted nets as errors, record waivers with a reason, and cross-check with the fab's DFM. | tinycomputers: "Never trust a single tool's DRC as authoritative". dev.to: "five were routed with zero DRC errors, but four still had pin-level mistakes"; Gerbers were exported with unrouted nets | auto: ERC/DRC/parity + `WAIVERS` |
| **R-E3** | Each footprint must match the **ordered** package (pitch, pin 1, variant). | dev.to: a 10 nF cap on an electrolytic footprint; a BOM connector from a different maker than its land pattern | auto: `PACKAGE` |

### F · BOM and procurement
| ID | Rule | Why | Check |
|---|---|---|---|
| **R-F1** | Every BOM line has a status: in hand, in transit, unconfirmed, or none needed. "Probably ordered" counts as **unconfirmed**. | **Here:** the "Additions" sheet was never confirmed as submitted | auto: `ORDER_STATUS` |
| **R-F2** | Note single-quantity critical parts and keep spares where it's cheap. | **Here:** only one LCD was bought | auto (info) |

### G · Process
| ID | Rule | Why | Check |
|---|---|---|---|
| **R-G1** | Review read-only first, then edit separately with backups. A human signs off. | diode: the reviewer is read-only, and "if there is no evidence, there is no report"; AllSpice: "Engineers always make the final call" | M |
| **R-G2** | Every finding carries evidence: net, pin, page, number. No evidence, no flag. | diode, AllSpice ("Every comment is inspectable") | auto (report format) |
| **R-G3** | Close the loop with an external verifier (ERC/DRC, SPICE, bench measurements), and **verify the verifier** with planted faults. | HN: "hallucination gets much worse when the loop has no external verifier" | auto: `selftest.py` |
| **R-G4** | Time-box debugging. If fixes stop converging, stop and propose a workaround. | tinycomputers: "Six hours on the clearance bug should have been two" | M |
| **R-G5** | Check against *this* project's requirements, not the generic "average application". | JITX: models default to datacenter assumptions | M |
| **R-G6** | Run deterministic checks for anything rule-based. LLM review is only for judgement calls, and runs twice if it matters. | AllSpice DRCY: "LLM outputs are nondeterministic" | auto |

---

## Mistakes already made in this project (keep adding)
| Date | What went wrong | Rule |
|---|---|---|
| 11/01 | Used TI SN74LVC1G17 thresholds when the board has Nexperia 74LVC1G17GV-Q100 | R-A4 |
| 11/01 | The firmware brief (82k, ÷9.2, τ = 2.1 ms) drifted from the schematic (100k, ÷11, τ = 1.0 ms) | R-D3 |
| 11/01 | AO3400A text showed "mW"/"mA" for mΩ/µA (PDF glyphs) | R-A5 |
| 11/01 | The BOM table said "H1–H4" (4 holes); the PCB has 2 | R-B1 |
| 11/01 | The R1 duty-cap example used the wrong corner (0.26 W instead of 0.33 W) | R-D1 |
| 11/01 | A pickup-scaling table listed "6–17 V" when that option's window is 8.6–24 V | R-D1 |
| 11/01 | The first rework-map overlay used assumed coordinates; I fixed it after viewing the render | R-G3 |
| 11/01 | The first ERC run showed 285 "violations": all library-path warnings, not design errors | R-E2 |

## Sources
- JITX, "Testing Generative AI for Circuit Board Design": https://blog.jitx.com/jitx-corporate-blog/testing-generative-ai-for-circuit-board-design
- AllSpice, "Using AI in schematic design reviews": https://www.allspice.io/post/using-ai-in-schematic-design-reviews-what-we-learned-and-what-surprised-us
- AllSpice, DRCY paper (arXiv 2603.15672): https://arxiv.org/html/2603.15672
- diode, "Hardware review": https://blog.diode.computer/hardware-review
- "What routing 314 nets taught me about AI-assisted PCB design": https://tinycomputers.io/posts/what-routing-314-nets-taught-me-about-ai-assisted-pcb-design.md
- "I Asked an AI to Design Six PCBs. Here's What a Pin-by-Pin Review Found" (dev.to): https://dev.to/dibyaprakash_pradhan/i-asked-an-ai-to-design-six-pcbs-heres-what-a-pin-by-pin-review-found-2i2e
- Hacker News, "Ask HN: Why is ChatGPT so bad at electronics?": https://news.ycombinator.com/item?id=41679459
- Hacker News thread on Claude + SPICE + oscilloscope via MCP: https://hn.svelte.dev/item/47801255
- LessWrong, "Testing ChatGPT's Performance in Engineering": https://www.lesswrong.com/posts/RsvKae3KSXEaivpgJ/transcript-testing-chatgpt-s-performance-in-engineering
- pcbGPT (arXiv 2606.01188), validator categories: https://arxiv.org/html/2606.01188v1

*Search coverage:* I found no LinkedIn posts with concrete examples. Two Reddit threads (r/arduino "ChatGPT cannot be trusted", r/PrintedCircuitBoard) couldn't be fetched, so the community evidence comes from Hacker News, dev.to and engineering blogs instead.
