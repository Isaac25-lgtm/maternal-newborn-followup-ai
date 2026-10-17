import json
from datetime import date

import numpy as np
import pytest

from mnfollowup import access
from mnfollowup.metrics import capacity_recall


def test_hold_access_without_record(monkeypatch):
    monkeypatch.delenv(access.APPROVAL_ENV, raising=False)
    assert access.PROJECT_STATUS == "HOLD_ACCESS"
    with pytest.raises(access.AccessNotApproved, match="HOLD_ACCESS"):
        access.require_processing_permission("RW2019DHS", "x")


def test_repo_paths_refused():
    with pytest.raises(access.AccessNotApproved):
        access.refuse_repo_path(access.REPO_ROOT / "data" / "raw" / "file.dta")


def _record(tmp_path, **over):
    rec = {"investigator": "SYNTHETIC", "approving_body": "SYNTHETIC", "approval_reference": "SYN-1",
           "approved_purpose": "SYNTHETIC test", "survey_ids": ["RW2019DHS"],
           "approved_environment": "private-env", "expires_on": "2027-01-01"} | over
    p = tmp_path / "approval.json"
    p.write_text(json.dumps(rec))
    return p


def test_approval_record_checks(tmp_path, monkeypatch):
    monkeypatch.setenv(access.APPROVAL_ENV, str(_record(tmp_path)))
    today = date(2026, 10, 17)
    assert access.require_processing_permission("RW2019DHS", "private-env", today=today)["approval_reference"] == "SYN-1"
    for survey, env, when in [("KE2022DHS", "private-env", today), ("RW2019DHS", "github", today),
                              ("RW2019DHS", "private-env", date(2027, 2, 1))]:
        with pytest.raises(access.AccessNotApproved):
            access.require_processing_permission(survey, env, today=when)
    monkeypatch.setenv(access.APPROVAL_ENV, str(_record(tmp_path, approval_reference="")))
    with pytest.raises(access.AccessNotApproved, match="missing"):
        access.require_processing_permission("RW2019DHS", "private-env", today=today)


def test_capacity_recall_hand_computed():
    y = [1, 0, 1, 0, 1, 0, 0, 0, 0, 1]
    s = [0.9, 0.8, 0.7, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.05]
    r = capacity_recall(y, s, 0.3)  # flags indices 0,1,2
    assert r["flagged"] == 3 and r["recall"] == 0.5 and r["precision"] == pytest.approx(2 / 3)
    w = [2, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    rw = capacity_recall(y, s, 0.3, weights=w)
    assert rw["recall"] == pytest.approx(3 / 5) and rw["false_alarms_weighted"] == 1


def test_capacity_recall_rejects_missing_and_nonbinary():
    with pytest.raises(ValueError):
        capacity_recall([1, np.nan], [0.1, 0.2], 0.5)
    with pytest.raises(ValueError):
        capacity_recall([2, 0], [0.1, 0.2], 0.5)
