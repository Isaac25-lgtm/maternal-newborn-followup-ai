"""Eligibility flow and post-discharge endpoint on harmonised columns.

Inputs use concept names from ``concepts.py`` after a verified crosswalk has
been applied. Binary inputs are 1 yes / 0 no / NA (don't know, missing,
skipped). Nothing here reads raw survey files.

Clocks. The verified questionnaire wording (Rwanda 2019-20 Q442/Q446; Rwanda
2025 recode labels m67/m71) times the post-discharge check from DELIVERY, not
from discharge. The caller must state the clock of the timing columns
(``check_clock``) and the reference of the window (``window_from``); there is
no default that silently assumes one.

Per-member states:
    checked       post-discharge check within the window      -> missed 0
    missed        no post-discharge check within the window   -> missed 1
    died          newborn died after discharge, before the window ended and
                  before any check: a competing state, not a miss -> NA
    invalid_time  negative timing, or (window_from='discharge') a
                  "post-discharge" check timed before discharge   -> NA
    unknown       don't know / missing answer or timing         -> NA
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


def _to_window_reference(day: pd.Series, stay: pd.Series, check_clock: str, window_from: str) -> pd.Series:
    if check_clock == window_from:
        return day
    if check_clock == "birth":  # window from discharge
        return day - stay
    return day + stay  # discharge clock, window from birth


def _member_state(checked_after, check_day, stay, window_days, check_clock, window_from, death_day=None):
    state = pd.Series("unknown", index=checked_after.index, dtype="object")
    t = _to_window_reference(check_day, stay, check_clock, window_from)
    invalid = (checked_after == 1) & ((check_day < 0) | (t < 0))
    state[checked_after == 0] = "missed"
    state[(checked_after == 1) & (t <= window_days)] = "checked"
    state[(checked_after == 1) & (t > window_days)] = "missed"
    state[invalid] = "invalid_time"
    if death_day is not None:
        # window end and death expressed on the birth clock
        if window_from == "birth":
            window_end = pd.Series(float(window_days), index=state.index)
        else:
            window_end = stay + window_days
        died_in_window = death_day.notna() & (death_day <= window_end)
        unclear = death_day.notna() & window_end.isna()
        state[died_in_window & (state == "missed")] = "died"
        state[unclear & (state == "missed")] = "unknown"
    return state


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
    out["mother_state"] = _member_state(
        df.mother_check_after_discharge, df.mother_after_discharge_check_day, stay, window_days, check_clock, window_from
    )
    out["newborn_state"] = _member_state(
        df.newborn_check_after_discharge,
        df.newborn_after_discharge_check_day,
        stay,
        window_days,
        check_clock,
        window_from,
        death_day=df.newborn_age_at_death_days,
    )
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
