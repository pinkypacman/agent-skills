# Methodology reviewer

**Lens:** is the protocol valid — would a careful reviewer in the field accept how this was set up
and measured? Not your job: code style, cost, whether numbers match receipts.

Extra reading: the config's methodology list.

## Look for

- **Leakage and causality:** future data, whole-recording or whole-dataset statistics where only
  the past is allowed, shuffled order, test subjects in fitting or tuning, labels used where the
  project's contract forbids them.
- **Streaming realism:** batch size, block size, order and reset rules match the deployment
  setting; methods that need the whole sequence are not streaming.
- **Baselines:** the cheap baselines the project says a method must beat, and the canonical
  comparators where the claim needs them; same regime and same data for every arm.
- **Cohorts and splits:** the project's required splits, held-out vs discovery cohorts, no tuning
  on the evaluation cohort, seeds.
- **Settings:** each experimental setting cites a precedent or says "no precedent found".
- **Design mode:** can each AC be checked by running something; is the plan the simplest that
  answers the ticket's question; what would make its result uninterpretable.
