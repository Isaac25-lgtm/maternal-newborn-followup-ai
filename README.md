# Mother–newborn post-discharge follow-up (R03)

Investigator: Isaac Omoding · Research programme R03 · **Status: `HOLD_ACCESS`**

After a facility birth, mothers and newborns are discharged into the period when most maternal and neonatal deaths happen. If programmes can only call or visit some of them, they need to know at discharge which pairs are least likely to get a check after they leave. This project asks whether information available at discharge can rank facility-delivered mother–newborn pairs by their risk of having **no health check after discharge**, and whether that ranking still holds in a later survey wave and in other countries.

**What exists here:** tested, access-gated utilities (concept schema with timing labels, survey crosswalk with an evidence gate, eligibility flow, post-discharge endpoint logic, predictor-leakage guards, outreach-capacity recall), synthetic test fixtures, and a log of public catalogue sources actually fetched.
**What does not exist:** no respondent microdata, no verified source-variable mapping, no event rates, no trained model, no metrics, no dashboard.

## Research questions (not yet answered)

1. Do the target DHS surveys record a check **after discharge** separately from a check **before leaving the facility**, for both mother and newborn, with usable timing? (Gate 1)
2. Among facility births, can discharge-known information find more of the pairs that miss post-discharge follow-up, at realistic outreach capacity, than simple rules?
3. Does that hold from Rwanda 2019–20 to Rwanda 2025 (temporal) and in Kenya 2022 / Ethiopia 2024–25 (geographic), if the endpoint is comparable?

## What this checkpoint verified (17 Oct 2026)

From the DHS Program API and national/World Bank catalogues (full log: [docs/DATA_ACCESS.md](docs/DATA_ACCESS.md)):

- **Standard DHS postnatal indicators do not measure post-discharge follow-up.** All 50 indicator records matching "postnatal" define the *first* postnatal checkup timed from **birth** (e.g. `RH_PCMT_W_DY2`, `RH_PCCT_C_DY2`) and never mention discharge. For facility births the first check is usually the pre-discharge one, so published PNC coverage cannot be the endpoint. Whether the recode files carry separate after-discharge items is **not yet verified**.
- Rwanda 2019–20 (`RW2019DHS`, fieldwork 2019-11 to 2020-07), Rwanda 2025 (`RW2025DHS`, 2025-07 to 2025-11, API release date 2026-08-05), Kenya 2022 (`KE2022DHS`) and Ethiopia 2024–25 (`ET2024DHS`, API release date 2026-07-08) have recode files listed in the DHS Program catalogue ([extract](docs/source_extracts/dhs_api_recode_files.csv)).
- **Uganda 2022 is not listed** in the DHS Program survey or dataset catalogue (latest Uganda DHS listed: `UG2016DHS`). Its distributor and access route must be confirmed with UBOS.
- Kenya's KNBS catalogue lists KDHS 2022 as a public-use dataset under conditions (no redistribution; statistical/research use) but publishes no variable-level metadata.

## Design (frozen before any data is seen)

- **Unit:** mother + most recent live birth, facility delivery, singleton, birth within 24 months of interview, full endpoint window elapsed, newborn alive at window end (selection on survival is recorded as a limitation).
- **Endpoint (per member):** 1 = no check after discharge within *W* days; 0 = check after discharge within *W*; missing = don't know / timing unknown. Dyad endpoint = at least one of mother or newborn missed (three-valued logic: unknown stays unknown). A pre-discharge check never counts. *W* (e.g. 7 or 42 days) is fixed after Gate 1 shows what timing the questionnaires capture.
- **Predictors:** only information available at discharge. Interview-time measurements (current wealth, residence, marital status, insurance) are rejected by the leakage guard and only allowed as a labelled sensitivity analysis.
- **Planned comparison (only after Gate 1 passes on real data):** simple triage rules, prevalence, weighted regularised logistic, one tree ensemble; Rwanda 2019–20 → 2025 temporal test; leave-one-country-out only if comparable; cluster-aware uncertainty. Primary metric: missed pairs captured at actual outreach capacity.

Details: [docs/SCIENTIFIC_PROTOCOL.md](docs/SCIENTIFIC_PROTOCOL.md).

## Status

| Dimension | Status |
|---|---|
| Data access | `HOLD_ACCESS` — no approved respondent data in this environment |
| Endpoint validity | Unverified; standard indicators shown unsuitable; recode items not yet checked |
| Scientific novelty | Not assessed; competitor audit not done ([docs/PRIOR_ART.md](docs/PRIOR_ART.md)) |
| AI incremental value | Not tested |
| Readiness | Not ready for protocol or manuscript |

See [docs/STATUS.md](docs/STATUS.md) and the [minimum access request](docs/ACCESS_REQUEST.md).

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/python -m pytest -q          # 27 tests, synthetic fixtures only
```

Re-creating the source extracts requires re-fetching the three DHS API URLs in [docs/DATA_ACCESS.md](docs/DATA_ACCESS.md) to a directory outside the repository, then:

```bash
.venv/bin/python -I scripts/extract_public_metadata.py <surveys.json> <datasets.json> <indicators.json> docs/source_extracts
```

## Layout

```
src/mnfollowup/   concepts.py (timing registry) · crosswalk.py (evidence gate) · endpoint.py
                  leakage.py · access.py (approval gate) · metrics.py (capacity recall)
configs/          crosswalk.csv — every concept × survey, all UNVERIFIED, no source variables
data/samples/     SYNTHETIC_harmonised_dyads.csv — 12 hand-built rows, not survey data
data/manifests/   source_probe_2026-10-17.json — every request, status, bytes, sha256
docs/             STATUS, DATA_ACCESS, SCIENTIFIC_PROTOCOL, PRIOR_ART, ACCESS_REQUEST, ...
scripts/          extract_public_metadata.py
tests/            fixture tests for endpoint, eligibility, crosswalk, leakage, access, metrics
```

## Data boundary

No DHS respondent files, audit sheets or individual predictions may be committed or deployed. `access.require_processing_permission` refuses to run without an approval record kept outside the repository, and `access.refuse_repo_path` refuses data paths inside it. DHS data are subject to the DHS Program's terms of use and each country's conditions.

## AI assistance

Code, tests and documents on this branch were drafted with an AI coding assistant (Claude Code) under the investigator's direction and are pending the investigator's review.
