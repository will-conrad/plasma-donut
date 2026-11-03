# Host tests (pytest) for the conversion math. Run from pico-firmware/:  python3 -m pytest tests/host
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import config as C          # noqa: E402
import sensors as S         # noqa: E402
import cal                  # noqa: E402


def code_for_r(r):
    return round(4096 * r / (r + C.NTC_R_FIX))


def test_ntc_25c():
    t, st = S.ntc_temp_c(2048)
    assert st == S.NTC_OK and abs(t - 25.0) < 0.05


def test_ntc_100c():
    r100 = 10_000 * math.exp(3435 * (1 / 373.15 - 1 / 298.15))   # ~987 ohm
    t, st = S.ntc_temp_c(code_for_r(r100))
    assert st == S.NTC_OK and abs(t - 100.0) < 0.5


def test_ntc_faults():
    assert S.ntc_temp_c(4095) == (None, S.NTC_OPEN)
    assert S.ntc_temp_c(0) == (None, S.NTC_SHORT)


def test_vdd_ratio_11():
    # 24 V on the tap -> 24/11 = 2.18 V at the pin
    code = round(24 / 11 / 3.3 * 4095)
    assert abs(S.vdd_from_code(code) - 24.0) < 0.05
    assert abs(S.vdd_from_code(4095) - 36.3) < 1e-6


def test_vdd_gain_cal():
    measured = S.vdd_from_code(2000)
    g = cal.gain_from_reference(measured, measured * 1.02)
    assert abs(S.vdd_from_code(2000, g) / measured - 1.02) < 1e-9


def test_phase_range_and_cal():
    assert S.phase_deg(0) == 0.0
    assert abs(S.phase_deg(2048) - 90.0) < 0.1
    assert S.phase_deg(4095) <= 180.0
    assert abs(S.phase_deg(2048, phi0_deg=10.0) - 80.0) < 0.1


def test_passive_peak():
    assert S.passive_coil_vpk(0) is None
    # 60 V pk -> k*60 - 0.24 = 1.474 V at the pin
    v = (C.PASSIVE_DIV_K * 60 - C.PASSIVE_D1_VF)
    code = round(v / 3.3 * 4095)
    assert abs(S.passive_coil_vpk(code) - 60) < 0.5


def test_oscillating_window():
    assert S.oscillating(13_560_000)
    assert S.oscillating(13_560_000 * 1.049)
    assert not S.oscillating(13_560_000 * 1.06)
    assert not S.oscillating(None)


def test_config_fixes():
    assert 4 not in C.MCP_CH_ENABLED and 5 not in C.MCP_CH_ENABLED     # ISSUES #5
    assert C.BL_MAX_DUTY <= 0.75                                         # ISSUES #7
    assert C.PICO_ADC_MIN_GAP_MS >= 5                                    # ISSUES #8
    assert C.VDD_DIV_RATIO == 11.0
