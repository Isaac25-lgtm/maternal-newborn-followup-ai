# R03 evidence status

Last updated 2026-10-17 (public phase 2).

**Scientific decision: `HOLD_ACCESS`.**

| Dimension | Status | Evidence |
|---|---|---|
| Data access | No approved respondent data in this environment; none requested or transferred | [DATA_ACCESS.md](DATA_ACCESS.md) |
| Endpoint existence | **Verified from public documents**: Rwanda 2019-20 questionnaire Q441/Q445 and Rwanda 2025 recode m66/m70 ask about checks after leaving the facility, separately from in-facility checks (Q435/Q438; m62/m74) | [ENDPOINT_AUDIT.md](ENDPOINT_AUDIT.md) |
| Endpoint validity | Not verified: codes, DK rates, skips, unit encoding, 2019-20 recode names; timing uses the delivery clock; mother/newborn items asymmetric | ENDPOINT_AUDIT.md "Unresolved" |
| Survey availability | RW2019DHS, RW2025DHS, KE2022DHS, ET2024DHS listed by DHS Program; UG2022 not listed | DATA_ACCESS.md |
| Scientific novelty | Conditional: closest same-dataset competitor (Kubahoniyesu 2026) checked at abstract depth only | [PRIOR_ART.md](PRIOR_ART.md) |
| AI incremental value | Not tested | — |
| Readiness | Not protocol- or manuscript-ready | — |

## Done

- Checkpoint 1: environment probe; 13 catalogue requests; package and 27 tests.
- Phase 2 (13 public requests): Rwanda 2019-20 questionnaire (FR370 Appendix F) and Rwanda 2025 NISR dictionary read; crosswalk now has 9 `QUESTIONNAIRE_ONLY` rows (RW2019DHS, no variable names asserted) and 10 `VERIFIED_LABEL` rows (RW2025DHS); five-competitor matrix at abstract depth.
- Code fix: eligibility now conditions on newborn alive **at discharge**; post-discharge newborn deaths kept as a competing `died` state; survivor-only analysis is an explicit sensitivity. Explicit timing clocks; negative, inconsistent and unconvertible times become unknown; ambiguous clocks raise.
- Chronology fix (final review): a birth-clock post-discharge check earlier than the known stay is `invalid_time` under both window clocks; death before a reported check is `inconsistent` (never `checked`); death before discharge is `inconsistent`; same-day check/death and undeterminable order are `unknown`; a valid check before a later death stays `checked` with the death kept in `newborn_died_after_discharge`. Reasons recorded in `*_flag`.
- Tests: 60 passed (`.venv/bin/python -m pytest -q`).

## Not done

No 2019-20 recode names; no unit/missing-code verification; no Kenya/Ethiopia/Uganda questionnaires; no competitor full texts; no 50-dyad audit, event rates, models or metrics.

## Next

1. Public: DHS-8 recode manual or a 2019-20 dictionary for RWIR81 names and unit codes; Rwanda 2025 questionnaire.
2. Competitor full texts, starting with Kubahoniyesu 2026.
3. Investigator: [ACCESS_REQUEST.md](ACCESS_REQUEST.md).
