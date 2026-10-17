"""Eligibility flow and post-discharge endpoint on harmonised columns.

Inputs use concept names from ``concepts.py`` after a verified crosswalk has
been applied. Binary inputs are 1 yes / 0 no / NA (don't know, missing,
skipped). Nothing here reads raw survey files.

Clocks. The verified questionnaire wording (Rwanda 2019-20 Q442/Q446; Rwanda
2025 recode labels m67/m71) times the post-discharge check from DELIVERY, not
from discharge. The caller must state the clock of the timing columns
(``check_clock``) and the reference of the window (``window_from``); there is
no default that silently assumes one.

Per-member states (all chronology compared on the birth clock; no death or
check time is ever imputed):
    checked       valid post-discharge check within the window   -> missed 0
    missed        no post-discharge check within the window      -> missed 1
    died          newborn died after discharge, before the window ended, with
                  no valid check before death: competing state   -> NA
    invalid_time  negative time, or a "post-discharge" check timed before the
                  known discharge time (whatever ``window_from`` is) -> NA
    inconsistent  chronology contradicts itself: death before discharge, or
                  death before a reported check                  -> NA
    unknown       don't know / missing answer, timing, stay length needed for a
                  conversion, or check/death order undeterminable -> NA
``<member>_flag`` names the reason for invalid_time / inconsistent / unknown
chronology. A valid check before a later death stays ``checked``; the death is
kept separately in ``newborn_died_after_discharge``.
A check before discharge never counts as post-discharge follow-up.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

CLOCKS = ("birth", "discharge")
_UNIT_DAYS = {"hours": 1 / 24, "days": 1.0, "weeks": 7.0}


def unit_value_to_days(unit: pd.Series, value: pd.Series) -> pd.Series:
    """Convert the questionnaire's (unit, number) timing to days.

    Units are the questionnaire's HOURS / DAYS / WEEKS as lowercase strings; the
    numeric recode encoding of units is NOT assumed here. Don't-know or missing
    gives NA; a negative number gives NA; an unrecognised unit raises.
    """
    unit = pd.Series(unit, dtype="object")
    value = pd.to_numeric(pd.Series(value), errors="coerce")
    bad = set(unit.dropna()) - set(_UNIT_DAYS) - {"dont_know"}
    if bad:
        raise ValueError(f"unrecognised timing unit(s) {sorted(bad)}")
    days = value * unit.map(_UNIT_DAYS).astype("float64")
    return days.where(days >= 0)


def apply_eligibility(
    df: pd.DataFrame, window_days: int, *, window_from: str = "birth", recall_days: int = 730
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (eligible dyads, exclusion flow). Missing values exclude, and are counted.

    Survival is conditioned on only up to discharge. Newborns who die after
    discharge stay in the cohort and are handled as a competing state by
    ``missed_followup``.
    """
    if window_from not in CLOCKS:
        raise ValueError(f"window_from must be one of {CLOCKS}")
    if window_from == "birth":
        exposure = ("full window elapsed (birth + W)", lambda d: d.days_since_birth >= window_days)
    else:
        exposure = (
            "full window elapsed (discharge + W; needs stay length)",
            lambda d: d.days_since_birth >= d.facility_stay_days + window_days,
        )
    steps = [
        ("most recent birth", lambda d: d.is_most_recent_birth == 1),
        (f"birth within {recall_days} days of interview", lambda d: d.days_since_birth <= recall_days),
        exposure,
        ("facility delivery", lambda d: d.facility_delivery == 1),
        ("singleton birth (multiples excluded from primary)", lambda d: d.multiple_birth == 0),
        ("newborn alive at discharge", lambda d: d.newborn_alive_at_discharge == 1),
    ]
    flow = []
    cur = df
    for label, rule in steps:
        keep = rule(cur).fillna(False).astype(bool)
        flow.append({"step": label, "n_in": len(cur), "n_excluded": int((~keep).sum()), "n_out": int(keep.sum())})
        cur = cur[keep]
    return cur.copy(), pd.DataFrame(flow)


def _member_state(checked_after, check_day, stay, window_days, check_clock, window_from, death_day=None):
    """Return (state, flag) Series for one member."""
    idx = checked_after.index
    state = pd.Series("unknown", index=idx, dtype="object")
    flag = pd.Series("", index=idx, dtype="object")
    # the check on both clocks; NA when the conversion needs an unknown stay
    if check_clock == "birth":
        t_birth, t_discharge = check_day, check_day - stay
    else:
        t_birth, t_discharge = check_day + stay, check_day
    t = t_birth if window_from == "birth" else t_discharge
    checked = checked_after == 1

    state[checked_after == 0] = "missed"
    state[checked & (t <= window_days)] = "checked"
    state[checked & (t > window_days)] = "missed"
    flag[checked & check_day.notna() & t.isna()] = "clock_conversion_needs_stay"
    before_discharge = checked & (check_day >= 0) & (t_discharge < 0)
    state[before_discharge] = "invalid_time"
    flag[before_discharge] = "check_before_discharge"
    negative = checked & (check_day < 0)
    state[negative] = "invalid_time"
    flag[negative] = "negative_time"

    if death_day is not None:
        known = death_day.notna()
        window_end = pd.Series(float(window_days), index=idx) if window_from == "birth" else stay + window_days
        valid_check = checked & state.isin(["checked", "missed"])
        # no valid check before the window closed, and death inside the window
        died = known & (death_day <= window_end) & (state == "missed")
        state[died] = "died"
        unclear = known & window_end.isna() & (state == "missed")
        state[unclear] = "unknown"
        flag[unclear] = "death_vs_window_unknown"
        order_unknown = known & valid_check & t_birth.isna()
        state[order_unknown] = "unknown"
        flag[order_unknown] = "death_check_order_unknown"
        same_day = known & valid_check & (death_day == t_birth)
        state[same_day] = "unknown"
        flag[same_day] = "death_check_same_day"
        death_first = known & checked & (death_day < t_birth) & ~negative
        state[death_first] = "inconsistent"
        flag[death_first] = "death_before_reported_check"
        before_dc = known & (death_day < stay)
        state[before_dc] = "inconsistent"
        flag[before_dc] = "death_before_discharge"
    return state, flag


def missed_followup(df: pd.DataFrame, window_days: int, *, check_clock: str, window_from: str = "birth") -> pd.DataFrame:
    """Add per-member states, 1/0/NA missed flags and the dyad endpoint.

    ``check_clock`` is the reference of the *_after_discharge_check_day columns
    for this survey (from the crosswalk ``timing_reference``). Converting
    between clocks needs ``facility_stay_days``; if it is missing the result is
    unknown, not assumed.
    """
    for name, val in (("check_clock", check_clock), ("window_from", window_from)):
        if val not in CLOCKS:
            raise ValueError(f"{name}={val!r} is ambiguous; must be one of {CLOCKS}")
    stay = df.facility_stay_days if "facility_stay_days" in df else pd.Series(np.nan, index=df.index)
    out = df.copy()
    out["mother_state"], out["mother_flag"] = _member_state(
        df.mother_check_after_discharge, df.mother_after_discharge_check_day, stay, window_days, check_clock, window_from
    )
    out["newborn_state"], out["newborn_flag"] = _member_state(
        df.newborn_check_after_discharge,
        df.newborn_after_discharge_check_day,
        stay,
        window_days,
        check_clock,
        window_from,
        death_day=df.newborn_age_at_death_days,
    )
    death = df.newborn_age_at_death_days
    died_after = pd.Series(np.nan, index=df.index, dtype="float64")
    died_after[death.isna()] = 0.0
    died_after[death.notna() & (death >= stay)] = 1.0
    out["newborn_died_after_discharge"] = died_after  # NA if death timing vs discharge unknown or contradictory
    code = {"checked": 0.0, "missed": 1.0}
    out["mother_missed"] = out.mother_state.map(code).astype("float64")
    out["newborn_missed"] = out.newborn_state.map(code).astype("float64")
    m, n = out.mother_missed, out.newborn_missed
    dyad = pd.Series(np.nan, index=df.index, dtype="float64")
    dyad[(m == 1) | (n == 1)] = 1.0
    dyad[(m == 0) & (n == 0)] = 0.0
    out["dyad_any_missed"] = dyad
    return out


def survivor_only_sensitivity(scored: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Explicit sensitivity analysis: drop dyads whose newborn died after discharge
    before follow-up. Returns (subset, number dropped); never used for the primary cohort."""
    died = scored.newborn_state == "died"
    return scored[~died].copy(), int(died.sum())
