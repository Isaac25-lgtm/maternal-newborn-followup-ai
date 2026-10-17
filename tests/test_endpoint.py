import numpy as np
import pandas as pd
import pytest

from mnfollowup.endpoint import apply_eligibility, missed_followup, survivor_only_sensitivity, unit_value_to_days

ELIGIBLE = {
    "both checked within window",
    "pre-discharge checks only: still missed",
    "mother checked late newborn on time",
    "mother dont-know newborn missed",
    "mother checked timing unknown",
    "newborn died after discharge before any check",
    "negative mother timing",
    "newborn checked then died",
    "check timed before discharge on birth clock",
}


def _scored(df, window=7, clock="birth", window_from="birth"):
    eligible, _ = apply_eligibility(df, window_days=window, window_from=window_from)
    return missed_followup(eligible, window, check_clock=clock, window_from=window_from).set_index("case_note")


def test_eligibility_flow_counts_every_exclusion(synthetic_dyads):
    eligible, flow = apply_eligibility(synthetic_dyads, window_days=7)
    assert list(flow.n_excluded) == [1, 1, 1, 2, 1, 1]
    assert flow.n_in.iloc[0] == 16 and flow.n_out.iloc[-1] == 9 == len(eligible)
    assert (flow.n_in - flow.n_excluded == flow.n_out).all()
    assert set(eligible.case_note) == ELIGIBLE


def test_post_discharge_death_is_retained_not_conditioned_on(synthetic_dyads):
    eligible, flow = apply_eligibility(synthetic_dyads, window_days=7)
    assert "newborn died after discharge before any check" in set(eligible.case_note)
    assert "newborn died before discharge" not in set(eligible.case_note)
    assert flow.step.iloc[-1] == "newborn alive at discharge"


def test_missing_place_of_delivery_is_excluded_not_assumed(synthetic_dyads):
    eligible, _ = apply_eligibility(synthetic_dyads, window_days=7)
    assert "place of delivery missing" not in set(eligible.case_note)


def test_endpoint_states_birth_clock(synthetic_dyads):
    out = _scored(synthetic_dyads)
    expect = {  # mother_missed, newborn_missed, dyad, newborn_state
        "both checked within window": (0, 0, 0, "checked"),
        "pre-discharge checks only: still missed": (1, 1, 1, "missed"),
        "mother checked late newborn on time": (1, 0, 1, "checked"),
        "mother dont-know newborn missed": (np.nan, 1, 1, "missed"),
        "mother checked timing unknown": (np.nan, 0, np.nan, "checked"),
        "newborn died after discharge before any check": (0, np.nan, np.nan, "died"),
        "negative mother timing": (np.nan, 0, np.nan, "checked"),
        "newborn checked then died": (0, 0, 0, "checked"),
        "check timed before discharge on birth clock": (np.nan, 0, np.nan, "checked"),
    }
    for note, (m, n, d, ns) in expect.items():
        got = tuple(out.loc[note, ["mother_missed", "newborn_missed", "dyad_any_missed"]])
        np.testing.assert_array_equal(got, (m, n, d), err_msg=note)
        assert out.loc[note, "newborn_state"] == ns, note
    assert out.loc["negative mother timing", "mother_state"] == "invalid_time"
    assert out.loc["check timed before discharge on birth clock", "mother_flag"] == "check_before_discharge"
    assert out.loc["mother dont-know newborn missed", "mother_state"] == "unknown"


def test_discharge_window_flags_check_timed_before_discharge(synthetic_dyads):
    out = _scored(synthetic_dyads, window_from="discharge")
    row = out.loc["check timed before discharge on birth clock"]
    assert row.mother_state == "invalid_time" and np.isnan(row.mother_missed)  # day 2 < stay 3
    assert row.newborn_state == "checked"  # day 5 - stay 3 = 2 days after discharge


def test_discharge_window_without_stay_length_is_unknown(synthetic_dyads):
    df = synthetic_dyads.assign(facility_stay_days=np.nan, days_since_birth=100)
    eligible, flow = apply_eligibility(df, 7, window_from="discharge")
    assert len(eligible) == 0 and flow.n_excluded.iloc[2] > 0  # exposure cannot be confirmed
    scored = missed_followup(df, 7, check_clock="birth", window_from="discharge")
    checked = df.mother_check_after_discharge == 1
    assert scored.mother_missed[checked].isna().all()


@pytest.mark.parametrize("clock", [None, "", "delivery", "unknown", "UNVERIFIED"])
def test_ambiguous_clock_refused(synthetic_dyads, clock):
    with pytest.raises(ValueError, match="ambiguous"):
        missed_followup(synthetic_dyads, 7, check_clock=clock)


def test_survivor_only_sensitivity_is_explicit(synthetic_dyads):
    out = _scored(synthetic_dyads).reset_index()
    kept, dropped = survivor_only_sensitivity(out)
    assert dropped == 1 and len(kept) == len(out) - 1
    assert "newborn died after discharge before any check" not in set(kept.case_note)


def test_pre_discharge_check_never_counts_as_followup(synthetic_dyads):
    df = synthetic_dyads.assign(mother_check_before_discharge=1, newborn_check_before_discharge=1,
                                mother_check_after_discharge=0, newborn_check_after_discharge=0,
                                newborn_age_at_death_days=np.nan)
    out = missed_followup(df, 42, check_clock="birth")
    assert (out.dyad_any_missed == 1).all()


def test_window_changes_late_check(synthetic_dyads):
    late = synthetic_dyads[synthetic_dyads.case_note == "mother checked late newborn on time"]
    assert missed_followup(late, 7, check_clock="birth").mother_missed.iloc[0] == 1
    assert missed_followup(late, 42, check_clock="birth").mother_missed.iloc[0] == 0


def test_unit_value_to_days():
    got = unit_value_to_days(pd.Series(["hours", "days", "weeks", "dont_know", None, "days"]),
                             pd.Series([12, 3, 2, 98, 5, -1]))
    np.testing.assert_allclose(got, [0.5, 3, 14, np.nan, np.nan, np.nan])
    with pytest.raises(ValueError, match="unrecognised"):
        unit_value_to_days(pd.Series(["months"]), pd.Series([1]))


# --- chronology invariants: hand-built SYNTHETIC rows, both window clocks ---------

def _syn(**kw):
    """One SYNTHETIC_NOT_REAL dyad; mother always validly checked on day 3 after a 1-day stay."""
    row = dict(synthetic_record="SYNTHETIC_NOT_REAL", facility_stay_days=1.0,
               mother_check_after_discharge=1, mother_after_discharge_check_day=3.0,
               newborn_check_after_discharge=1, newborn_after_discharge_check_day=3.0,
               newborn_age_at_death_days=np.nan)
    row.update(kw)
    return pd.DataFrame([row])


BOTH = pytest.mark.parametrize("window_from", ["birth", "discharge"])


def _score(df, window_from, window=7):
    return missed_followup(df, window, check_clock="birth", window_from=window_from).iloc[0]


@BOTH
def test_birth_clock_check_before_known_discharge_is_invalid(window_from):
    r = _score(_syn(facility_stay_days=3.0, newborn_after_discharge_check_day=1.0), window_from)
    assert (r.newborn_state, r.newborn_flag) == ("invalid_time", "check_before_discharge")
    assert np.isnan(r.newborn_missed) and np.isnan(r.dyad_any_missed)


@BOTH
def test_check_on_discharge_day_is_valid(window_from):
    r = _score(_syn(facility_stay_days=3.0, newborn_after_discharge_check_day=3.0), window_from)
    assert r.newborn_state == "checked" and r.newborn_missed == 0


@BOTH
def test_death_before_reported_check_is_never_checked(window_from):
    r = _score(_syn(newborn_after_discharge_check_day=5.0, newborn_age_at_death_days=3.0), window_from)
    assert (r.newborn_state, r.newborn_flag) == ("inconsistent", "death_before_reported_check")
    assert np.isnan(r.newborn_missed) and np.isnan(r.dyad_any_missed)
    assert r.newborn_died_after_discharge == 1


@BOTH
def test_death_before_late_check_outside_window_is_inconsistent_not_died(window_from):
    r = _score(_syn(newborn_after_discharge_check_day=20.0, newborn_age_at_death_days=4.0), window_from)
    assert (r.newborn_state, r.newborn_flag) == ("inconsistent", "death_before_reported_check")


@BOTH
def test_valid_check_then_later_death_stays_checked_and_death_kept(window_from):
    r = _score(_syn(newborn_after_discharge_check_day=2.0, newborn_age_at_death_days=5.0), window_from)
    assert r.newborn_state == "checked" and r.newborn_missed == 0 and r.dyad_any_missed == 0
    assert r.newborn_died_after_discharge == 1


@BOTH
def test_same_day_check_and_death_order_unknown(window_from):
    r = _score(_syn(newborn_age_at_death_days=3.0), window_from)
    assert (r.newborn_state, r.newborn_flag) == ("unknown", "death_check_same_day")


@BOTH
def test_no_check_then_death_in_window_is_competing_died(window_from):
    r = _score(_syn(newborn_check_after_discharge=0, newborn_after_discharge_check_day=np.nan,
                    newborn_age_at_death_days=4.0), window_from)
    assert r.newborn_state == "died" and np.isnan(r.newborn_missed)


@BOTH
def test_death_before_discharge_is_inconsistent_even_if_marked_alive(window_from):
    r = _score(_syn(facility_stay_days=2.0, newborn_check_after_discharge=0,
                    newborn_after_discharge_check_day=np.nan, newborn_age_at_death_days=1.0), window_from)
    assert (r.newborn_state, r.newborn_flag) == ("inconsistent", "death_before_discharge")
    assert np.isnan(r.newborn_died_after_discharge)


def test_unknown_stay_with_death_discharge_window_is_unknown_not_died():
    r = _score(_syn(facility_stay_days=np.nan, newborn_check_after_discharge=0,
                    newborn_after_discharge_check_day=np.nan, newborn_age_at_death_days=4.0), "discharge")
    assert (r.newborn_state, r.newborn_flag) == ("unknown", "death_vs_window_unknown")
    # birth window does not need stay length: death day 4 <= 7 is a competing death
    assert _score(_syn(facility_stay_days=np.nan, newborn_check_after_discharge=0,
                       newborn_after_discharge_check_day=np.nan, newborn_age_at_death_days=4.0), "birth").newborn_state == "died"


def test_discharge_clock_check_with_unknown_stay_cannot_be_ordered_against_death():
    df = _syn(facility_stay_days=np.nan, newborn_after_discharge_check_day=2.0, newborn_age_at_death_days=10.0)
    r = missed_followup(df, 7, check_clock="discharge", window_from="discharge").iloc[0]
    assert (r.newborn_state, r.newborn_flag) == ("unknown", "death_check_order_unknown")


def test_death_timing_is_never_imputed():
    r = _score(_syn(newborn_check_after_discharge=0, newborn_after_discharge_check_day=np.nan), "birth")
    assert r.newborn_state == "missed" and r.newborn_died_after_discharge == 0  # NA death = alive per concept
