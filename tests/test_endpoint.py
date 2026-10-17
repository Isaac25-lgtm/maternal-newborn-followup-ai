import numpy as np

from mnfollowup.endpoint import apply_eligibility, missed_followup


def test_eligibility_flow_counts_every_exclusion(synthetic_dyads):
    eligible, flow = apply_eligibility(synthetic_dyads, window_days=7)
    assert list(flow.n_excluded) == [1, 1, 1, 2, 1, 1]
    assert flow.n_in.iloc[0] == 12 and flow.n_out.iloc[-1] == 5 == len(eligible)
    assert (flow.n_in - flow.n_excluded == flow.n_out).all()
    assert set(eligible.case_note) == {
        "both checked within window",
        "pre-discharge checks only: still missed",
        "mother checked late newborn on time",
        "mother dont-know newborn missed",
        "mother checked timing unknown",
    }


def test_missing_place_of_delivery_is_excluded_not_assumed(synthetic_dyads):
    eligible, _ = apply_eligibility(synthetic_dyads, window_days=7)
    assert "place of delivery missing" not in set(eligible.case_note)


def test_endpoint_logic(synthetic_dyads):
    eligible, _ = apply_eligibility(synthetic_dyads, window_days=7)
    out = missed_followup(eligible, window_days=7).set_index("case_note")
    expect = {
        "both checked within window": (0, 0, 0),
        "pre-discharge checks only: still missed": (1, 1, 1),
        "mother checked late newborn on time": (1, 0, 1),
        "mother dont-know newborn missed": (np.nan, 1, 1),
        "mother checked timing unknown": (np.nan, 0, np.nan),
    }
    for note, values in expect.items():
        got = tuple(out.loc[note, ["mother_missed", "newborn_missed", "dyad_any_missed"]])
        np.testing.assert_array_equal(got, values, err_msg=note)


def test_pre_discharge_check_never_counts_as_followup(synthetic_dyads):
    df = synthetic_dyads.assign(mother_check_before_discharge=1, newborn_check_before_discharge=1,
                                mother_check_after_discharge=0, newborn_check_after_discharge=0)
    out = missed_followup(df, window_days=42)
    assert (out.dyad_any_missed == 1).all()


def test_window_changes_late_check(synthetic_dyads):
    eligible, _ = apply_eligibility(synthetic_dyads, window_days=7)
    late = eligible[eligible.case_note == "mother checked late newborn on time"]
    assert missed_followup(late, 7).mother_missed.iloc[0] == 1
    assert missed_followup(late, 42).mother_missed.iloc[0] == 0
