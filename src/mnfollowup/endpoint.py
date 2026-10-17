"""Eligibility flow and post-discharge endpoint on harmonised columns.

Inputs use concept names from ``concepts.py`` after a verified crosswalk has
been applied. Binary inputs are 1 yes / 0 no / NA (don't know, missing,
skipped). Nothing here reads raw survey files.

Endpoint (per member, window W days): 1 = no post-discharge check within W,
0 = a post-discharge check within W, NA = unknown. A check before discharge
never counts as post-discharge follow-up.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_eligibility(df: pd.DataFrame, window_days: int, *, recall_days: int = 730) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (eligible dyads, exclusion flow). Missing values exclude, and are counted."""
    steps = [
        ("most recent birth", lambda d: d.is_most_recent_birth == 1),
        (f"birth within {recall_days} days of interview", lambda d: d.days_since_birth <= recall_days),
        (f"full {window_days}-day exposure before interview", lambda d: d.days_since_birth >= window_days),
        ("facility delivery", lambda d: d.facility_delivery == 1),
        ("singleton birth (multiples excluded from primary)", lambda d: d.multiple_birth == 0),
        ("newborn alive at window end", lambda d: d.child_alive_at_window_end == 1),
    ]
    flow = []
    cur = df
    for label, rule in steps:
        keep = rule(cur).fillna(False).astype(bool)
        flow.append({"step": label, "n_in": len(cur), "n_excluded": int((~keep).sum()), "n_out": int(keep.sum())})
        cur = cur[keep]
    return cur.copy(), pd.DataFrame(flow)


def _member_missed(checked_after: pd.Series, check_day: pd.Series, window_days: int) -> pd.Series:
    out = pd.Series(np.nan, index=checked_after.index, dtype="float64")
    out[checked_after == 0] = 1.0
    within = (checked_after == 1) & (check_day <= window_days)
    beyond = (checked_after == 1) & (check_day > window_days)
    out[within] = 0.0
    out[beyond] = 1.0
    return out  # checked_after == 1 with unknown timing stays NA


def missed_followup(df: pd.DataFrame, window_days: int) -> pd.DataFrame:
    """Add mother_missed, newborn_missed, dyad_any_missed (Kleene OR) columns."""
    out = df.copy()
    out["mother_missed"] = _member_missed(df.mother_check_after_discharge, df.mother_after_discharge_check_day, window_days)
    out["newborn_missed"] = _member_missed(df.newborn_check_after_discharge, df.newborn_after_discharge_check_day, window_days)
    m, n = out.mother_missed, out.newborn_missed
    dyad = pd.Series(np.nan, index=df.index, dtype="float64")
    dyad[(m == 1) | (n == 1)] = 1.0
    dyad[(m == 0) & (n == 0)] = 0.0
    out["dyad_any_missed"] = dyad
    return out
