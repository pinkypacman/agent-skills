---
name: ticket-loop
description: Run one Scrum ticket from Ready to In Review as an orchestrator of subagents, with two owner checkpoints (before launch, at hand-off). Usage `/ticket-loop <KEY>` or `/ticket-loop <KEY> resume`.
disable-model-invocation: true
---

# Ticket loop

You are the **orchestrator**. Subagents do every piece of work: design review, preparation, implementation, review, recomputation and fixes. You claim the ticket, route work, launch long jobs, keep the ticket's **loop state**, apply the stop rules and talk to the owner. The owner steps in exactly twice: **Checkpoint 1** before anything is launched and **Checkpoint 2** at hand-off. Every owner question the loop raises waits for one of the two.

## Config

The project instructions (`CLAUDE.md` / `AGENTS.md`) name a **loop config**. It points to the `ticket-review` config for the tracker, repo, interpreter and checklist, and it holds the loop's own keys: models and effort per role, round cap, isolation (`worktree` or `shared`), GPU and host rules, claim fields, WIP limit, workdir, hand-off marker, notify channel, data-access ledger, the recommendation table and the project's developer rules. Read both files first. If no loop config is named, stop and ask for one. Paths in a config are relative to its folder.

Every subagent call pins its model and effort from the config (Agent `model` / `effort`; Workflow `agent()` takes the full model id). Every subagent returns its model id on its first line. Compare it with the config's full id; if it differs, stop and tell the owner.

You are the **only tracker writer**. Developers write repo files inside the ticket's Owns paths and, under `worktree` isolation, only in the ticket's worktree, committing each step on the ticket branch (local, never pushed, never on the base branch). Every output and log path a ticket writes contains its key. Reviewers and recomputers write nothing outside their round's folder. Loop artefacts go to the config's workdir for this ticket, outside the repo:
- `dev/` holds the sketch, launch plan and hand-off draft;
- `r<n>/` holds round n's packet, returns and snapshots;
- the workdir root holds your logs.

Tell each subagent which folders it may open: its own, plus the files you name.

## Arguments

- `<KEY>` starts at phase 1. If the ticket already has a loop state toggle, stop and say "already started: use `resume`".
- `<KEY> resume` reads the loop state ([`state.md`](state.md)) and continues from the recorded phase.

## Phases

After every phase, rewrite the loop state on the ticket ([`state.md`](state.md)) before starting the next.

### 1. Pre-checks and claim

Fetch the ticket, its blockers and every In Progress ticket. Run all checks, print each one as pass or fail, then stop if any failed:

| Check | Pass when |
|---|---|
| Status | Ready |
| Blockers | every `Blocked by` ticket is Done with a merge commit recorded |
| Owns | Owns paths filled |
| Conflicts | against every In Progress and In Review ticket: no shared write path (else stop). Each of these is a Checkpoint 1 decision: this ticket writes a file the other imports or runs, or the other writes a file this one imports; this ticket writes a path the other lists as read-only or verifies in its AC |
| AC | acceptance criteria present, so they can be numbered AC1…ACn |
| WIP | In Progress tickets actively written by a session, counted before this claim, < the config's limit (launched machine-only jobs do not count; list them when unsure) |
| GPU | for a ticket that runs GPU jobs (config rule): enough free cards under the config's GPU rule, after removing cards another In Progress ticket reserves. Host CPU and RAM headroom per the config is a warning for Checkpoint 1 |
| Type | the recommendation table has a row for it (owner-action types stop here) |

Claim the ticket with the config's claim fields. Under `worktree` isolation, create the ticket's branch and worktree from the base branch with [`worktree.sh`](worktree.sh): it links every git-ignored path of the main checkout into the worktree, so data, outputs, logs and untracked code stay shared. Then fill the ticket's branch and worktree fields. *Done when* the claim fields read back from the tracker and `git -C <worktree> status` is clean.

### 2. Design review (round 0)

Run review round 0 in **design mode** (see Review rounds). Post its review as a toggle at the end of Do, with the verdict as its first line; never write the tracker's verdict field. Give every design finding a `D0.<n>` line in the state and sort it:

- **wording** (clarifies the text without changing what is built, measured or claimed): apply it to the ticket yourself;
- **plan gap** inside the ticket's scope, Blocker or Fix: pass it to the developer in phase 3, whose plan must answer it;
- **owner question** (scope, a setting, what an AC measures, Owns paths): goes to the Checkpoint 1 card as a decision with a recommended answer. The developer prepares on the ticket as written and notes what each answer would change;
- **optional**: pass it to the developer as optional.

There is no second design round. The verdict "Revise plan" means the plan gaps go to phase 3, and hand-off round 1 receives the D0 Blockers and Fixes as prior findings, so it checks they were built. *Done when* every D0 line is sorted.

### 3. Prepare

Spawn a developer subagent with [`developer.md`](developer.md) in **prepare** mode. It writes the sketch, makes any small enabling change and runs a smoke check. A ticket that launches jobs gets a launch plan: exact commands, run list, resources (including the cards it proposes), outputs, expected time, and the code the run imports, split into tracked (isolated by the branch) and untracked or linked (shared). Re-run the Conflicts check with that import list; new conflicts become Checkpoint 1 decisions. A smoke check that would write outside the current Owns waits for `go` and becomes the first step after it. A pure-code ticket stops after the sketch, before its first edit. Post the sketch in the ticket's Do section. *Done when* every plan gap has an answer in the sketch, and every launch-plan field is filled (or the ticket is pure code and the sketch is posted).

### 4. Checkpoint 1

Pick the recommendation row and post the launch plan plus the card from [`checkpoint.md`](checkpoint.md): the open owner questions and pre-check warnings go under "Decisions for you". Then print the card, notify the owner, and **wait**. Parse the reply with the grammar in `checkpoint.md` and record the choice and the answers beside the recommendation. Any other reply is conversation: answer it, revise and re-present the card. *Done when* the owner has replied with a `go` form and the choice is recorded.

### 5. Loop

Repeat until a stop rule fires:

1. **Implement / run.**
   - A developer subagent (implement mode) writes the code and runs the short checks. A Run ticket without code skips this.
   - Before the launch, run the **launch gate**. The GPUs must still be free (card ids may change to other free cards with the same process count). The shared imported code (untracked or linked files, and under `shared` isolation all of it) must hash the same as at `go`; record HEAD and those hashes. A changed file fires S4.
   - Launch the long jobs yourself as **one background chain** (`run_in_background`, plus `Monitor` with an until-condition for failure lines), with the plan's post-run checks as the chain's tail. You are woken when the chain exits, so never poll.
   - Record job ids and log paths in the state.
   - When the jobs finish, a developer subagent collects the outputs into the hand-off draft. Post it as the Hand-off body, replacing any earlier version, and fill the file and receipt fields.
2. **Review.** Run hand-off round r (see Review rounds). Record every finding in the state, matched against earlier ones.
3. **Stop check** (Stop rules). If none fires:
4. **Fix.** A *new* developer subagent in fix mode gets the ticket, this round's open findings and the repo, and commits its fixes on the ticket branch. Rerun every check and analysis step the outputs depend on, on the fixed code. Rerun jobs only when the fix changed what they compute; otherwise re-verify their receipts. Then go back to 2.

### 6. Checkpoint 2

Confirm that the last review round saw the final state: the current hashes must equal that round's snapshot. If a stop fired mid-phase, say what the last round did not see. Then:
- fill the Hand-off: marker callout first, then the 5-line summary from `checkpoint.md`, then the developer's top-down body, receipts collapsed last;
- fill the file and receipt fields from the branch diff against the base (`git diff --name-status <base>...<branch>`, or `git status` of the Owns paths under `shared` isolation), plus a file listing or manifest for git-ignored outputs;
- check that the branch still merges cleanly into the current base (`git merge-tree`), and put the merge block from `checkpoint.md` in the Hand-off;
- add every data access the subagents reported to the config's ledger rows in the Hand-off;
- set Status In Review and leave the verdict field empty;
- notify the owner.

Never set Done, never fill the verdict or merge fields, never commit on the base branch, never merge, never push.

## Review rounds

Round 0 is the design round. Rounds 1, 2, … are hand-off rounds, and the round cap counts hand-off rounds only. Each round is run by one **fresh arbiter subagent** with [`reviewer.md`](reviewer.md), given exactly the inputs that brief lists, and none of your own context or opinion. Facts about the environment that a stranger cannot discover go in as labelled facts with evidence, never as opinions: which command writes into the repo, a known test artefact, that the outputs are git-ignored. Hand-off rounds run in hand-off mode even though Status is still In Progress. Under `worktree` isolation the diff under review is `<base>...<branch>` in the worktree.

- **Before:**
  - re-query the related tickets' statuses;
  - hash every file under the Owns paths (in the worktree) and outputs into `r<n>/snapshot.sha256`, and record the branch HEAD;
  - save `git status --porcelain` beside it (per-table hashes may replace full-file hashes for large databases).
- **After:** once the arbiter's task has finished, including its lenses, check the hashes and compare `git status`. A change outside the ticket's Owns is another session's: name it and check its time and owner. A change inside the Owns stops the loop (S5).
- If the arbiter reports it cannot spawn subagents, spawn the lenses yourself with `ticket-review`'s briefs, then give their returns to a second fresh subagent to arbitrate.
- **Ultracode only** (the owner said `go ultracode`): run each round, and any parallel builders, as a Workflow (load `workflow-authoring`); the lenses, recomputer and arbiter are `agent()` calls.

## Stop rules

Check them in this order after every round. Stop at the first that fires and name it in the state and at Checkpoint 2:

| Rule | Fires when |
|---|---|
| **S1 clean** | no Blocker or Fix finding is open (Optional items do not count) |
| **S2 cap** | the hand-off round number has reached the round cap |
| **S3 stuck** | a finding with the same file/line and claim is still open after two fixes |
| **S4 plan change** | a fix needs different commands, data inputs or Owns paths than approved; a developer returns `CANNOT-FIX-IN-PLAN` or `NEEDS-OWNS`; or the launch gate finds the plan's inputs changed under it. Stop *before* acting |
| **S5 broken** | a launched job failed twice; a tool the loop needs is unavailable; or a round's snapshot shows a write inside the Owns that no developer made |

A finding that is still open but has had fewer than two fixes goes to another fix round. S4 and S5 also fire mid-phase: stop at once, record the state, go to Checkpoint 2 and say what changed or broke.

[`pitfalls.md`](pitfalls.md) lists the tool traps that have cost earlier loops time. Read it before phase 1, and give its path to every developer.
