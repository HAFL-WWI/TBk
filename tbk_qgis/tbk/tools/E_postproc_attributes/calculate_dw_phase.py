# *************************************************************************** #
# Dauerwald-Ueberfuehrungsphase (nach Schuetz) per stand: DW_Phase and its a/b/c Zusatz.
#
# Pure logic (no QGIS processing boilerplate), see tool_calc_dw_phase.py for the algorithm.
# Mirrors the "TBk Dauerwaldcode" / "TBk Dauerwaldcode Zusatz abc" layer expressions of
# resources/TBk_Template.qgz (and auxiliary_ressources/tbk_dauerwald_if-clause.py, v5 + a/b/c) -
# keep them in sync when changing thresholds.
#
# Authors: Hannes Horneber (BFH-HAFL)
# *************************************************************************** #

# Attributes the calculation needs (DG_ks is only used for labels, not the phase itself)
REQUIRED_FIELDS = ['VegZone_Code', 'NH', 'hdom', 'DG_os', 'DG_ueb', 'DG_ms', 'DG_us']

# hdom thresholds [m] per vegetation height zone group and NH (coniferous, NH > 50) / LH (deciduous):
# (phase: hdom >= this gets a phase 0-5, else Jungwald -1/-2/-3,
#  jung_1: hdom > this -> -1, jung_2: hdom > this -> -2, else -3,
#  abc_b: hdom >= this -> 'b', abc_c: hdom >= this -> 'c', else 'a')
DW_THRESHOLDS = {
    # Kollin / Submontan / Untermontan (KL, SM, UM) + no/other category
    'KL': {'NH': (26, 18, 10, 33, 38), 'LH': (23, 16, 9, 29, 33)},
    # Obermontan
    'OM': {'NH': (23, 16, 9, 29, 33), 'LH': (19, 13, 7, 23, 29)},
    # Hochmontan
    'HM': {'NH': (19, 13, 7, 23, 29), 'LH': (16, 11, 6, 19, 23)},
    # Subalpin
    'SA': {'NH': (16, 11, 6, 19, 23), 'LH': (13, 9, 5, 16, 19)},
}


def _ge(a, b):
    """a >= b with QGIS expression NULL semantics (NULL comparison -> false)"""
    return a is not None and a >= b


def _gt(a, b):
    """a > b with QGIS expression NULL semantics (NULL comparison -> false)"""
    return a is not None and a > b


def _add(a, b):
    """a + b with QGIS expression NULL semantics (NULL + x -> NULL)"""
    return None if a is None or b is None else a + b


def veg_zone_group(veg_zone_code):
    """
    Map VegZone_Code to the threshold group. Like the template expression, anything not listed
    (including NULL) falls through to Subalpin.
    """
    if veg_zone_code in (-1, 0, 1, 2, 4, 5):
        return 'KL'
    if veg_zone_code in (6, 7):
        return 'OM'
    if veg_zone_code == 8:
        return 'HM'
    return 'SA'


def calc_dw_phase(veg_zone_code, nh, hdom, dg_os, dg_ueb, dg_ms, dg_us):
    """
    Returns (dw_phase, dw_phase_abc):
    - dw_phase: -3/-2/-1 Jungwald (Vorbereitung), 0 Stabilisierung, 1 Nachwuchsfoerderung,
      2 Strukturierung, 3 Gleichgewicht, 4 Struktur geht verloren (zuviel MS),
      5 Struktur geht verloren (zuwenig OS)
    - dw_phase_abc: 'a'/'b'/'c' hdom stage for phases 0-5, None for Jungwald

    NULL inputs behave like in the QGIS expression (comparisons with NULL are false), so results
    are identical to the template layer symbology.
    """
    nh_lh = 'NH' if _gt(nh, 50) else 'LH'
    thr_phase, thr_jung_1, thr_jung_2, thr_b, thr_c = DW_THRESHOLDS[veg_zone_group(veg_zone_code)][nh_lh]

    if not _ge(hdom, thr_phase):
        # Jungwald
        if _gt(hdom, thr_jung_1):
            return -1, None
        if _gt(hdom, thr_jung_2):
            return -2, None
        return -3, None

    if not _ge(_add(dg_os, dg_ueb), 45):
        phase = 5
    elif _ge(dg_ms, 35):
        phase = 4
    elif _ge(dg_ms, 25):
        phase = 3 if _ge(dg_us, 20) else 2
    elif _ge(dg_ms, 15):
        phase = 2 if _ge(dg_us, 10) else 1
    else:
        phase = 1 if _ge(dg_us, 10) else 0

    if _ge(hdom, thr_c):
        abc = 'c'
    elif _ge(hdom, thr_b):
        abc = 'b'
    else:
        abc = 'a'

    return phase, abc
