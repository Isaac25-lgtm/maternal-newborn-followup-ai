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
| 2026-10-17 | Correct checkpoint-1 framing: standard indicators were insufficient to rule out distinct items; Rwanda questionnaires do ask after-discharge checks separately | FR370 Q441/Q445; NISR 2025 m66/m70 |
| 2026-10-17 | Eligibility conditions on newborn alive at discharge, not at window end; post-discharge deaths kept as competing `died` state; survivor-only only as explicit sensitivity | Window-end survival is future information and induces selection |
| 2026-10-17 | `missed_followup` requires explicit `check_clock`; no default | Post-discharge timing items use the delivery clock; silent assumption would mis-time windows |
| 2026-10-17 | Add `QUESTIONNAIRE_ONLY` crosswalk level; RW2019DHS rows carry wording but no variable names | Recode names for RWIR81 not seen |
| 2026-10-17 | Access request narrowed to RWIR81 only; 2025 file deferred | Least data needed to test codes before requesting more |
