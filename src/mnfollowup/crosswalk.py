"""Survey-to-concept crosswalk with an evidence gate.

Every row maps one harmonised concept to one source variable for one survey.
Evidence levels:
    UNVERIFIED          concept only; no source variable may be asserted
    QUESTIONNAIRE_ONLY  official question wording seen, recode variable unknown
                        (source_variable must stay empty)
    VERIFIED_LABEL      official recode variable name + label seen
    VERIFIED_RAW_AUDIT  codes and skips checked on 50 dyads in approved data
Endpoint derivation for modelling requires VERIFIED_RAW_AUDIT.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .concepts import ENDPOINT_INPUTS, REGISTRY

COLUMNS = [
    "survey_id",
    "concept",
    "source_file",
    "source_variable",
    "source_location",  # page / question number / dictionary offset
    "timing_reference",  # birth | discharge | not_applicable | UNVERIFIED
    "status",  # see STATUS_ORDER
    "evidence_url",
    "evidence_label_verbatim",
    "verified_on",
    "notes",
]
STATUS_ORDER = {"UNVERIFIED": 0, "QUESTIONNAIRE_ONLY": 1, "VERIFIED_LABEL": 2, "VERIFIED_RAW_AUDIT": 3}
TIMED_CONCEPTS = ("mother_after_discharge_check_day", "newborn_after_discharge_check_day")


class EndpointNotReady(RuntimeError):
    pass


def load(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    errors = validate(df)
    if errors:
        raise ValueError("Invalid crosswalk:\n" + "\n".join(errors))
    return df


def validate(df: pd.DataFrame) -> list[str]:
    errors = []
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        return [f"missing columns {missing}"]
    dup = df.duplicated(["survey_id", "concept"])
    for i in df.index[dup]:
        errors.append(f"row {i}: duplicate survey/concept {df.at[i, 'survey_id']}/{df.at[i, 'concept']}")
    for i, r in df.iterrows():
        where = f"row {i} ({r.survey_id}/{r.concept})"
        if r.concept not in REGISTRY:
            errors.append(f"{where}: unknown concept")
        if r.status not in STATUS_ORDER:
            errors.append(f"{where}: bad status {r.status!r}")
            continue
        if r.status in ("UNVERIFIED", "QUESTIONNAIRE_ONLY"):
            if r.source_variable:
                errors.append(f"{where}: {r.status} rows must not assert a source variable")
        if r.status == "UNVERIFIED":
            continue
        required = ["source_file", "source_location", "evidence_url", "evidence_label_verbatim", "verified_on"]
        if r.status != "QUESTIONNAIRE_ONLY":
            required.append("source_variable")
        for field in required:
            if not r[field]:
                errors.append(f"{where}: {r.status} requires {field}")
        if r.concept in TIMED_CONCEPTS and r.timing_reference not in ("birth", "discharge"):
            errors.append(f"{where}: timing concepts need timing_reference birth|discharge")
    return errors


def template(survey_ids: list[str]) -> pd.DataFrame:
    """All registered concepts for each survey, UNVERIFIED with no source variable."""
    rows = [
        {c: "" for c in COLUMNS}
        | {"survey_id": s, "concept": name, "status": "UNVERIFIED", "timing_reference": "UNVERIFIED"}
        for s in survey_ids
        for name in REGISTRY
    ]
    return pd.DataFrame(rows, columns=COLUMNS)


def require_endpoint_ready(df: pd.DataFrame, survey_id: str, minimum: str = "VERIFIED_RAW_AUDIT") -> None:
    """Raise EndpointNotReady unless every endpoint input for the survey meets ``minimum``."""
    need = STATUS_ORDER[minimum]
    sub = df[df.survey_id == survey_id].set_index("concept")
    short = [
        f"{c}={sub.at[c, 'status'] if c in sub.index else 'ABSENT'}"
        for c in ENDPOINT_INPUTS
        if c not in sub.index or STATUS_ORDER[sub.at[c, "status"]] < need
    ]
    if short:
        raise EndpointNotReady(f"{survey_id}: endpoint inputs below {minimum}: {', '.join(short)}")
