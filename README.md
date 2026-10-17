# Mother–newborn post-discharge follow-up (R03)

Investigator: Isaac Omoding · Research programme R03 · **Status: `HOLD_ACCESS`**

After a facility birth, mothers and newborns are discharged into the period when most maternal and neonatal deaths happen. If programmes can only call or visit some of them, they need to know at discharge which pairs are least likely to get a check after they leave. This project asks whether information available at discharge can rank facility-delivered mother–newborn pairs by their risk of having **no health check after discharge**, and whether that ranking still holds in a later survey wave and in other countries.

**What exists here:** a public-document endpoint audit for Rwanda 2019–20 and 2025 ([docs/ENDPOINT_AUDIT.md](docs/ENDPOINT_AUDIT.md)); a five-competitor matrix ([docs/PRIOR_ART.md](docs/PRIOR_ART.md)); tested, access-gated utilities (concept schema with timing labels, evidence-gated survey crosswalk, eligibility flow, post-discharge endpoint with explicit clocks and competing death state, leakage guards, outreach-capacity recall); synthetic test fixtures; and logs of every public source fetched.
**What does not exist:** no respondent microdata, no raw-code-verified mapping, no event rates, no trained model, no metrics, no dashboard.

## Research questions (not yet answered)

1. Do the target DHS surveys record a check **after discharge** separately from a check **before leaving the facility**, for both mother and newborn, with usable timing? (Gate 1)
2. Among facility births, can discharge-known information find more of the pairs that miss post-discharge follow-up, at realistic outreach capacity, than simple rules?
3. Does that hold from Rwanda 2019–20 to Rwanda 2025 (temporal) and in Kenya 2022 / Ethiopia 2024–25 (geographic), if the endpoint is comparable?

## What has been verified from public sources (17 Oct 2026)

Full logs: [docs/DATA_ACCESS.md](docs/DATA_ACCESS.md), [docs/ENDPOINT_AUDIT.md](docs/ENDPOINT_AUDIT.md).

- **A distinct post-discharge endpoint exists in both Rwanda waves.** The Rwanda 2019–20 questionnaire (FR370 Appendix F) asks, for facility births only, whether anyone checked the mother "while you were still in the facility" (Q435) and "after you left the facility" (Q441), and the same for the newborn (Q438, Q445). The Rwanda 2025 recode dictionary (NISR, file `RWNR91FL`) has the matching labels: `m62`/`m74` before discharge and `m66`/`m70` after discharge (shared with home deliveries).
- **Post-discharge timing uses the delivery clock** (Q442/Q446; `m67`/`m71`), so a window after discharge needs the stay length (Q431/`m61`). The 2019–20 newborn item counts only health providers or traditional birth attendants within two months of leaving; the mother item counts "anyone", with no time limit.
- **Standard DHS postnatal indicators and the final-report tables do not use these items.** They time the *first* check from birth (50 indicator definitions; FR370 Tables 9.9/9.11), so published PNC coverage cannot be the endpoint.
- **Still unverified:** 2019–20 recode variable names, numeric unit and don't-know codes, Rwanda 2025 questionnaire routing, and all raw values.
- Rwanda 2019–20 (`RW2019DHS`, fieldwork 2019-11 to 2020-07), Rwanda 2025 (`RW2025DHS`, 2025-07 to 2025-11, API release date 2026-08-05), Kenya 2022 (`KE2022DHS`) and Ethiopia 2024–25 (`ET2024DHS`, API release date 2026-07-08) have recode files listed in the DHS Program catalogue ([extract](docs/source_extracts/dhs_api_recode_files.csv)).
- **Uganda 2022 is not listed** in the DHS Program survey or dataset catalogue (latest Uganda DHS listed: `UG2016DHS`). Its distributor and access route must be confirmed with UBOS.
- Kenya's KNBS catalogue lists KDHS 2022 as a public-use dataset under conditions (no redistribution; statistical/research use) but publishes no variable-level metadata.

## Design (frozen before any data is seen)

- **Unit:** mother + most recent live birth, facility delivery, singleton, birth within 24 months of interview, full endpoint window elapsed, newborn alive at **discharge**. Newborns who die after discharge stay in the cohort as a competing `died` state; survivor-only analysis is a separate, explicit sensitivity.
- **Endpoint (per member):** 1 = no check after discharge within *W* days; 0 = check after discharge within *W*; missing = don't know, timing unknown, negative time, a post-discharge check timed before discharge, death before discharge or before a reported check, or a clock conversion that lacks stay length (each with a reason flag; no times imputed). The caller must state the clock of the timing item; an ambiguous clock raises an error. Dyad endpoint = at least one of mother or newborn missed (three-valued logic: unknown stays unknown). A pre-discharge check never counts. *W* (candidates 7 or 42 days from birth) is fixed after the raw audit.
- **Predictors:** only information available at discharge. Interview-time measurements (current wealth, residence, marital status, insurance) are rejected by the leakage guard and only allowed as a labelled sensitivity analysis.
- **Planned comparison (only after Gate 1 passes on real data):** simple triage rules, prevalence, weighted regularised logistic, one tree ensemble; Rwanda 2019–20 → 2025 temporal test; leave-one-country-out only if comparable; cluster-aware uncertainty. Primary metric: missed pairs captured at actual outreach capacity.

Details: [docs/SCIENTIFIC_PROTOCOL.md](docs/SCIENTIFIC_PROTOCOL.md).

## Status

| Dimension | Status |
|---|---|
| Data access | `HOLD_ACCESS` — no approved respondent data in this environment |
| Endpoint existence | Verified from Rwanda questionnaire and dictionary |
| Endpoint validity | Codes, skips, don't-know rates and 2019–20 variable names unverified |
| Scientific novelty | Conditional; closest same-dataset competitor (Kubahoniyesu 2026) checked at abstract depth only ([docs/PRIOR_ART.md](docs/PRIOR_ART.md)) |
| AI incremental value | Not tested |
| Readiness | Not ready for protocol or manuscript |

See [docs/STATUS.md](docs/STATUS.md) and the [minimum access request](docs/ACCESS_REQUEST.md).

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/python -m pytest -q          # 60 tests, synthetic fixtures only
```

Re-creating the source extracts requires re-fetching the three DHS API URLs in [docs/DATA_ACCESS.md](docs/DATA_ACCESS.md) to a directory outside the repository, then:

```bash
.venv/bin/python -I scripts/extract_public_metadata.py <surveys.json> <datasets.json> <indicators.json> docs/source_extracts
```

## Layout

```
src/mnfollowup/   concepts.py (timing registry) · crosswalk.py (evidence gate) · endpoint.py
                  leakage.py · access.py (approval gate) · metrics.py (capacity recall)
configs/          crosswalk.csv — concept × survey; 10 VERIFIED_LABEL (RW2025), 9 QUESTIONNAIRE_ONLY (RW2019), rest UNVERIFIED
data/samples/     SYNTHETIC_harmonised_dyads.csv — 16 hand-built edge-case rows, not survey data
data/manifests/   source_probe_2026-10-17{,_phase2}.json — every request, status, bytes, sha256
docs/             STATUS, ENDPOINT_AUDIT, DATA_ACCESS, SCIENTIFIC_PROTOCOL, PRIOR_ART, ACCESS_REQUEST, ...
scripts/          extract_public_metadata.py · build_crosswalk.py
tests/            fixture tests for endpoint, eligibility, crosswalk, leakage, access, metrics
```

## Data boundary

No DHS respondent files, audit sheets or individual predictions may be committed or deployed. `access.require_processing_permission` refuses to run without an approval record kept outside the repository, and `access.refuse_repo_path` refuses data paths inside it. DHS data are subject to the DHS Program's terms of use and each country's conditions.

## AI assistance

Code, tests and documents on this branch were drafted with an AI coding assistant (Claude Code) under the investigator's direction and are pending the investigator's review.
