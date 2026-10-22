# Checkpoints

## Checkpoint 1: launch card

Pick the recommendation row from the loop config's table. Rows are checked from the most demanding up; the first match wins. Post the card at the end of the ticket's Do section (as a toggle `Checkpoint 1 (date)`) and print it in the conversation:

```markdown
### <KEY> — ready to launch (Checkpoint 1)

**Design review:** <verdict> · <n> wording fixes applied · <n> plan gaps answered in the sketch.

**Decisions for you** (<n>; "none" if empty) — owner questions from the design round, conflicts with other tickets and pre-check warnings, each with what it changes:
1. <question in plain words>? <why it is a choice>. → I recommend <answer>, because <reason>. <"**Needs your answer**" when it changes Owns paths or scope>

**Launch plan** (pure-code ticket: "sketch only, no launch" + file map)
- Commands: <exact, copy-pasteable, one per line>
- Run list: <arms × cohorts × seeds, count>
- Resources: <GPU cards and why they are free now and unreserved, processes per card, RAM, threads, host headroom>
- Branch: `<branch>` in `<worktree>` from `<base>` at <sha> (or "shared checkout")
- Imported code: tracked <paths, isolated by the branch> · shared <untracked or linked paths, hashed at `go`; a change stops the launch>
- Outputs: <paths that will exist>
- Expected time: <wall-clock, from the smoke check's rate>
- Smoke check: <command> → <result, log path>
- Enabling change: <files touched, or "none">

**Recommendation** (row <Rk>: <why it matched — type, size, GPU, stat claims>)
| Role | Recommended | Why |
|---|---|---|
| Orchestrator `/model` · `/effort` | … | … |
| Developer | model · effort | … |
| Reviewers (lenses + arbiter) | model · effort | … |
| Recomputer | model · effort, or "none" | … |
| Ultracode | on / off | … |
| Round cap | N | … |

**Reply:** `go` · `go ultracode` · `go cap=N` · `go effort=X` (may be combined: `go ultracode cap=4`). Answer a decision with its number (`go 1=keep`); a bare `go` accepts the recommended answers, except decisions marked **Needs your answer**.
Switch `/model` and `/effort` first if you take the orchestrator advice.
```

### Reply grammar

| Token | Meaning |
|---|---|
| `go` | launch with the recommendation as shown |
| `ultracode` | review rounds and parallel builders run as a Workflow |
| `cap=N` | round cap N instead of the row's |
| `effort=X` | every subagent role runs at effort X (`/effort` sets only the orchestrator's) |
| `<n>=<answer>` | the answer to decision n; unanswered decisions take the recommended answer, except an Owns or scope decision: then reply "decision n needs your answer" and launch nothing |

Record the choice in the loop state: the row, the reply verbatim, each decision's answer, the date, and the orchestrator model you are running at the time of `go`. Any reply without `go` is conversation, so nothing is launched.

## Checkpoint 2: hand-off

Top of the ticket's Hand-off section, in this order:

1. A callout with the config's hand-off marker, the stop rule that fired, and the date.
2. A 5-line summary:

```markdown
1. **Outcome:** AC met <n>/<m>; stopped by <S1–S5 name> after round <r>/<cap>.
2. **Findings (hand-off rounds):** <raised> raised, <resolved> resolved, <open> open, <outside> moved to other tickets; design round: <n> D0 items, <k> confirmed built.
3. **Open:** <≤ 3 items, plain title — `path:line`; or "none">.
4. **Receipts:** <run receipt / test log / page URL>.
5. **Your move:** <the one decision or check the owner should make first>.
```

3. A merge block (worktree isolation):

```markdown
**Merge** — branch `<branch>` (<n> commits) merges cleanly into `<base>` at <sha>: <yes / no, conflicting files>.
Review: `git -C <main> diff <base>...<branch>`
Merge: `git -C <main> merge --squash <branch> && git -C <main> commit -m "<KEY>: <title>"`, then push; afterwards `git -C <main> worktree remove <worktree> && git -C <main> branch -D <branch>`.
```

4. The developer's top-down Hand-off body, with receipts collapsed last.
5. The last round's full review text in a collapsed toggle `AI review — round <r> (date)`.

Then notify the owner with lines 1 and 5 and the ticket link.
