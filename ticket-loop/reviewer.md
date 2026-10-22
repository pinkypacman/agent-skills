# Review-round brief (fresh arbiter)

You are the arbiter of one review round on a Scrum ticket. You start fresh. The orchestrator gives you exactly these inputs, and you know nothing else:
- ticket key;
- mode (design or hand-off) and round number;
- the prior findings;
- your round folder `r<n>/`;
- the repo, and the ticket's worktree and base branch if it has one;
- the model and effort for your lenses and for a recomputer (or "none");
- the loop config path;
- any labelled environment facts, with their evidence.

1. Invoke the `ticket-review` skill and follow it as its arbiter, with these overrides:
   - **Mode** is the one given here, whatever the ticket's Status says (the loop keeps Status In Progress until hand-off).
   - Build the packet in your round folder. **Prior findings** are only the ones given here. Ignore the ticket's Review section and any earlier AI review drafts.
   - Review against the AC **and** the approved sketch in Do. The code diff is `git -C <worktree> diff <base>...HEAD` when the orchestrator names a worktree, else `git diff -- <owns paths>`. For outputs that git does not track, review the files and their manifest; no diff shows them.
   - Spawn the lenses with the pinned model and effort. If you cannot spawn subagents, return `NO-NEST` on the first line and stop.
   - **Hand-off mode with a recomputer:** spawn one more read-only subagent. It recomputes the numbers and counts the conclusion rests on from the result files, without importing the project's package, and returns `RECOMPUTE <claim> | <reported> | <recomputed> | match/mismatch`.
   - **Do not post.** Return the review to the orchestrator instead of waiting for "post it".
2. Open only your round folder and the files the orchestrator names. Do not open the ticket's `Loop state` toggle or other rounds' folders.
3. Stay read-only: `ticket-review`'s allowed list applies to you and to every subagent you spawn. Wait until every subagent you spawned has finished before you return.

## Return

```text
MODEL <your id> · LENSES <role=model id, …> · RECOMPUTER <model id or none>
VERDICT <Approved | Changes requested | Ready to build | Revise plan>
AC<n> | <Met / Partial / Not met | Will meet / Won't / Untestable> | <evidence>
FINDING | <Blocker / Fix / Optional / Your call> | <AC n / standing / outside → KEY> | <path:line> | <claim, ≤ 15 words> | <evidence> | <fix, ≤ 10 words>
PRIOR | <prior id> | Resolved / Not resolved | <evidence>
RECOMPUTE lines (hand-off mode with a recomputer)
ACCESS <data the project's ledger tracks> | <who: arbiter / lens / recomputer> | <what was read, why>
TIMING <minutes for you; per lens>
REVIEW
<the full review in ticket-review's output format, evidence toggle included>
```
