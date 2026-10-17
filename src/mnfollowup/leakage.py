"""Guards against predictor leakage and validation-split contamination."""

from __future__ import annotations

from collections.abc import Iterable

from .concepts import DISCHARGE_ORIGIN, Availability, get


class LeakageError(ValueError):
    pass


def check_predictors(features: Iterable[str], *, allow_interview_time: bool = False) -> list[str]:
    """Return the features unchanged if all are admissible at discharge.

    Raises LeakageError listing every offending feature. Unregistered names are
    rejected: an unknown timing is treated as a leak, not as safe.

    ``allow_interview_time`` admits INTERVIEW-measured proxies (e.g. wealth at
    interview) and must only be used for a labelled sensitivity analysis.
    """
    features = list(features)
    problems = []
    for f in features:
        try:
            c = get(f)
        except KeyError:
            problems.append(f"{f}: unregistered concept (timing unknown)")
            continue
        if c.role in ("endpoint_input", "identifier", "design", "eligibility"):
            problems.append(f"{f}: role {c.role!r} is never a predictor")
        elif c.availability == Availability.INTERVIEW:
            if not allow_interview_time:
                problems.append(f"{f}: measured at interview, not known at discharge")
        elif c.availability > DISCHARGE_ORIGIN:
            problems.append(f"{f}: available {c.availability.name}, after discharge origin")
    if len(set(features)) != len(features):
        problems.append("duplicate feature names")
    if problems:
        raise LeakageError("; ".join(problems))
    return features


def assert_group_disjoint(train_groups: Iterable, test_groups: Iterable, label: str = "group") -> None:
    """Fail if any sampling unit (cluster, survey, country) appears in both splits."""
    overlap = set(train_groups) & set(test_groups)
    if overlap:
        shown = sorted(map(str, overlap))[:5]
        raise LeakageError(f"{len(overlap)} {label}(s) in both train and test, e.g. {shown}")


def assert_temporal_holdout(train_fieldwork_end: Iterable[str], test_fieldwork_start: Iterable[str]) -> None:
    """Fail unless every test survey's fieldwork starts after all training fieldwork ended.

    Dates are ISO strings (YYYY-MM-DD) so lexical comparison is chronological.
    """
    latest_train = max(train_fieldwork_end)
    earliest_test = min(test_fieldwork_start)
    if not earliest_test > latest_train:
        raise LeakageError(f"test fieldwork starts {earliest_test}, not after training fieldwork end {latest_train}")
