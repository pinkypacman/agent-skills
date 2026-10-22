# Plan pipeline

Ten phases, five owner stops (A–E). The state lives on the **plan page** so that `plan resume` works in a new session: a `Planning checklist (sprint-manager)` toggle at the top of the page, one line per phase, ticked as the phase ends:

```markdown
- [x] 0 catch-up · <date>
- [x] 1 minutes · <date> · A: owner yes <date>
- [ ] 2 grilling · Q<n> asked, waiting
- [ ] 3 carry-over · B
…
- [ ] 9 hand-over
```

A phase that ends at a stop is ticked only after the owner's yes, recorded on its line. Phase 0 runs before the page exists; tick it when phase 1 creates the page.

## Phases

### 0. Catch-up

Read the project's catch-up pages (the project instructions name the query), the previous Sprint row (goal, "goal met when", schedule, retrospective rules, carry-over), its plan page and the Board. *Done when* you can state in three lines: the previous goal, what it delivered, what is unfinished.

### 1. Minutes

Read the newest advisor-meeting minutes in the config's minutes folder (PDF; read every page), the deck shown and any file written for that meeting (config: slides and meeting folders), and the previous meeting's minutes and advisor-prep page. Build:

- **Action items**: every action item of the previous meeting and every new ask of this one, each mapped to **done** (cite the ticket or page), **superseded** (by what, and why), or **open** (becomes a sprint candidate). Drop none silently.
- **Decided vs open**: what the advisor decided (direction, parked topics, venue, deadlines) versus what the owner still has to decide. Each open item becomes a grilling question.
- **Assumptions**: what you assume the advisor already knows, so the owner can correct it.
- **Tensions**: where the minutes contradict a reviewed result or the previous plan (a finding the advisor holds in an older form; a scope the advisor deferred that a candidate ticket would touch); each one is a grilling question or an item for the next meeting.

**Stop A**: show the four lists, and ask what was said in the meeting that the minutes do not record. Every decision that rests only on the owner's account says so. On yes, create the plan page in the working-docs database (Category Plan, Status Draft, Catch-up off, current phase, Created today) with: purpose callout, objective, the checklist, the four lists, an empty grilling log. *Done when* the page re-fetches with all four lists.

### 2. Goal alignment (grilling)

Load the `grilling` skill and question the owner one question at a time: the sprint goal (one sentence), its "goal met when" conditions, then every open item from phase 1. Before each question, explain the mechanism; give your recommendation first.

The **grilling log** on the plan page is plain bullet lines (no tables: they cannot be appended to reliably):

`- **Q<n>** · <question> · <decided <date> / open / rejected> · <decision, with the owner's reason>`

Write each answer into the log **before** asking the next question, and update the checklist line (`Q<n> asked, waiting`). An answer that changes an earlier one rewrites that line and says "amended <date>". *Done when* the goal and its conditions are decided and no phase-1 open item is still open (an item may be decided "deferred to next sprint").

### 3. Carry-over

For every ticket of the previous sprint not Done or Dropped: status at close · state of the work (from its Hand-off, Files, Receipt) · why unfinished · proposed **carry** / **drop** / **supersede by <new item>**. Then the next-sprint candidates: Backlog tickets, the previous plan's candidate list, open action items. **Stop B**: the table. On yes, record it on the plan page. *Done when* every unfinished ticket has an accepted disposition.

### 4. Ticket set

Draft a sketch table: sketch key · `Card` · title · Type · Priority · Size (≤ 2) · `Review (days)` · Blocked by · Owns paths (+ read-only). Each ticket serves the goal through its `Card`. Then check every ticket and print each check as pass or fail:

| Check | Pass when |
|---|---|
| Runs on today's code | open every script, runner and input the ticket names; every argument, setting and path it needs exists now (a run over seeds needs a `--seed` the runner reads, not a hard-coded seed; a grid needs the grid to be a parameter). A gap becomes an enabling change in Do or a blocker ticket |
| Owns disjoint | no two tickets of the set, nor a carried In Progress ticket, write the same path; read-only lists do not overlap another ticket's writes |
| Precedent | every experimental setting cites a precedent or says "no precedent found" |
| Size | ≤ 2 days, or an owner exception recorded in the grilling log |
| Dependencies | Blocked by forms no cycle; a Run ticket is blocked by the code it runs |
| Rules | the project's standing constraints (label use, sealed outputs, forbidden files) appear in Owns and Do where they apply |

**Stop C**: the table and the checks. *Done when* the owner approves the set and every failed check is fixed or waived in the log.

### 5. Create

Create the Sprint row (Status Planning, number, dates, one-sentence goal, Plan page, "goal met when"). Create each ticket with the project's required properties and sections, its Key counted from that sprint's existing tickets, Status Ready when it has no blockers (else Blocked), and its `Review (days)`. Apply the carry-over dispositions accepted at stop B (Sprint relation, Status Dropped, Backlog). Re-fetch every page. *Done when* the Sprint row lists every ticket and each ticket reads back complete.

### 6. Schedule

First ask the owner which days of the sprint are days off (no review or reading; machines keep running). Their answer replaces the sprint's entries in the config's non-workday list; show the new list in the stop D table. Then, from the config calendar and the ticket set:

- critical path to the sprint's deadline (sprint end, or the advisor meeting);
- per ticket `Ready for review` (developer calendar), `Due` and its review days (owner workdays);
- owner days (which review lands on which workday), developer lanes at the WIP limit, GPU toggle (which cards, processes per card, wall time from earlier logs, run now through the GPU rule).

Compare the owner's review load with capacity day by day. Where it exceeds capacity, propose cuts (review after the sprint, move to next sprint) with the effect on slack. **Stop D**: the schedule table, owner days, lanes, GPU toggle and the cuts. On yes, write the three ticket properties and the Sprint row's schedule section (generated from the properties). *Done when* every ticket has a `Due` or an explicit "after the sprint", and no day is over capacity without an accepted reason.

### 7. Close the previous sprint and write the Handoff

Draft the previous sprint's close with [`close.md`](close.md) and the new Handoff (current state, design decisions, open items, next action). Show both with the phase-8 list. **Stop E**: the owner's "go" covers phases 7 and 8. Then write: the previous sprint closed, the new Handoff (Catch-up on), the old Handoff (Catch-up off, Superseded).

### 8. Switch

Point the Board filter at the new sprint plus Backlog; set Sprint Status (old Closed, new Active); plan page Active + Catch-up on, the previous plan Superseded + Catch-up off; Scrum page "Current sprint" text and a line in the sprint archive list. Offer archive moves (completed evidence Closed, obsolete pages Superseded, Catch-up off first) as a separate yes. Re-fetch every page changed. *Done when* every changed page reads back as intended.

### 9. Hand over

Run the status mode once (its log line is the new sprint's first). Print the card and the first `/ticket-loop <KEY>` command. Tick the last checklist line.

## Resume

1. Find the plan page: the Planning Sprint row's Plan page, else the newest Draft plan page in the working-docs database. Read its checklist.
2. Re-read the configs, the Board and the grilling log.
3. Continue at the first unticked line. A stop waiting for a yes: show its table again. Phase 2: ask the next question after the last logged one. Phase 5 half done: compare what exists with the approved set and create only what is missing.
