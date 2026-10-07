---
name: spec
description: Turn a goal into a spec that an agent can implement and the owner can review quickly — aim, acceptance checks, file map, and a planned Input → Process → Output figure. Use when the user wants to plan an implementation, hand coding work to an agent, or write requirements before coding; also used by the bulk-review refactor branch.
---

# Spec

The owner cannot read every line an agent writes. A spec turns review into a comparison. Before
coding, the owner approves the **aim, the acceptance checks and a planned figure**. After coding,
the agent shows the **actual figure** (structure skill), the **bulk report** (bulk-review), and
the **check results**. The owner reads code only where these disagree.

## Steps

1. **Read the existing code** the work touches (`structure.py scan`, any `STRUCTURE.md`). Never
   write a spec blind.
2. **Clarify** with the `grilling` skill, one question at a time, recommended answer first,
   until these are settled:
   - aim;
   - in and out of scope;
   - inputs and outputs;
   - constraints;
   - acceptance checks;
   - where new code goes.

   Small, unambiguous work may need only one or two questions.
3. **Write the spec** using the template below.
4. **Place it**, following the project's own rules first:
   - **existing ticket or issue** covering this work → put the spec in it (e.g. its Do and
     Acceptance sections);
   - **new ticket**, only when the project requires one and none exists;
   - **no tracker, or a small change** → the conversation, summarised in the commit message.
5. **Get approval.** The spec is ready when *Open questions* is empty. The owner approves it
   before implementation starts.
6. **After implementation**, hand back three things:
   - the actual `STRUCTURE.md` figure next to the planned one, with every difference explained;
   - `bulk-review/measure.py --since <base>` output;
   - the result of each acceptance check.

7. **Clean up** once the owner accepts the work:
   - a spec kept in a ticket stays there as the record, with the hand-off results added;
   - a spec written as a file (e.g. `SPEC.md` in the code tree) is deleted, or moved to the
     project's archive if the project keeps one. Its content is preserved in the ticket or the
     commit message;
   - a spec in the conversation needs nothing, beyond its one-line summary in the commit message.

   No spec file stays in the code tree after the work is accepted.

**Done when** the spec has no open questions, every box in the planned figure appears in the file
map, and every acceptance item can be checked by running something. After acceptance, step 7 has
removed any spec file.

## Template

```markdown
## Aim
One sentence: what is true when this is done.

## Scope
In: … · Out: …

## Behaviour
Inputs → outputs. Constraints (e.g. frozen paths, memory or latency budget).

## Planned structure
Mermaid Input → Process → Output figure in the structure skill's conventions; boxes may name
files that do not exist yet.

## File map
| File | New / changed | Aim (one line) |

## Acceptance
- [ ] command or test → expected result
- [ ] `measure.py --since <base>` passes (or each exception justified)
- [ ] `structure.py check <folder>/STRUCTURE.md` passes after implementation

## Open questions
(must be empty before hand-off)
```

## Notes

- The planned figure follows the structure skill's conventions, so the finished `STRUCTURE.md`
  is the planned figure made true. Run `check` only after implementation: planned files fail it
  until they exist.
- Keep a spec to about one screen. If it needs more, split the work into several specs.
