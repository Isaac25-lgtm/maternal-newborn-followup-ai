import pytest

from mnfollowup.concepts import ENDPOINT_INPUTS, REGISTRY, Availability
from mnfollowup.leakage import LeakageError, assert_group_disjoint, assert_temporal_holdout, check_predictors

SAFE = ["maternal_age_at_birth", "parity", "anc_visits", "caesarean_delivery", "facility_stay_days",
        "mother_check_before_discharge", "newborn_check_before_discharge"]


def test_discharge_known_predictors_pass():
    assert check_predictors(SAFE) == SAFE


@pytest.mark.parametrize("bad", list(ENDPOINT_INPUTS))
def test_endpoint_inputs_rejected(bad):
    with pytest.raises(LeakageError, match=bad):
        check_predictors(SAFE + [bad])


def test_interview_time_wealth_rejected_by_default_and_only_allowed_explicitly():
    with pytest.raises(LeakageError, match="interview"):
        check_predictors(["household_wealth_at_interview"])
    assert check_predictors(["household_wealth_at_interview"], allow_interview_time=True)


@pytest.mark.parametrize("bad", ["sample_weight", "cluster_id", "days_since_birth", "newborn_alive_at_discharge"])
def test_design_and_eligibility_rejected(bad):
    with pytest.raises(LeakageError):
        check_predictors([bad])


def test_unregistered_and_duplicate_rejected():
    with pytest.raises(LeakageError, match="unregistered"):
        check_predictors(["m70"])
    with pytest.raises(LeakageError, match="duplicate"):
        check_predictors(["parity", "parity"])


def test_registry_predictors_are_all_pre_discharge_or_interview():
    for c in REGISTRY.values():
        if c.role == "predictor":
            assert c.availability <= Availability.BEFORE_DISCHARGE or c.availability == Availability.INTERVIEW


def test_group_and_temporal_guards():
    assert_group_disjoint(["RW2019DHS"], ["RW2025DHS"], "survey")
    with pytest.raises(LeakageError):
        assert_group_disjoint([1, 2, 3], [3, 4], "cluster")
    # fieldwork dates as published by the DHS API (docs/source_extracts)
    assert_temporal_holdout(["2020-07-01"], ["2025-07-01"])
    with pytest.raises(LeakageError):
        assert_temporal_holdout(["2025-11-01"], ["2025-07-01"])
