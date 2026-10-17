# Data: acquisition and permission matrix

No respondent microdata is stored in this repository or was accessed in this environment. Raw, restricted and processed data directories (`data/raw/`, `data/restricted/`, `data/processed/`, `data/audit/`) are git-ignored, and `mnfollowup.access.refuse_repo_path` rejects data paths inside the repository.

| Survey | Role | Distributor (as listed) | Catalogue evidence | Access status here |
|---|---|---|---|---|
| Rwanda DHS 2019–20 (`RW2019DHS`) | Development | DHS Program | Recode files listed, DHS API 2026-10-17 | Not approved / not fetched |
| Rwanda DHS 2025 (`RW2025DHS`) | Temporal test | DHS Program | Recode files listed; API release 2026-08-05 | Not approved / not fetched |
| Kenya DHS 2022 (`KE2022DHS`) | Geographic test (if comparable) | DHS Program; KNBS lists as public-use | DHS API; KNBS NADA | Not approved / not fetched |
| Ethiopia DHS 2024–25 (`ET2024DHS`) | Later geographic test | DHS Program | Recode files listed; API release 2026-07-08 | Not approved / not fetched |
| Uganda DHS 2022 | Geographic test (if obtainable) | **Not listed by DHS Program**; confirm with UBOS | Absent from DHS API | Route unknown |

- `samples/SYNTHETIC_harmonised_dyads.csv` — 12 hand-built rows for tests. Every row has `synthetic_record = SYNTHETIC_NOT_REAL`. Not derived from any survey.
- `manifests/source_probe_2026-10-17.json` — every catalogue request made, with HTTP status, bytes and sha256.
