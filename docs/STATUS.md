# R03 evidence status

Last updated 2026-10-17 (cloud checkpoint 1).

**Scientific decision: `HOLD_ACCESS`.**

| Dimension | Status | Evidence |
|---|---|---|
| Data access | No approved respondent data in this environment; none requested or transferred | [DATA_ACCESS.md](DATA_ACCESS.md) |
| Endpoint validity | DHS standard PNC indicators shown unsuitable (timed from birth, no discharge distinction). Recode/questionnaire after-discharge items **not yet seen** | DHS API indicator definitions |
| Survey availability | RW2019DHS, RW2025DHS, KE2022DHS, ET2024DHS listed by DHS Program; UG2022 **not listed** | DHS API datasets |
| Scientific novelty | Not assessed | [PRIOR_ART.md](PRIOR_ART.md) |
| AI incremental value | Not tested | — |
| Readiness | Not protocol- or manuscript-ready | — |

## Done in this checkpoint

- Environment probe: Claude Code cloud container, Python 3.13.16, 4 vCPU, 15 GiB RAM; outbound HTTPS via proxy; PyPI reachable.
- 13 public catalogue requests across 5 hosts, logged with status, bytes, sha256 ([manifest](../data/manifests/source_probe_2026-10-17.json)).
- Package `mnfollowup`: concept/timing registry, evidence-gated crosswalk, eligibility flow, post-discharge endpoint, leakage guards, access gate, capacity recall.
- `configs/crosswalk.csv`: 31 concepts × 5 surveys, all `UNVERIFIED`, no source variable asserted.
- 27 tests on synthetic fixtures pass (`python -m pytest -q`).

## Not done

- No questionnaire, recode manual or final report inspected (host budget used by probes; see procedural note in DATA_ACCESS.md).
- No source-variable mapping, no 50-dyad audit, no event rates, no models, no metrics, no dashboard.
- Competitor audit not started.

## Blockers and next steps

1. Public, no permission needed: fetch and save questionnaires and recode manuals; fill `VERIFIED_LABEL` crosswalk rows with verbatim labels and URLs.
2. Competitor audit (five named works).
3. Investigator action: [ACCESS_REQUEST.md](ACCESS_REQUEST.md).
