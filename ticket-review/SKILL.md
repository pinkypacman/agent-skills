---
name: ticket-review
description: Review a Scrum ticket against its acceptance criteria with independent reviewer subagents and an arbiter that verifies every finding — a design review of the plan before coding, or a hand-off review of the delivered work. Use when the user asks to review a ticket, a hand-off or a ticket's plan, or gives a ticket key to review.
---

# Ticket review

The owner approves tickets; this skill prepares the review so the owner can decide in a minute.
Reviewers are **independent subagents**, one per lens, that see only their brief and the review
packet. You are the **arbiter**: you run the checklist, verify every finding against the code or
data, apply the verdict rule and write one brief review. Nothing leaves the conversation until the
owner says **"post it"**.

## Project config

Everything project-specific lives outside this skill, in the **review config** that the project
instructions (`CLAUDE.md` / `AGENTS.md`) point to: where tickets live, the repo root, how to run
Python, what each reviewer reads, and the project's checklist rows. Paths in the config are
relative to the config file's folder. Read it first; if the project names none, stop and ask for it.

## Mode and roster

Input: a ticket key. Fetch the ticket from the tracker named in the config. Its Status picks the mode:

| Status | Mode | Question |
|---|---|---|
| Backlog / Ready / In Progress, Do + AC filled | design | will the plan in Do meet every AC, and is the plan valid? |
| In Review | hand-off | did the delivered work meet every AC without breaking a standing rule? |
| Done / Dropped, or AC empty | stop | say why in one line ("write the spec first" when the AC are empty) |

Its Type picks the reviewers (briefs in `reviewers/` next to this file):

| Type | Reviewers |
|---|---|
| Implementation | methodology, evidence, engineering |
| Analysis | methodology, evidence (+ engineering if it ships analysis code) |
| Run | methodology, evidence |
| Design | methodology, engineering |
| any other type | stop: "nothing to verify against" |

## Steps

1. **Fetch.** Ticket properties (Type, Status, Owns paths with any READ-ONLY / FORBIDDEN lists,
   Card or parent plan, Files created, Files modified, Receipt) and body (Why, Do, AC, Hand-off,
   Review). Read the plan decisions the ticket cites (Card and body), not the whole plan.
   *Done when* the AC are numbered AC1…ACn.
2. **Build the review packet** in a temporary directory outside the repo: ticket text, numbered
   AC, cited decisions, mode, and in hand-off mode the file list and `git diff -- <owns paths>`
   plus every new file. Add the **related tickets** (the ones this ticket blocks or is blocked by):
   key, title, Status, Owns paths and AC of each. If the Review section holds an earlier review,
   add its findings as **prior findings**.
3. **Spawn the roster** in parallel: one independent subagent per reviewer, told to read
   `reviewers/shared.md` and its role file (absolute paths of this skill's folder), the review
   config, and the packet. Pass no opinion of your own.
4. **Run `checklist.md` yourself** while they work: its generic rows, then the config's rows.
5. **Verify.** Merge and de-duplicate the findings; open every evidence pointer and tag it
   **CONFIRMED** or **PLAUSIBLE**, or drop it. A disagreement the evidence cannot settle becomes a
   **[Your call]** finding (`A: … / B: … → recommend …`). Prior findings get Resolved / Not resolved.
   Before keeping a finding, check the related tickets: if one owns it (its Owns paths, Do or AC
   cover it), move it to "Outside this ticket → <that key>" with any note that ticket needs, and do
   not count it against this one. You set the final severity and AC verdict; when reviewers differ, the AC's own wording decides,
   and the evidence toggle notes the change.
   *Done when* every returned finding is tagged or dropped.
6. **Verdict** (a recommendation; never write the tracker's verdict field):
   - any Blocker, Fix, Not met or Partial → **Changes requested**; name the items that could be
     waived to approve instead;
   - otherwise **Approved** (Optional items do not count). Never recommend "Not needed".
   - Design mode says **Ready to build** / **Revise plan** instead.
7. **Write the review** in the conversation using `output.md`: filter and sort the nice-to-haves,
   and hold the evidence back until the owner asks for it.
8. **Post it** only when the owner says so: hand-off → append to the ticket's Review section under
   `Draft — AI peer review (date)`; design → a toggle `Design review (date)` at the end of Do.
   Never change the verdict field, Status, Reviewer or Merge commit. Re-fetch the page to verify.

**Done when** every AC has a scorecard row, every checklist row was run, every finding is
CONFIRMED / PLAUSIBLE / dropped, and the verdict follows the rule.

## What you and the reviewers may run

Allowed (read-only, CPU): reading files, receipts and tracker pages; `git status/diff/log`; the
ticket's tests; `bulk-review/measure.py --changed --since HEAD` and `structure/structure.py check
<folder>/STRUCTURE.md` (sibling skill folders next to this one); read-only queries on result databases to recompute a reported
number; `sha256sum` of sealed files.

Forbidden: editing or creating files in the repo, commits, GPU jobs, re-running experiments,
tracker writes before "post it". A GPU reproduction is a `[Your call]` finding, not an action.
