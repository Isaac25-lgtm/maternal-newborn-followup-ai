"""Access gate: no respondent data is processed without a recorded approval.

The approval record is a JSON file kept OUTSIDE this repository and pointed to
by the environment variable named in ``APPROVAL_ENV``. Its contents are
written by the investigator from their actual DHS Program / national
statistics office authorisation; this code only checks that it exists, covers
the requested survey, has not expired and names the processing environment.
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

PROJECT_STATUS = "HOLD_ACCESS"
APPROVAL_ENV = "MNF_APPROVAL_RECORD"
REQUIRED_FIELDS = (
    "investigator",
    "approving_body",
    "approval_reference",
    "approved_purpose",
    "survey_ids",
    "approved_environment",
    "expires_on",
)
REPO_ROOT = Path(__file__).resolve().parents[2]


class AccessNotApproved(PermissionError):
    pass


def refuse_repo_path(path: str | Path) -> Path:
    """Respondent files and audit sheets must never live inside the Git work tree."""
    p = Path(path).resolve()
    if p == REPO_ROOT or REPO_ROOT in p.parents:
        raise AccessNotApproved(f"{p} is inside the repository; keep restricted data outside {REPO_ROOT}")
    return p


def require_processing_permission(survey_id: str, environment: str, *, today: date | None = None) -> dict:
    record_path = os.environ.get(APPROVAL_ENV)
    if not record_path:
        raise AccessNotApproved(f"{PROJECT_STATUS}: no approval record ({APPROVAL_ENV} unset)")
    path = refuse_repo_path(record_path)
    if not path.is_file():
        raise AccessNotApproved(f"{PROJECT_STATUS}: approval record {path} not found")
    record = json.loads(path.read_text())
    missing = [f for f in REQUIRED_FIELDS if not record.get(f)]
    if missing:
        raise AccessNotApproved(f"approval record missing {missing}")
    if survey_id not in record["survey_ids"]:
        raise AccessNotApproved(f"{survey_id} not covered by approval {record['approval_reference']}")
    if environment != record["approved_environment"]:
        raise AccessNotApproved(f"environment {environment!r} not approved (approved: {record['approved_environment']!r})")
    if date.fromisoformat(record["expires_on"]) < (today or date.today()):
        raise AccessNotApproved(f"approval {record['approval_reference']} expired {record['expires_on']}")
    return record
