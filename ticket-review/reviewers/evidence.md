# Evidence & claims reviewer

**Lens:** does every stated result and verdict follow from the receipts? Not your job: whether
the protocol was the right one, code quality.

Extra reading: the config's evidence list, and the receipts and result files the ticket names.

## Look for

- **Recompute:** pick the numbers the conclusion rests on and recompute them read-only from the
  result files or receipts. A mismatch is a Blocker.
- **Claims vs tables:** every sentence in the TL;DR and Hand-off is supported by a table cell; no
  conclusion that flips inside the project's threshold range.
- **Completeness:** the project's required metric set at every required threshold; required
  subgroups reported separately; the no-op or abstain rate where a rule can decline to act.
- **Denominators and aggregation:** units weighted as registered, seeds averaged as registered,
  counts with their denominators, no ratio with a near-zero denominator.
- **Labels:** numbers computed with held-out labels are marked as the project requires;
  correlations of a change with its own baseline are corrected for regression to the mean or not
  claimed.
- **Design mode:** does each AC name the number, table or file that will prove it.
