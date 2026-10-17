# Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-10-17 | Remain `HOLD_ACCESS`; no data requested or transferred | No approved respondent data supplied; investigator instruction |
| 2026-10-17 | Endpoint = no check **after discharge** within *W* days; pre-discharge checks never count | DHS standard PNC indicators time first check from birth and do not distinguish discharge |
| 2026-10-17 | Unknown values stay unknown (three-valued dyad logic); missing eligibility values exclude and are counted | Avoid silently coding don't-know as no check |
| 2026-10-17 | Interview-time variables excluded from predictors by default | Not known at discharge (e.g. wealth at interview) |
| 2026-10-17 | Unregistered predictors rejected | Unknown timing treated as leakage risk |
| 2026-10-17 | Crosswalk committed with no source variables | Labels not yet seen; no invented mappings |
| 2026-10-17 | Multiples excluded from primary cohort, counted | Dyad definition ambiguous for twins; revisit after audit |
| 2026-10-17 | No `train.py`, `baselines.py`, `experiment.yaml` or dashboard yet | Would be untested placeholders before Gate 1 |
| 2026-10-17 | Uganda 2022 not usable as validation until access route confirmed | Not listed in DHS Program catalogue |
