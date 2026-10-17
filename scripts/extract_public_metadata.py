"""Extract small, public catalogue facts from DHS API JSON responses.

Inputs are raw responses saved outside the repository (they are public
catalogue metadata, not respondent data). Outputs are small CSV extracts
committed under docs/source_extracts/ so reviewers can see exactly what was
read. No respondent microdata is touched.

Usage:
    python -I scripts/extract_public_metadata.py <surveys.json> <datasets.json> <indicators.json> <out_dir>
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

SURVEYS = {"RW2019DHS", "RW2025DHS", "KE2022DHS", "ET2024DHS", "UG2016DHS"}
RECODES = {"Births Recode", "Individual Recode", "Children's Recode", "Household Recode"}


def main(surveys_path: str, datasets_path: str, indicators_path: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    surveys = json.loads(Path(surveys_path).read_text())["Data"]
    with open(out / "dhs_api_surveys_RW_UG_KE_ET.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["SurveyId", "SurveyYearLabel", "FieldworkStart", "FieldworkEnd", "ReleaseDate", "SurveyStatus"])
        for s in sorted(surveys, key=lambda s: s["SurveyId"]):
            w.writerow([s["SurveyId"], s["SurveyYearLabel"], s["FieldworkStart"], s["FieldworkEnd"], s["ReleaseDate"], s["SurveyStatus"]])

    datasets = json.loads(Path(datasets_path).read_text())["Data"]
    listed = sorted({d["SurveyId"] for d in datasets})
    with open(out / "dhs_api_recode_files.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["SurveyId", "FileType", "FileFormat", "FileName", "FileDateLastModified", "FileSizeBytes"])
        for d in sorted(datasets, key=lambda d: (d["SurveyId"], d["FileType"])):
            if d["SurveyId"] in SURVEYS and d["FileType"] in RECODES and d["FileFormat"].startswith("Stata"):
                w.writerow([d["SurveyId"], d["FileType"], d["FileFormat"], d["FileName"], d["FileDateLastModified"], d["FileSize"]])
    (out / "dhs_api_dataset_survey_ids.txt").write_text("\n".join(listed) + "\n")

    indicators = json.loads(Path(indicators_path).read_text())["Data"]
    with open(out / "dhs_api_postnatal_indicator_definitions.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["IndicatorId", "Label", "Definition", "Denominator"])
        for x in indicators:
            text = f"{x.get('Label') or ''} {x.get('Definition') or ''}"
            if re.search(r"postnatal", text, re.I):
                w.writerow([x["IndicatorId"], x["Label"], x.get("Definition"), x.get("Denominator")])


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
