# Close a sprint

Used by `close` and by plan phase 7. Draft everything in the conversation first; write only after the owner's yes (in plan, stop E).

## Read

The Sprint row (goal, "goal met when" verbatim, schedule, rules in force, `Status log`), every ticket in its relation (Status, Finished, Merge commit, Review verdict, Receipt, Hand-off TL;DR), the plan page, and the Result pages the tickets link.

## Draft, in this order on the Sprint row body

1. **Outcome callout** at the top: goal met / partly met / not met, n of m Done, one line on what is missing; **Your move:** the owner's next decision.
2. **Goal-met scorecard**: one row per planning condition, verbatim · result with evidence (ticket, commit, page). A departure from the condition is named as one.
3. **What shipped** (per ticket, with commit or page) and **what it taught**, each finding labelled the way the project's rules require (oracle / label-scored results, AI-reviewed with verdict empty, provisional).
4. **What slipped.**
5. **Carry-over table**: ticket · status at close · state of the work · why unfinished · proposed disposition (carry / drop / supersede by …). Dispositions are proposals until the owner accepts them.
6. **Root causes** of the slips, numbered; then what worked.
7. **Retrospective**: numbered process changes for the next sprint. Use the `Status log` for facts: how many days the verdict was AT RISK or LATE, which reviews overflowed capacity, which tickets stalled.
8. **Archived tickets**: a linked Tickets view filtered to this Sprint row, at the bottom.

Properties: `Review` (a paragraph: goal met?, n/m Done, shipped, learned, slipped) and `Retrospective` (the numbered changes in one paragraph).

## Handoff

A new working-docs page, Category Handoff, Status Active, Catch-up on, with: purpose and next action callout; where the project stands (table); what the sprint established (labelled as above); decisions taken; open items as checkboxes; links in a collapsed toggle. On write, the previous Handoff of the same track gets Catch-up off and Status Superseded, so exactly one Catch-up Handoff remains per track.

## Write (after the yes)

Write the row body and properties, create the linked view, set Status Closed, create the Handoff, update the old one, apply the accepted carry-over dispositions (Sprint relation, Status), add the sprint's line to the Scrum page's archive list. Re-fetch every page and check it. *Done when* every carry-over ticket shows its accepted disposition and the Scrum page lists the closed sprint.
