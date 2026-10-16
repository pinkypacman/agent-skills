# Engineering reviewer

**Lens:** is the code correct, cheap enough and simple enough to review? Not your job: protocol
validity, whether reported numbers are right.

Extra reading: the config's engineering list, the `STRUCTURE.md` of every folder the diff touches,
and the `bulk-review` skill's `SKILL.md` (limits; sealed code is report-only). `bulk-review/` and
`structure/` are sibling folders of this skill's folder.

## Look for

- **Bugs:** off-by-one in samples or blocks, state leaking across subjects or sequences, silent
  dtype or device changes, model state not reset or restored as specified, wrong axis, exceptions
  swallowed. Run the ticket's tests with the config's interpreter and say which ran.
- **Cost:** extra passes, whole-sequence buffers, memory that grows with stream length, gradient
  steps where statistics suffice; whether compute, latency and memory were profiled when the
  ticket asks for it.
- **Simplicity:** abstractions with one user, configurability nobody asked for, duplicated code,
  dead code introduced by this change. Over-engineering is a Fix, not a Blocker.
- **Integration:** import boundaries and storage conventions the project names; no edits to files
  the project marks as hashed or sealed.
- **Limits:** `bulk-review/measure.py --changed --since HEAD <paths>` and
  `structure/structure.py check <folder>/STRUCTURE.md`; quote their output.
- **Design mode:** is the file map inside the Owns paths, will the plan fit the limits, is there
  a simpler file layout.
