# Loop state

The loop state is how `resume` works: everything needed to continue lives on the ticket, not in a session. It is one collapsed toggle at the **end of the ticket's Hand-off section**, titled `Loop state (ticket-loop)`. Rewrite it after every phase and every round.

## Format

Plain bullet lines only, with no tables and no `|` in any line, so that the tracker's text-matching update can anchor on each line:

```markdown
- **phase:** <1 claim · 2 design · 3 prepare · 4 checkpoint-1 · 5.<r> implement|run|review|fix · 6 checkpoint-2 · stopped> · updated <date time>
- **round:** hand-off round <r> of <cap> (round 0 = design)
- **workdir:** `<path>`
- **branch:** `<branch>` · worktree `<path>` · base `<base>` at <sha> (or "shared checkout")
- **recommendation:** <row> — orchestrator <model·effort>, developer <…>, reviewers <…>, recomputer <…>, ultracode <on/off>, cap <N>
- **owner choice:** `<reply verbatim>` on <date>; orchestrator ran <model id>
- **decisions:** <n>=<answer> (recommended / owner), one per Checkpoint 1 decision
- **launch gate:** branch HEAD <sha> · shared imported code hashed `<workdir>/launch_hashes.sha256` · cards <ids>
- **jobs:** <task id> · <log path> · started <time> · <running/exited n>
- **snapshot:** `<workdir>/r<r>/snapshot.sha256` · <verified / pending>
- **design:** <verdict>; wording applied: <list>
- **D0.<n>** · <Blocker/Fix/Optional> · `<path:line or AC n>` · <claim, ≤ 15 words> · <wording / plan gap / owner question / optional> · <applied / answered in sketch / decision n / built (round r) / not built>
- **F<r>.<n>** · <Blocker/Fix/Optional> · `<path:line>` · <claim, ≤ 15 words> · <open/resolved/waived/outside → KEY> · fixes <k> · same as <F…, or "new">
- **stop:** <S1–S5 name, one line why; or "none yet">
```

**Matching findings:** a finding is the *same* as an earlier one (an F or a D0 line) when it names the same file (the same function, or a line within a few lines) and the same claim. Record `same as <id>` and carry the fix count forward; only fix rounds count as fixes, not the prepare phase. That count is what S3 reads.

## Resume

1. Fetch the ticket and read the toggle. If it is missing, stop: "no loop state; start with `/ticket-loop <KEY>`".
2. Re-query the blockers and the In Progress tickets. Re-read both configs.
3. Continue from the recorded phase:

| Recorded phase | Resume by |
|---|---|
| 1–3 | redo that phase (it is idempotent: nothing is launched yet) |
| 4 checkpoint-1 | re-print the card and wait (the reply may come in the new session) |
| 5.r run, jobs running | check each job is alive (process, log tail); re-arm the background monitor; on a dead job, read its log and treat it as an exit |
| 5.r implement | compare the branch's commits and the worktree's `git status` with the sketch's file map; give a new developer the sketch and what already exists |
| 5.r review | rerun the round with a fresh arbiter (reviews are read-only) |
| 5.r fix | compare `git status` / hashes of the Owns paths with the snapshot; give a new developer the round's open findings and what already changed |
| 6 / stopped | print the Checkpoint 2 summary; nothing more to do |
