import pytest

from mnfollowup import crosswalk
from mnfollowup.concepts import ENDPOINT_INPUTS

ROOT = crosswalk.Path(__file__).resolve().parents[1]


@pytest.fixture
def committed():
    return crosswalk.load(ROOT / "configs" / "crosswalk.csv")


def test_committed_crosswalk_never_claims_raw_audit(committed):
    assert "VERIFIED_RAW_AUDIT" not in set(committed.status)
    for s in ["RW2019DHS", "RW2025DHS", "KE2022DHS", "UG2022DHS", "ET2024DHS"]:
        with pytest.raises(crosswalk.EndpointNotReady):
            crosswalk.require_endpoint_ready(committed, s)


def test_only_rwanda_has_evidence_and_2019_asserts_no_variable(committed):
    promoted = committed[committed.status != "UNVERIFIED"]
    assert set(promoted.survey_id) == {"RW2019DHS", "RW2025DHS"}
    rw19 = committed[committed.survey_id == "RW2019DHS"]
    assert (rw19.source_variable == "").all()
    assert set(rw19.status) == {"QUESTIONNAIRE_ONLY", "UNVERIFIED"}


def test_post_discharge_timing_clock_is_birth_in_both_rwanda_surveys(committed):
    timed = committed[committed.concept.isin(crosswalk.TIMED_CONCEPTS) & (committed.status != "UNVERIFIED")]
    assert len(timed) == 4 and set(timed.timing_reference) == {"birth"}


def test_newborn_death_input_still_unverified_everywhere(committed):
    rows = committed[committed.concept == "newborn_age_at_death_days"]
    assert set(rows.status) == {"UNVERIFIED"}


def test_unverified_or_questionnaire_row_cannot_assert_variable():
    df = crosswalk.template(["SYN_A"])
    df.loc[0, "source_variable"] = "x1"
    assert any("must not assert" in e for e in crosswalk.validate(df))
    df.loc[0, ["status", "source_file", "source_location", "evidence_url", "evidence_label_verbatim", "verified_on"]] = [
        "QUESTIONNAIRE_ONLY", "SYN", "Q1", "https://example.invalid", "SYNTHETIC", "2026-10-17"]
    assert any("must not assert" in e for e in crosswalk.validate(df))


def test_promotion_requires_evidence_and_timing_reference():
    df = crosswalk.template(["SYN_A"])
    i = df.index[df.concept == "mother_after_discharge_check_day"][0]
    df.loc[i, ["status", "source_variable"]] = ["VERIFIED_LABEL", "x1"]
    errs = crosswalk.validate(df)
    assert any("evidence_url" in e for e in errs)
    assert any("source_location" in e for e in errs)
    assert any("timing_reference" in e for e in errs)


def test_endpoint_ready_only_when_all_inputs_audited():
    df = crosswalk.template(["SYN_A"])
    for c in ENDPOINT_INPUTS:
        i = df.index[df.concept == c][0]
        df.loc[i, ["status", "source_file", "source_variable", "source_location", "evidence_url",
                   "evidence_label_verbatim", "verified_on", "timing_reference"]] = [
            "VERIFIED_RAW_AUDIT", "SYNTHETIC.dta", f"syn_{c}", "synthetic", "https://example.invalid/synthetic",
            "SYNTHETIC LABEL", "2026-10-17", "birth"]
    assert crosswalk.validate(df) == []
    crosswalk.require_endpoint_ready(df, "SYN_A")
    df.loc[df.concept == ENDPOINT_INPUTS[0], "status"] = "VERIFIED_LABEL"
    with pytest.raises(crosswalk.EndpointNotReady):
        crosswalk.require_endpoint_ready(df, "SYN_A")
