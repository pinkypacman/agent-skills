# Refactor branch (of bulk-review)

Entered only when the owner accepts the offer in step 4 of `SKILL.md`. The owner decides; the
agent prepares the options, asks, writes the spec, and refactors only what was approved.

## Steps

1. **Prepare options.** For each real item, or the group the owner picks, write 1–2 options:
   - what moves where: new functions or files, each with a one-line aim;
   - the trade-off: what gets simpler, what gets more indirect;
   - the risk: which tests cover this code, and what has none;
   - if the folder has a `STRUCTURE.md`: the box(es) before and after.
2. **Ask, one question at a time,** using the `grilling` skill. Lead with your recommended answer.
   Settle, in this order:
   - which items to do now, and which to leave as known debt;
   - which option for each;
   - names of the new functions and files;
   - how behaviour is proven unchanged: existing tests, or a new test written first;
   - the order of the splits.

   Stop asking once every decision has an answer.
3. **Write the refactor spec** in the `spec` skill's format. The aim is "same behaviour, smaller
   units". Acceptance: the tests pass, `measure.py --since <base>` passes, and `structure.py check`
   passes. Place it where the `spec` skill says (existing ticket, new ticket, or the conversation).
4. **Wait for approval of the spec.** Then do one split at a time:
   - make the split;
   - run the tests;
   - re-measure;
   - update `STRUCTURE.md` with the structure skill.
5. **Hand off** three things: the before/after figure, the `measure.py --since <base>` output, and
   the test results.

**Done when** every approved split is in, all acceptance checks pass, and anything not done is
listed as known debt with the owner's reason.
