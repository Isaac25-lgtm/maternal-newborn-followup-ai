# Endpoint audit: public questionnaire and codebook evidence

Date 2026-10-17. Public documents only; no respondent records. Request log: [`data/manifests/source_probe_2026-10-17_phase2.json`](../data/manifests/source_probe_2026-10-17_phase2.json). Machine-readable mapping: [`configs/crosswalk.csv`](../configs/crosswalk.csv) (built by `scripts/build_crosswalk.py`).

**Correction to checkpoint 1.** Checkpoint 1 showed only that the DHS *standard indicators* time the first postnatal check from birth. That was not evidence about the questionnaires. Both Rwanda surveys do ask **separately** about checks before and after leaving the facility, for mother and newborn.

## Sources read

| ID | Source | Identity check | Location |
|---|---|---|---|
| S1 | Rwanda DHS 2019-20 Final Report FR370, `https://dhsprogram.com/pubs/pdf/FR370/FR370.pdf`, 14,694,544 bytes, sha256 `f85ad9814654973189b675a64fb931eaf28a6b419268f2b5c607ed6675c5f6fa` | PDF title "Rwanda Demographic and Health Survey 2019-20 Final Report [FR370]", 619 pages | Appendix F, Woman's Questionnaire Section 4, printed pp. 446–449 (PDF p. 479 = printed 447) |
| S2 | NISR microdata catalogue, Rwanda DHS 2025 (catalog 126), file F9 `RWNR91FL- Pregnancy and Postnatal Care (last 3 yrs) Recode` | Page title "Rwanda - Rwanda Demographic and Health Survey 2025 - data_file - F9" | Dictionary offsets 600 and 700 |

## Verified: Rwanda 2019–20 questionnaire (S1), recode names NOT verified

| Item | Verbatim wording (short) | Routing / coding as printed | Concept |
|---|---|---|---|
| Q430 | "Where did you give birth to (NAME)?" | Her home 11, other home 12 → skip to 434; public 21–26, private 31–36, other 96 → skip to 434 | `facility_delivery` |
| Q431 | "How long after (NAME) was delivered did you stay there?" | HOURS 1 / DAYS 2 / WEEKS 3; DON'T KNOW 998 | `facility_stay_days` |
| Q434B | "CHECK 430: PLACE OF DELIVERY" | Codes 11, 12 or 96 → skip to 449 (non-facility path) | facility filter |
| Q435 | "…Did anyone check on your health while you were still in the facility?" | YES 1 / NO 2 (→438); **no DON'T KNOW code printed** | `mother_check_before_discharge` |
| Q436 | "How long after delivery did the first check take place?" | HOURS/DAYS/WEEKS; DK 998 | (pre-discharge timing) |
| Q438 | "…Did anyone check on (NAME)'s health while you were still in the facility?" | YES 1 / NO 2 (→441) / DK 8 | `newborn_check_before_discharge` |
| Q439 | "How long after delivery was (NAME)'s health first checked?" | HOURS/DAYS/WEEKS; DK 998 | (pre-discharge timing) |
| Q441 | "Now I want to talk to you about what happened after you left the facility. Did anyone check on your health after you left the facility?" | YES 1 / NO 2 (→445); **no DK code printed**; no time limit in wording | `mother_check_after_discharge` |
| Q442 | "How long after delivery did that check take place?" | HOURS/DAYS/WEEKS; DK 998 — **clock = delivery** | `mother_after_discharge_check_day` |
| Q443–444 | Who checked; where | Provider codes 11–23, 96; place codes 11–36, 96 | (not yet in registry) |
| Q445 | "Did any health care provider or a traditional birth attendant check on (NAME)'s health in the two months after you left (FACILITY IN 430)?" | YES 1 / NO 2 (→457) / DK 8 | `newborn_check_after_discharge` |
| Q446 | "How many hours, days or weeks after the birth of (NAME) did that check take place?" | HOURS/DAYS/WEEKS; DK 998 — **clock = birth** | `newborn_after_discharge_check_day` |
| Q447–448 | Who checked; where | as Q443–444 | (not yet in registry) |
| Q449 | "…Did anyone check on your health after you gave birth to (NAME)?" | Non-facility path | not part of endpoint |

The final report's Tables 9.9 and 9.11 tabulate the *first* postnatal check by time after delivery (footnotes: maternal includes checks after 41 days; newborn includes checks after the first week). Their titles and footnotes do not separate pre- from post-discharge checks, consistent with the standard indicators.

## Verified: Rwanda 2025 recode labels (S2), codes NOT verified

| Variable | Dictionary label (as displayed) | Concept |
|---|---|---|
| m15 | place of delivery | `facility_delivery` (derivation pending code list) |
| m17 | delivery by caesarean section | `caesarean_delivery` |
| m18 | size of child at birth | `reported_birth_size` |
| m61 | time spent at place of delivery | `facility_stay_days` |
| m62 | respondent's health checked after delivery before discharge | `mother_check_before_discharge` |
| m63 | how long after delivery respondent's health check before discharge took place | (pre-discharge timing) |
| m64 | who checked respondent's health before discharge | — |
| m66 | respondent's health checked after discharge/delivery at home | `mother_check_after_discharge` |
| m67 | how long after delivery respondent's health check (after discharge/home delivery *[truncated]* | `mother_after_discharge_check_day`, clock = delivery |
| m68 | who checked respondent's health after discharge/delivery at home | — |
| m69 | where respondent's check after discharge/delivery at home took place | — |
| m70 | child's health checked after discharge/delivery at home | `newborn_check_after_discharge` |
| m71 | how long after delivery child's health check (after discharge/home delivery) too *[truncated]* | `newborn_after_discharge_check_day`, clock = delivery |
| m72 | who checked child's health after discharge/home delivery | — |
| m73 | where child's health check after discharge/home delivery took place | — |
| m74 | child's health checked before discharge | `newborn_check_before_discharge` |
| m75 | how long after delivery child's health check before discharge took place | (pre-discharge timing) |
| m76 | who checked child's health before discharge | — |
| m78a–h | during first 2 days health provider: examine cord / measure temperature / signs baby needs medical attention / counsel on breastfeeding / observe breastfeeding / measure blood pressure / discuss vaginal bleeding / discuss family planning | PNC content (Kawuki-type outcome); not the endpoint |

## Consequences for the endpoint

1. **A distinct post-discharge endpoint exists** in both Rwanda waves (2019-20 Q441/Q445; 2025 m66/m70), so the project is not blocked on endpoint existence.
2. **Facility restriction is essential.** In 2025 the after-discharge variables are shared with home deliveries ("after discharge/delivery at home"); in 2019-20 home/other births are routed to Q449. The cohort must be facility births only.
3. **Timing is on the delivery clock.** Q442, Q446, m67 and m71 time the post-discharge check from delivery/birth. A window "within *W* days after discharge" needs the stay length (Q431 / m61), which is recorded in hours/days/weeks with DK. `endpoint.missed_followup` requires the caller to state `check_clock` and `window_from` and returns unknown when the conversion is impossible or inconsistent.
4. **Mother and newborn items are not symmetric (2019-20).** Mother: "anyone", no time limit. Newborn: "any health care provider or a traditional birth attendant", "in the two months after you left". A dyad endpoint must use a window ≤ ~2 months after discharge and accept different provider scopes, or analyse members separately.
5. **Don't-know handling differs.** Q435 and Q441 print no DK code; Q438 and Q445 do. Recode missing-value codes are unverified.

## Unresolved (must stay unverified until the stated evidence is seen)

| Question | Evidence needed |
|---|---|
| Rwanda 2019-20 recode variable names for Q431–Q446 (RWIR81) | 2019-20 recode dictionary or DHS-8 recode manual (not reachable: World Bank API ignores `limit`/`offset`; 2019-20 not in NISR search results) |
| Numeric encoding of time units in m61/m63/m67/m71/m75 and missing codes | Variable-level value labels (NISR variable pages) or recode manual |
| Rwanda 2025 questionnaire wording, routing and whether the mother item has a time limit | 2025 questionnaire / final report |
| Whether section 4 PNC items apply to the last birth only (the 2019-20 next-to-last column skips at Q434) | Full Section 4 routing review, recode data |
| Recall period: 2019-20 tables use births in 2 years; the 2025 file is "last 3 yrs" | Recode and report documentation |
| Measurability of newborn alive at discharge (age at death in days vs stay length) | Birth history recode labels |
| Kenya 2022, Ethiopia 2024-25 equivalents; Uganda 2022 access route | Questionnaires / dictionaries; UBOS |
| Actual codes, skips, inconsistencies and twin handling | 50-dyad raw audit in approved data only |
