# Data dictionary

No survey variable has been observed or audited. The harmonised concepts, their roles and timing are defined in [`src/mnfollowup/concepts.py`](../src/mnfollowup/concepts.py). Their mapping to source variables per survey is [`configs/crosswalk.csv`](../configs/crosswalk.csv), currently all `UNVERIFIED`.

Crosswalk status levels:

- `UNVERIFIED` — concept defined, no source variable asserted (validator rejects a variable here).
- `VERIFIED_LABEL` — source file, variable, verbatim official label and URL recorded from a public questionnaire, recode manual or catalogue.
- `VERIFIED_RAW_AUDIT` — codes, skips and missing values checked on 50 eligible dyads in approved data. Required by `crosswalk.require_endpoint_ready` before endpoint derivation for modelling.

Timing concepts (`*_after_discharge_check_day`) also need `timing_reference` = `birth` or `discharge`.
