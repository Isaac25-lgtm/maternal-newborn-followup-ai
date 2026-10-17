# Scientific protocol (draft, gated)

Status `HOLD_ACCESS`. This protocol fixes definitions before any data is seen. Items marked *Gate 1* depend on the raw-code audit; nothing here is a result.

## Aim

Rank facility-delivered mother–newborn pairs **at discharge** by their risk of receiving **no health check after discharge**, to support outreach under a fixed contact capacity. This is a prediction aim. It makes no claim that outreach would change outcomes.

## Why not routine PNC

DHS standard indicators and the FR370 tables time the *first* postnatal check from birth. For a facility birth this is usually the in-facility check. The Rwanda questionnaires, however, ask separately about checks after leaving the facility (2019-20 Q441/Q445; 2025 m66/m70): see [ENDPOINT_AUDIT.md](ENDPOINT_AUDIT.md). The target uses those items only.

## Cohort

Mother + most recent live birth in the recall period, with:

| Step | Rule | Concept |
|---|---|---|
| 1 | Most recent birth | `is_most_recent_birth` |
| 2 | Birth ≤ recall days before interview | `days_since_birth` |
| 3 | Full window elapsed before interview (birth + *W*, or birth + stay + *W* for a discharge window) | `days_since_birth`, `facility_stay_days` |
| 4 | Facility delivery (post-discharge items are shared with home births in 2025) | `facility_delivery` |
| 5 | Singleton (multiples reported separately) | `multiple_birth` |
| 6 | Newborn **alive at discharge** | `newborn_alive_at_discharge` |

Missing values exclude and are counted at the step where they occur (`endpoint.apply_eligibility`). Survival is conditioned on only up to discharge, which is known at the decision time. Newborns who die after discharge stay in the cohort (below). Mothers are survey respondents, so maternal deaths are excluded by design; this is a known survivor bias.

## Endpoint

Per member, window *W* days, with the timing clock stated explicitly (`check_clock` = clock of the source timing item, `window_from` = reference of the window):

| State | Rule | Missed flag |
|---|---|---|
| checked | post-discharge check within *W* | 0 |
| missed | no post-discharge check, or first one after *W* | 1 |
| died | newborn died after discharge, before window end, with no valid check before death | NA (competing) |
| invalid_time | negative time, or a post-discharge check timed before the known stay length, under **either** window clock | NA |
| inconsistent | death before discharge, or death before a reported check (never counted as checked) | NA |
| unknown | don't know / missing answer, timing, stay length needed for a conversion, or check and death on the same day / in undeterminable order | NA |

All chronology is compared on the birth clock and no check or death time is imputed. A valid check before a later death stays `checked`; the death is kept separately in `newborn_died_after_discharge`. Each NA state carries a reason in `mother_flag` / `newborn_flag` so the raw audit can count them.

Dyad endpoint = at least one member missed (1 if either is 1; 0 only if both 0; else NA). Survivor-only analysis (dropping `died`) is available only as the explicit sensitivity `endpoint.survivor_only_sensitivity`, reported alongside the primary.

Verified constraints (ENDPOINT_AUDIT.md): post-discharge timing items use the **delivery** clock; the 2019-20 newborn item is limited to two months after leaving and to health providers or TBAs, the mother item to "anyone" without a time limit. Primary *W* will be fixed after the raw audit within those limits (candidates: 7 and 42 days from birth; 7 days from discharge as sensitivity requiring stay length).

## Predictors

Only concepts with availability ≤ `BEFORE_DISCHARGE` in `concepts.py`, including pre-discharge checks (m62/m74; Q435/Q438) and stay length. Interview-time variables are rejected by `leakage.check_predictors` unless a labelled sensitivity sets `allow_interview_time=True`. Each predictor needs a verified crosswalk row.

## Analysis plan (only after Gate 1 on approved data)

1. 50-dyad raw-code audit per survey: eligibility, endpoint codes and units, DK codes, skip logic, last-birth applicability, twins, weights, cluster and strata, duplicates, newborn death timing vs stay.
2. Development: Rwanda 2019-20. Temporal test: Rwanda 2025 (`leakage.assert_temporal_holdout`). Geographic tests only where items match; Uganda 2022 pending access route.
3. Models: prevalence; simple triage rules; weighted regularised logistic; one tree ensemble with limited tuning inside training folds.
4. Primary metric: weighted recall of missed pairs at actual outreach capacity (`metrics.capacity_recall`), with precision, F2, false-alarm burden; AUROC/AUPRC and calibration secondary; cluster bootstrap within strata.
5. Reporting: TRIPOD+AI; risk of bias per PROBAST+AI.

## Falsification

Stop or redesign if: raw codes show the post-discharge items are not usable on facility births (e.g. high DK, routing errors); the endpoint cannot be audited on 50 dyads; the closest competitor already used these items with discharge-time predictors (see PRIOR_ART.md); or discharge-known predictors do not beat simple rules at realistic capacity in the 2025 wave.
