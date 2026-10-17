"""Build configs/crosswalk.csv from the evidence actually read on 2026-10-17.

Only items whose official wording or recode label was seen are promoted.
Everything else stays UNVERIFIED with no source variable.

Usage: python scripts/build_crosswalk.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mnfollowup import crosswalk  # noqa: E402

SURVEYS = ["RW2019DHS", "RW2025DHS", "KE2022DHS", "UG2022DHS", "ET2024DHS"]
SEEN = "2026-10-17"

NISR_URL = "https://microdata.statistics.gov.rw/index.php/catalog/126/datafile/F9/?limit=100&offset=600"
NISR_FILE = "RWNR91FL (Pregnancy and Postnatal Care (last 3 yrs) Recode)"
# (concept, variable, dictionary label as displayed, timing_reference, note)
RW2025 = [
    ("facility_delivery", "m15", "place of delivery", "not_applicable", "Facility code set not yet seen; derivation rule pending audit"),
    ("facility_stay_days", "m61", "time spent at place of delivery", "not_applicable", "Unit encoding (hours/days/weeks) not yet seen"),
    ("mother_check_before_discharge", "m62", "respondent's health checked after delivery before discharge", "not_applicable", ""),
    ("mother_check_after_discharge", "m66", "respondent's health checked after discharge/delivery at home", "not_applicable",
     "Shared with home deliveries; must be restricted to facility births"),
    ("mother_after_discharge_check_day", "m67", "how long after delivery respondent's health check (after discharge/home delivery",
     "birth", "Label truncated in dictionary; clock is delivery, not discharge"),
    ("newborn_check_after_discharge", "m70", "child's health checked after discharge/delivery at home", "not_applicable",
     "Shared with home deliveries; must be restricted to facility births"),
    ("newborn_after_discharge_check_day", "m71", "how long after delivery child's health check (after discharge/home delivery) too",
     "birth", "Label truncated in dictionary; clock is delivery, not discharge"),
    ("newborn_check_before_discharge", "m74", "child's health checked before discharge", "not_applicable", ""),
    ("caesarean_delivery", "m17", "delivery by caesarean section", "not_applicable", ""),
    ("reported_birth_size", "m18", "size of child at birth", "not_applicable", ""),
]

FR370_URL = "https://dhsprogram.com/pubs/pdf/FR370/FR370.pdf"
FR370_FILE = "FR370 Appendix F, Woman's Questionnaire Section 4 (sha256 f85ad981...c5f6fa)"
# (concept, location, verbatim question, timing_reference, note)
RW2019 = [
    ("facility_delivery", "Q430, printed p.446", "Where did you give birth to (NAME)?", "not_applicable",
     "Home 11/12 and other 96 skip facility block (Q434B)"),
    ("facility_stay_days", "Q431, printed p.446", "How long after (NAME) was delivered did you stay there?", "not_applicable",
     "Recorded as HOURS/DAYS/WEEKS, DON'T KNOW 998"),
    ("caesarean_delivery", "Q432, printed p.446", "Was (NAME) delivered by caesarean, that is, did they cut your belly open to take the baby out?",
     "not_applicable", ""),
    ("mother_check_before_discharge", "Q435, printed p.447",
     "Did anyone check on your health while you were still in the facility?", "not_applicable", "YES/NO; no DON'T KNOW code printed"),
    ("newborn_check_before_discharge", "Q438, printed p.447",
     "Did anyone check on (NAME)'s health while you were still in the facility?", "not_applicable", "YES/NO/DON'T KNOW"),
    ("mother_check_after_discharge", "Q441, printed p.448",
     "Did anyone check on your health after you left the facility?", "not_applicable",
     "Asked only on facility path; 'anyone'; no time limit in wording; YES/NO, no DON'T KNOW code printed"),
    ("mother_after_discharge_check_day", "Q442, printed p.448", "How long after delivery did that check take place?", "birth",
     "Clock is delivery"),
    ("newborn_check_after_discharge", "Q445, printed p.448",
     "Did any health care provider or a traditional birth attendant check on (NAME)'s health in the two months after you left (FACILITY IN 430)?",
     "not_applicable", "Provider-restricted and limited to two months after leaving; YES/NO/DON'T KNOW"),
    ("newborn_after_discharge_check_day", "Q446, printed p.449",
     "How many hours, days or weeks after the birth of (NAME) did that check take place?", "birth", "Clock is birth"),
]


def main() -> None:
    df = crosswalk.template(SURVEYS)
    df["notes"] = "Concept defined; no source evidence read yet."
    df.loc[df.survey_id == "UG2022DHS", "notes"] = (
        "Not listed in DHS Program dataset catalogue (api.dhsprogram.com, 2026-10-17); distributor to be confirmed with UBOS."
    )

    def put(survey, concept, **fields):
        i = df.index[(df.survey_id == survey) & (df.concept == concept)]
        assert len(i) == 1, (survey, concept)
        for k, v in fields.items():
            df.loc[i[0], k] = v

    for concept, var, label, ref, note in RW2025:
        put("RW2025DHS", concept, status="VERIFIED_LABEL", source_file=NISR_FILE, source_variable=var,
            source_location="NISR NADA catalog 126, file F9, dictionary offsets 600-700", timing_reference=ref,
            evidence_url=NISR_URL, evidence_label_verbatim=label, verified_on=SEEN,
            notes=note or "Label only; codes, skips and missing values not yet seen")
    for concept, loc, question, ref, note in RW2019:
        put("RW2019DHS", concept, status="QUESTIONNAIRE_ONLY", source_file=FR370_FILE, source_location=loc,
            timing_reference=ref, evidence_url=FR370_URL, evidence_label_verbatim=question, verified_on=SEEN,
            notes=note + ("; " if note else "") + "recode variable name not yet verified for RWIR81")
    errors = crosswalk.validate(df)
    if errors:
        sys.exit("\n".join(errors))
    df.to_csv(ROOT / "configs" / "crosswalk.csv", index=False)
    print(df.status.value_counts().to_dict())


if __name__ == "__main__":
    main()
