# sensors.py -- conversions from raw codes to engineering units. Pure Python, no `machine`,
# so it runs under pytest on the Mac. Every formula is derived in
# docs/design-requirements.md (DC-xx noted per function).
import math

try:
    import config as C
except ImportError:  # pragma: no cover
    from . import config as C

NTC_OK, NTC_OPEN, NTC_SHORT = "ok", "open", "short"


def ntc_temp_c(code, r_fix=C.NTC_R_FIX, r0=C.NTC_R0, t0_k=C.NTC_T0_K, beta=C.NTC_BETA):
    """DC-05. 10k on top (from /VREF_ADC), NTC on the bottom -> ratiometric:
    R = r_fix * N / (4096 - N);  1/T = 1/T0 + ln(R/R0)/B.
    Returns (temp_C or None, status). Open cable reads ~4095, short ~0 (ISSUES #15)."""
    if code >= C.NTC_OPEN_CODE:
        return None, NTC_OPEN
    if code <= C.NTC_SHORT_CODE:
        return None, NTC_SHORT
    r = r_fix * code / (4096 - code)
    inv_t = 1.0 / t0_k + math.log(r / r0) / beta
    return 1.0 / inv_t - 273.15, NTC_OK


def pico_adc_volts(code12, vref=C.PICO_ADC_VREF):
    """RP2350 ADC, 12-bit code (read_u16() >> 4)."""
    return code12 * vref / 4095


def vdd_from_code(code12, gain=1.0):
    """DC-07. 100k/10k divider -> V_DD = 11 * V_pin, times the per-channel gain calibration
    (covers ADC_VREF offset, resistor tolerance and any residual ADC loading)."""
    return pico_adc_volts(code12) * C.VDD_DIV_RATIO * gain


def passive_coil_vpk(code12, gain=1.0):
    """DC-12. Peak detector: V_C38 ~= k * Vpk - VF  ->  Vpk ~= (V_pin + VF) / k.
    Returns None when the pin voltage is below the diode-dominated region (< ~10 V pk)."""
    v = pico_adc_volts(code12)
    if v < C.PASSIVE_MIN_VALID_V:
        return None
    return (v + C.PASSIVE_D1_VF) / C.PASSIVE_DIV_K * gain


def phase_deg(code12, phi0_deg=0.0, v_logic=C.V_LOGIC, v_ref=C.V_REF_NOM):
    """DC-09. XOR averaged by R20/C26: V = V_logic * phi/180.  ADC measures against /VREF_ADC
    (VCC through 10 R, <= 14 mV low -> <= 0.8 deg). Result is a magnitude 0..180 deg, minus the
    zero-phase calibration phi0 (ISSUES #11)."""
    v = code12 * v_ref / 4096
    phi = 180.0 * v / v_logic - phi0_deg
    return max(0.0, min(180.0, phi))


def oscillating(freq_hz, nominal=C.OSC_NOMINAL_HZ, tol=C.OSC_TOL):
    return freq_hz is not None and abs(freq_hz - nominal) <= tol * nominal


def amplitude_mismatch(vdd_a, vdd_b, frac=0.15):
    """Flag for the '?' next to phase (brief): unequal coil drive skews the Schmitt edges."""
    if vdd_a is None or vdd_b is None:
        return True
    hi = max(vdd_a, vdd_b)
    return hi > 0 and abs(vdd_a - vdd_b) / hi > frac
