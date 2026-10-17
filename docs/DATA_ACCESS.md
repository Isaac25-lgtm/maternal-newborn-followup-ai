# Data access: what was actually fetched

Checkpoint date: 2026-10-17. Rule: at most 3 ordinary requests per host, short timeouts, public catalogue and documentation only, no login, no respondent data. Machine-readable log with sha256 per response: [`data/manifests/source_probe_2026-10-17.json`](../data/manifests/source_probe_2026-10-17.json).

## Requests

| Host | # | What | HTTP | Bytes | Used |
|---|---|---|---|---|---|
| dhsprogram.com | 1 | `methodology/survey/survey-display-554.cfm` | 200 | 57,457 | Reachability only; body discarded |
| dhsprogram.com | 2 | `pubs/pdf/FR370/FR370.pdf` | 200 | 14,694,544 | Reachability only; body discarded, **contents not inspected** |
| dhsprogram.com | 3 | guessed DHS-8 woman's questionnaire PDF URL | 404 | 103 | — |
| api.dhsprogram.com | 1 | `rest/dhs/surveys` (RW, UG, KE, ET; DHS) | 200 | 22,316 | Fieldwork and release dates |
| api.dhsprogram.com | 2 | `rest/dhs/indicators` (all 4,655) | 200 | 1,645,497 | Postnatal indicator definitions |
| api.dhsprogram.com | 3 | `rest/dhs/datasets` (RW, KE, UG, ET) | 200 | 639,140 | Recode file names and dates |
| microdata.worldbank.org | 1 | catalogue search, DHS, RWA/UGA/KEN ≥2019 | 200 | 22,715 | Study IDs |
| microdata.worldbank.org | 2 | `RWA_2019_DHS_v01_M/variables` | 200 | 10,351 | 3,053 variables exist; only first 100 (household recode) returned |
| microdata.worldbank.org | 3 | `RWA_2025_DHS_v01_M/variables` | 200 | 9,875 | 9,260 variables exist; only first 100 returned |
| microdata.statistics.gov.rw | 1 | guessed NADA API search path | 404 | 539 | Path guess failed; not evidence of unavailability |
| statistics.knbs.or.ke | 1 | NADA catalogue search | 200 | 9,978 | KDHS 2022 study ID |
| statistics.knbs.or.ke | 2 | KDHS 2022 variables | 200 | 26 | `total: 0` |
| statistics.knbs.or.ke | 3 | KDHS 2022 study metadata | 200 | 14,743 | Access conditions |

**Procedural error to record:** the first two dhsprogram.com requests were made as reachability probes with the body discarded, which used that host's budget before any questionnaire or recode manual could be saved. No questionnaire, recode manual or final report was inspected in this checkpoint.

## Findings from the saved responses

1. **Indicator definitions (DHS API).** 50 indicator records match "postnatal" ([extract](source_extracts/dhs_api_postnatal_indicator_definitions.csv)). Timing indicators define the *first* postnatal checkup relative to **birth** (mother: <4 h, 4–23 h, 1–2 d, 3–6 d, 7–41 d, none in 42 d; newborn: <1 h, 1–3 h, 4–23 h, 1–2 d, 3–6 d, none in 7 d). None mentions discharge. They therefore cannot serve as a post-discharge endpoint.
2. **Source anomaly (DHS API).** `RH_PCMN_W_MNB` is labelled "Mother and newborn received postnatal check in first two days" but its definition text says "neither … received"; `RH_PCMN_W_NMN` is labelled "Neither …" but its definition describes the mother receiving a check. Labels and definitions appear swapped. Do not use these indicators without checking the published tables.
3. **Survey dates (DHS API)** ([extract](source_extracts/dhs_api_surveys_RW_UG_KE_ET.csv)):

   | Survey | Fieldwork | API release date |
   |---|---|---|
   | RW2019DHS | 2019-11-01 – 2020-07-01 | 2021-10-04 |
   | RW2025DHS | 2025-07-01 – 2025-11-01 | 2026-08-05 |
   | KE2022DHS | 2022-02-01 – 2022-07-01 | 2023-07-03 |
   | ET2024DHS | 2024-08-01 – 2025-04-01 | 2026-07-08 |
   | UG2016DHS | 2016-06-01 – 2016-12-01 | 2018-03-12 |

4. **Recode files listed (catalogue only, not downloaded)** ([extract](source_extracts/dhs_api_recode_files.csv)): Rwanda 2019–20 `RWIR81DT.ZIP` (individual, 8,467,614 bytes, modified 2021-09-21), `RWBR81DT.ZIP`; Rwanda 2025 `RWIR91DT.zip` (8,833,346 bytes, modified 2026-07-20), `RWBR91DT.zip`; Kenya 2022 `KEIR8CDT.ZIP`; Ethiopia 2024–25 `ETIR8ADT.zip`. Listing a file is not access to it: DHS Program downloads require a registered, approved project.
5. **Uganda 2022 not in DHS Program catalogue.** Neither the surveys endpoint (`surveyType=DHS`) nor the dataset endpoint lists a Uganda DHS after `UG2016DHS` ([survey IDs](source_extracts/dhs_api_dataset_survey_ids.txt)). Access route must be confirmed with UBOS before Uganda can be a validation set.
6. **World Bank Microdata Library** lists `RWA_2019_DHS_v01_M` (3,053 variables), `RWA_2025_DHS_v01_M` (9,260 variables) and `KEN_2022_DHS_v01_M` (3,017 variables), all `form_model: remote` (data obtained from the external distributor). The variable endpoint is paginated (100 per page) and only household-recode variables were returned within budget, so **no maternal or newborn postnatal variable label has been seen**.
7. **KNBS** lists KDHS 2022 as `data_access_type: public`, "anonymized … Public Use Dataset … for statistical and research purposes only", with no redistribution. No variable metadata (`varcount: 0`). Metadata anomaly: its `doc_desc/title` reads "2021 FINACCESS HOUSEHOLD SURVEY".

## Not accessed

Respondent microdata of any survey; DHS questionnaires and recode manuals; national final reports; NISR and UBOS catalogues (beyond one failed NISR path); Ethiopia national catalogue.

## Next bounded fetch (no permission needed beyond ordinary public access)

In a fresh session with fresh host budget, save (not discard) and hash: the Rwanda 2019–20 and 2025 questionnaires and final reports from dhsprogram.com, and the DHS-7/DHS-8 recode manuals; then read the postnatal section and record verbatim item wording and recode variable labels into `configs/crosswalk.csv` as `VERIFIED_LABEL` with URL and quote. Alternatively page the World Bank variable endpoint (`?offset=`) to reach the women's file labels.

## Public phase 2 (same day, 13 further requests)

Log: [`data/manifests/source_probe_2026-10-17_phase2.json`](../data/manifests/source_probe_2026-10-17_phase2.json). No cached FR370 existed (phase-1 body was discarded), so it was fetched once and hashed.

| # | Host | What | HTTP | Result |
|---|---|---|---|---|
| 1–2 | microdata.statistics.gov.rw | Rwanda DHS 2025 file F9 `RWNR91FL` dictionary, offsets 600, 700 | 200 | Labels m15–m19a, m61–m78p read |
| 3 | microdata.statistics.gov.rw | catalogue search | 200 | 2019-20 DHS not among listed results |
| 4 | dhsprogram.com | FR370.pdf, 14,694,544 bytes, sha256 `f85ad981…c5f6fa` | 200 | Confirmed Rwanda DHS 2019-20 Final Report; questionnaire Q430–Q449 read |
| 5–7 | microdata.worldbank.org | RWA_2019 variables with `limit`/`offset` | 200 | Parameters ignored (identical body); 2019-20 recode names not reached |
| 8–11 | doi.org → link.springer.com | four BMC articles | 200 | Bot-check page only (3,038 bytes) |
| 12 | doi.org → bmjopen.bmj.com | Pillay 2026 | 403 | Refused |
| 13 | www.ebi.ac.uk (Europe PMC REST) | five DOIs | 200 | Five records with abstracts |

**Correction:** finding 1 above (standard indicators time the first check from birth) is correct but does not show the endpoint is unavailable. The questionnaire and 2025 dictionary contain separate after-discharge items; see [ENDPOINT_AUDIT.md](ENDPOINT_AUDIT.md).
