# Scientific protocol (draft, gated)

Status `HOLD_ACCESS`. This protocol fixes definitions before any data is seen. Items marked *Gate 1* depend on verifying the questionnaires and recode files; nothing here is a result.

## Aim

Rank facility-delivered mother–newborn pairs **at discharge** by their risk of receiving **no health check after discharge**, to support outreach under a fixed contact capacity. This is a prediction aim. It makes no claim that outreach would change outcomes.

## Why the standard PNC indicator is not the target

DHS standard indicators time the *first* postnatal check from birth (verified from the DHS API, [DATA_ACCESS.md](DATA_ACCESS.md) finding 1). For a facility birth this is usually the check before leaving the facility, so a woman can count as "PNC within 2 days" without anyone contacting her after she goes home. Predicting routine PNC coverage would also overlap with existing Rwanda PNC analyses. The target here is follow-up *after* discharge only.

## Cohort

Mother + most recent live birth in the survey's recall period (default 24 months), with:

| Step | Rule | Concept |
|---|---|---|
| 1 | Most recent birth | `is_most_recent_birth` |
| 2 | Birth ≤ recall days before interview | `days_since_birth` |
| 3 | Full endpoint window elapsed before interview | `days_since_birth ≥ W` |
| 4 | Facility delivery | `facility_delivery` |
| 5 | Singleton (multiples reported separately) | `multiple_birth` |
| 6 | Newborn alive at window end | `child_alive_at_window_end` |

Missing values exclude and are counted at the step where they occur (`endpoint.apply_eligibility` returns the flow table). Step 6 conditions on survival, which is post-discharge information; it is used only for eligibility and its selection effect must be reported.

## Endpoint

Per member (mother, newborn), window *W* days:

- 1 = no check after discharge, or first post-discharge check after day *W*
- 0 = first post-discharge check within *W*
- missing = don't know / missing, or checked with unknown timing

Dyad endpoint = at least one member missed, with three-valued logic (1 if either is 1; 0 only if both 0; otherwise missing). Implemented in `endpoint.missed_followup`.

*Gate 1 items:* whether each survey asks after-discharge checks separately for mother and newborn; whether timing is recorded from birth or from discharge (`timing_reference` in the crosswalk); skip patterns; whether the newborn item applies to all births or only some; choice of *W*. Without timing relative to discharge, a "within *W* days of birth" window mixes facility stay and home time; `facility_stay_days` may correct this if recorded.

## Predictors

Only concepts with availability ≤ `BEFORE_DISCHARGE` in `concepts.py`. Pre-discharge checks are admissible (known at discharge). Interview-time variables (wealth index, residence, marital status, insurance at interview) are rejected by `leakage.check_predictors` unless a labelled sensitivity analysis sets `allow_interview_time=True`. Unregistered names are rejected. Each predictor also needs a verified crosswalk row.

## Analysis plan (only after Gate 1 on approved data)

1. 50-dyad raw-code audit per survey: eligibility, endpoint codes, skip logic, twins, weights, cluster and strata, duplicates.
2. Development: Rwanda 2019–20. Temporal test: Rwanda 2025 (`leakage.assert_temporal_holdout` on fieldwork dates). Geographic: Kenya 2022 / Ethiopia 2024–25 only if endpoint items match; Uganda 2022 pending access route.
3. Models: prevalence; simple triage rules; weighted regularised logistic; one tree ensemble with limited tuning inside training folds.
4. Primary metric: weighted recall of missed pairs at the actual outreach capacity (`metrics.capacity_recall`), with precision, F2 and false-alarm burden; AUROC/AUPRC and calibration secondary. Uncertainty by cluster bootstrap respecting strata.
5. Subgroups: facility sector, residence, region, maternal age and education.
6. Reporting: TRIPOD+AI; risk of bias per PROBAST+AI.

## Falsification

The project stops or redesigns if: no survey separates after-discharge checks from pre-discharge checks; the endpoint cannot be audited on 50 dyads; or discharge-known predictors do not beat simple rules at realistic capacity in the held-out wave.
