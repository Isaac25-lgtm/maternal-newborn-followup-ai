# Minimum data authorisation request

The smallest step that would move R03 past `HOLD_ACCESS`:

> **Investigator (Isaac Omoding):** please confirm whether you hold an **approved DHS Program project** that covers **Rwanda DHS 2019–20 (`RW2019DHS`), Individual Recode, Stata file `RWIR81DT.ZIP`** (catalogue size 8,467,614 bytes). If yes, authorise in writing:
>
> 1. delivery of that **one file** to a **private location outside this Git repository** in a named processing environment (state whether this Claude Code cloud container is acceptable under your DHS approval and institutional ethics, or name another environment);
> 2. processing for **one purpose only**: the Gate 1 endpoint audit of 50 eligible mother–newborn pairs, producing variable-label checks and aggregate counts;
> 3. outputs limited to **aggregate, non-identifying** counts and code; no records, audit sheets or individual predictions committed or shared.
>
> Supply an approval record (JSON, kept outside the repository) with: `investigator`, `approving_body`, `approval_reference`, `approved_purpose`, `survey_ids`, `approved_environment`, `expires_on`, and set `MNF_APPROVAL_RECORD` to its path. `mnfollowup.access.require_processing_permission` checks these fields before any processing.

If no DHS project exists yet: register a project at the DHS Program website requesting Rwanda 2019–20 and Rwanda 2025 (for the temporal test), and state the research aim as in [SCIENTIFIC_PROTOCOL.md](SCIENTIFIC_PROTOCOL.md). Kenya 2022 and Ethiopia 2024–25 are requested only after Rwanda passes Gate 1. Uganda 2022 is not in the DHS Program catalogue; ask UBOS for its access route.

Not requested: household recode, GPS/cluster coordinates, men's file, any other country, any linkage, any public deployment.
