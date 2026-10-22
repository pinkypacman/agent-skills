# Status card and replan

## Inputs (read every one, every run)

1. **Sprint row**: the row with Status Active (else Planning; if neither, say "no active sprint: run `plan`" and stop). Its dates, goal, schedule section and `Status log` toggle.
2. **Tickets** in the row's Tickets relation: Key, title, Status, Type, Priority, `Size (days)`, `Review (days)`, `Ready for review`, `Due`, Started, Finished, Blocked by, Developer, Updated.
3. **Loop state** of every In Progress, In Review and Changes Requested ticket: the `Loop state (ticket-loop)` toggle at the end of its Hand-off section, lines `phase`, `jobs`, `stop`. No toggle means the ticket runs without the loop.
4. **Machines**: the config's GPU and load commands, run now. For each `jobs` line: is the process alive, and when did its log last change (`stat`, `tail`). The newest log per ticket in the config's log folders.
5. **Calendar** from the config: non-workdays, review capacity per owner workday, stall threshold. The time now from `date`.

A missing input is a line on the card ("no `Due` on <KEY>"; a ticket the schedule names but the Tickets relation lacks), never a guess.

## Two calendars

- **Calendar days** for developers and machines: every day counts.
- **Owner workdays** for reviews: every day not on the config's non-workday list.
- `cd(a→b)` counts calendar days, `wd(a→b)` counts owner workdays d with a < d ≤ b; both negative when b < a.

## Forecast per ticket

- **Ready (hand-off)**: In Review or later → the actual date (loop `phase: 6 checkpoint-2` line's date, else the dated Hand-off callout). Otherwise **forecast start** = the latest of: its planned start (the Sprint row's lanes table), today if it has not started (else its Started date), its lane predecessor's forecast Ready, each blocker's forecast Done. **Forecast Ready** = forecast start + its planned duration (planned `Ready for review` minus planned start; `Size (days)` when there is no lanes table). Note which constraint set the start: the critical path walks back through it.
- **Done**: the earliest day the review can finish: the ⌈`Review (days)`⌉-th owner workday on or after max(forecast Ready, today). Done tickets use Finished.

## Measures

| Measure | Definition | Reads |
|---|---|---|
| **Ready slip** | `cd(Ready for review → forecast Ready)` | property + forecast |
| **Slack** | `wd(forecast Done → Due)`: ≥ 1 ON TRACK, 0 AT RISK, < 0 LATE | property + forecast |
| **Critical path** | among P0/P1 tickets with a `Due` that nothing else waits on (by Blocked by or lane order), take the one with the smallest slack and walk back through the constraint that set each forecast start | Blocked by, lanes, forecasts |
| **Sprint verdict** | the slack of the critical path's last ticket; an earlier ticket's negative slack that later non-workdays absorb is a flag on that ticket, not the verdict | — |
| **Review load** | per owner workday from today to the sprint end. Taking reviews in order of latest `Ready for review` first, pack each review's r days backward from its `Due` into owner workdays, filling each day only up to capacity and never before its `Ready for review`; what does not fit lands on `Due` as **overload**. A review whose Ready falls after its `Due` lands whole on the first owner workdays from Ready, ignoring capacity, so its overload shows. Do it twice: planned (plan dates) and forecast (forecast Ready in place of planned) | `Review (days)`, `Due`, forecasts |
| **Late start** | not started and today is past its planned start | lanes table, Started |
| **Stalled** | In Progress and either the loop `phase` line is older than the stall threshold with no job alive, or a `jobs` line names a dead process or a log silent past the threshold; without a loop, Updated older than the threshold | loop state, machines |

Slack and review load answer different questions on purpose: slack uses the earliest day a review *could* finish (how much delay a ticket can absorb), review load uses the latest placement within capacity (whether the owner's days are full). A ticket can be ON TRACK and still sit on an overloaded day; the card shows both.

## Next action (the first that applies)

1. A dead job or a stalled ticket: name it and the log to read.
2. A ticket waiting for the owner's launch go (loop `phase: 4 checkpoint-1`, or its newest log line or ticket callout says it waits): the ticket, what passed, where.
3. A review due today or overdue: the ticket and its `Due`.
4. A free lane and a Ready ticket: the Ready ticket on the critical path with the earliest planned start, then the rest by planned start and Priority. For a GPU ticket, only if the GPU rule finds free cards now. Print `/ticket-loop <KEY>`.
5. A Blocked ticket whose blockers are all Done: propose Blocked → Ready (owner yes).

## Card (print it; then write the log line)

```markdown
### <Sprint name> — <date time> · <ON TRACK / AT RISK / LATE> (slack <n> wd on <last critical ticket>)
**Next:** <one action; the exact command when it is a launch>
**Then:** <up to two more>

| Ticket | Status · loop phase | Ready planned → forecast (slip cd) | Due → forecast (slack wd) | Flag |
|---|---|---|---|---|

**Critical path:** <KEY → KEY → KEY>, slack <n> wd.
**Owner review load:** <day: planned / forecast vs capacity, for each owner workday left; overloads in bold>.
**Machines:** GPUs <free cards>; load <1-min> on <cores>; jobs <KEY: alive/dead, log age>.
**Stalled:** <KEY: why>, or none.
**Needs your yes:** <Blocked → Ready proposals; "run replan" when the verdict is AT RISK or LATE or a day is overloaded>.
```

Sort the table by Due. Mark critical-path tickets in bold.

**Log line** (the only write): append one bullet inside the Sprint row's `Status log` toggle; create the toggle at the end of the row body on first use. Plain text, no `|`, no links:

`- <YYYY-MM-DD HH:MM> · <verdict> · slack <n> wd (<KEY>) · review load today <x>/<capacity> · stalled: <keys or none> · next: <action>`

*Done when* the card is printed and the re-fetched row shows the new line.

## Replan

Run when the owner asks, typically after a card says AT RISK, LATE or overloaded. Compute everything above, then propose the smallest change that brings the critical path to slack ≥ 1 and every day within capacity, trying in this order:

1. use buffer days already in the plan;
2. move review slots within the owner's capacity (changes `Due` only);
3. move `Ready for review` / `Due` dates;
4. **cut**: move the lowest-priority tickets (Stretch, then P2) out of the sprint to the next-sprint candidates;
5. split a ticket (a new ticket is scope: name both halves).

Show one table: ticket · field · old → new · why · new slack. Below it, the card as it would read after the change. Cuts and splits are scope and say so. On the owner's yes: write the properties; update the Sprint row's schedule section (the due-date and owner-days tables regenerated from the properties; the lanes table, which the forecast reads, rewritten with each moved ticket's new start and order, never dropped); add a log line `replan applied: <summary>`, re-fetch. On a partial yes, apply only the rows named.
