"""Harmonised concept registry with information-availability timing.

Concepts are survey-independent names. They deliberately carry NO source
variable names: mapping a concept to a DHS recode variable is the job of the
crosswalk (``crosswalk.py``) and requires documented evidence.

The prediction time origin is the moment of facility discharge after delivery.
A predictor is admissible only if its information is available at or before
that moment. Anything measured at the survey interview (e.g. current household
wealth, current marital status) is NOT assumed to be discharge-known.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Availability(IntEnum):
    """When the information exists relative to the discharge time origin."""

    BEFORE_PREGNANCY = 0  # stable or historical characteristics
    ANTENATAL = 1
    INTRAPARTUM = 2
    BEFORE_DISCHARGE = 3  # still in the facility, includes pre-discharge checks
    AFTER_DISCHARGE = 4  # outcome window; never a predictor
    INTERVIEW = 5  # measured at survey interview, months/years after birth
    DESIGN = 6  # survey design/identifier, never a predictor


DISCHARGE_ORIGIN = Availability.BEFORE_DISCHARGE


@dataclass(frozen=True)
class Concept:
    name: str
    role: str  # identifier | design | eligibility | endpoint_input | predictor
    availability: Availability
    description: str


_CONCEPTS = [
    # identifiers and survey design
    Concept("survey_id", "identifier", Availability.DESIGN, "Survey identifier, e.g. RW2019DHS"),
    Concept("cluster_id", "design", Availability.DESIGN, "Primary sampling unit"),
    Concept("stratum", "design", Availability.DESIGN, "Sampling stratum"),
    Concept("sample_weight", "design", Availability.DESIGN, "Woman/birth sampling weight (already de-scaled)"),
    Concept("household_id", "identifier", Availability.DESIGN, "Household within cluster"),
    Concept("woman_line", "identifier", Availability.DESIGN, "Respondent line number"),
    Concept("birth_index", "identifier", Availability.DESIGN, "Birth order within respondent's history (1 = most recent)"),
    # eligibility
    Concept("days_since_birth", "eligibility", Availability.INTERVIEW, "Interview date minus birth date, days"),
    Concept("facility_delivery", "eligibility", Availability.INTRAPARTUM, "Delivered in a health facility (1/0)"),
    Concept("multiple_birth", "eligibility", Availability.INTRAPARTUM, "Twin or higher-order birth (1/0)"),
    Concept("is_most_recent_birth", "eligibility", Availability.DESIGN, "Birth is respondent's most recent (1/0)"),
    Concept(
        "newborn_alive_at_discharge",
        "eligibility",
        Availability.BEFORE_DISCHARGE,
        "Newborn discharged alive; would be derived from age at death and facility stay (measurability UNVERIFIED)",
    ),
    # endpoint inputs (respondent-reported; coded 1 yes, 0 no, NA dk/missing/skip)
    Concept("mother_check_before_discharge", "predictor", Availability.BEFORE_DISCHARGE, "Mother's health checked before leaving facility"),
    Concept("newborn_check_before_discharge", "predictor", Availability.BEFORE_DISCHARGE, "Newborn's health checked before leaving facility"),
    Concept("mother_check_after_discharge", "endpoint_input", Availability.AFTER_DISCHARGE, "Mother's health checked after leaving facility"),
    Concept("newborn_check_after_discharge", "endpoint_input", Availability.AFTER_DISCHARGE, "Newborn's health checked after leaving facility"),
    Concept(
        "mother_after_discharge_check_day",
        "endpoint_input",
        Availability.AFTER_DISCHARGE,
        "Timing of first post-discharge maternal check, days; reference point (birth vs discharge) set per survey in crosswalk",
    ),
    Concept(
        "newborn_after_discharge_check_day",
        "endpoint_input",
        Availability.AFTER_DISCHARGE,
        "Timing of first post-discharge newborn check, days; reference point set per survey in crosswalk",
    ),
    Concept(
        "newborn_age_at_death_days",
        "endpoint_input",
        Availability.AFTER_DISCHARGE,
        "Newborn age at death in days since birth, NA if alive; post-discharge death is a competing state, not a miss",
    ),
    # candidate discharge-time predictors (non-exhaustive; each needs crosswalk evidence)
    Concept("facility_stay_days", "predictor", Availability.BEFORE_DISCHARGE, "Length of facility stay after delivery, days"),
    Concept("maternal_age_at_birth", "predictor", Availability.BEFORE_PREGNANCY, "Mother's age at the birth (derived from birth dates)"),
    Concept("parity", "predictor", Availability.BEFORE_PREGNANCY, "Number of births including index birth"),
    Concept("maternal_education", "predictor", Availability.BEFORE_PREGNANCY, "Highest education level (assumed stable; verify)"),
    Concept("anc_visits", "predictor", Availability.ANTENATAL, "Number of antenatal visits for index pregnancy"),
    Concept("caesarean_delivery", "predictor", Availability.INTRAPARTUM, "Delivery by caesarean section"),
    Concept("facility_sector", "predictor", Availability.INTRAPARTUM, "Public / private / other facility of delivery"),
    Concept("skilled_birth_attendant", "predictor", Availability.INTRAPARTUM, "Delivery assisted by skilled provider"),
    Concept("reported_birth_size", "predictor", Availability.INTRAPARTUM, "Mother-reported size at birth"),
    # interview-time measurements: excluded unless an explicit sensitivity analysis
    Concept("household_wealth_at_interview", "predictor", Availability.INTERVIEW, "Wealth index measured at interview, not at discharge"),
    Concept("residence_at_interview", "predictor", Availability.INTERVIEW, "Urban/rural residence at interview"),
    Concept("marital_status_at_interview", "predictor", Availability.INTERVIEW, "Current marital status at interview"),
    Concept("insurance_at_interview", "predictor", Availability.INTERVIEW, "Health insurance coverage at interview"),
]

REGISTRY: dict[str, Concept] = {c.name: c for c in _CONCEPTS}

ENDPOINT_INPUTS = tuple(c.name for c in _CONCEPTS if c.role == "endpoint_input")


def get(name: str) -> Concept:
    try:
        return REGISTRY[name]
    except KeyError:
        raise KeyError(f"Unregistered concept {name!r}; add it to concepts.py with a timing before use") from None
