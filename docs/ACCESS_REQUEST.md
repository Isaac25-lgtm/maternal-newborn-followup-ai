# Minimum data authorisation request

Public documentation has now established that a distinct post-discharge endpoint exists in both Rwanda waves ([ENDPOINT_AUDIT.md](ENDPOINT_AUDIT.md)). What it cannot establish is the coded values, skips and don't-know rates, which needs respondent data. Still-essential permissions only:

> **Investigator (Isaac Omoding):** confirm whether you hold an **approved DHS Program project** covering **Rwanda DHS 2019–20 Individual Recode `RWIR81DT.ZIP`** (catalogue size 8,467,614 bytes). If yes, authorise in writing:
>
> 1. delivery of that **one file** to a **private location outside this Git repository**, in a named environment that your DHS approval and institutional ethics allow (state whether this cloud container qualifies);
> 2. **one purpose**: Gate 1 audit of 50 eligible facility-birth dyads — codes and units of the after-discharge items, stay length, don't-know codes, skip logic, last-birth applicability, twins, weights and design variables;
> 3. outputs limited to **aggregate, non-identifying** counts and code; no records, audit sheets or individual predictions committed or shared.
>
> Provide an approval record (JSON outside the repository) with `investigator`, `approving_body`, `approval_reference`, `approved_purpose`, `survey_ids`, `approved_environment`, `expires_on`, and set `MNF_APPROVAL_RECORD` to its path.

If no DHS project exists: register one requesting Rwanda 2019–20 and Rwanda 2025 for this aim.

**Deferred (not requested now):** Rwanda 2025 file (`RWNR91FL` / `RWIR91`) until 2019–20 passes Gate 1; Kenya 2022 and Ethiopia 2024–25 until their questionnaires are checked; Uganda 2022 until UBOS confirms the access route. **Never requested:** GPS/cluster coordinates, men's file, linkage, public deployment.

No permission is needed for the remaining public step (2019–20 recode variable names and unit codes from the DHS recode manual or a dictionary).
