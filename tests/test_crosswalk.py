import pytest

from mnfollowup import crosswalk
from mnfollowup.concepts import ENDPOINT_INPUTS

ROOT = crosswalk.Path(__file__).resolve().parents[1]


def test_committed_crosswalk_is_valid_and_wholly_unverified():
    df = crosswalk.load(ROOT / "configs" / "crosswalk.csv")
    assert set(df.status) == {"UNVERIFIED"}
    assert (df.source_variable == "").all()
    for s in ["RW2019DHS", "RW2025DHS", "KE2022DHS", "UG2022DHS"]:
        with pytest.raises(crosswalk.EndpointNotReady):
            crosswalk.require_endpoint_ready(df, s)


def test_unverified_row_cannot_assert_variable():
    df = crosswalk.template(["SYN_A"])
    df.loc[0, "source_variable"] = "x1"
    assert any("must not assert" in e for e in crosswalk.validate(df))


def test_promotion_requires_evidence_and_timing_reference():
    df = crosswalk.template(["SYN_A"])
    i = df.index[df.concept == "mother_after_discharge_check_day"][0]
    df.loc[i, ["status", "source_variable"]] = ["VERIFIED_LABEL", "x1"]
    errs = crosswalk.validate(df)
    assert any("evidence_url" in e for e in errs)
    assert any("timing_reference" in e for e in errs)


def test_endpoint_ready_only_when_all_inputs_audited():
    df = crosswalk.template(["SYN_A"])
    for c in ENDPOINT_INPUTS:
        i = df.index[df.concept == c][0]
        df.loc[i, ["status", "source_file", "source_variable", "evidence_url", "evidence_label_verbatim",
                   "verified_on", "timing_reference"]] = [
            "VERIFIED_RAW_AUDIT", "SYNTHETIC.dta", f"syn_{c}", "https://example.invalid/synthetic",
            "SYNTHETIC LABEL", "2026-10-17", "birth"]
    assert crosswalk.validate(df) == []
    crosswalk.require_endpoint_ready(df, "SYN_A")
    df.loc[df.concept == ENDPOINT_INPUTS[0], "status"] = "VERIFIED_LABEL"
    with pytest.raises(crosswalk.EndpointNotReady):
        crosswalk.require_endpoint_ready(df, "SYN_A")
