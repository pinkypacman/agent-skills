---
name: bulk-review
description: Review Python code for files or functions that have grown too long or tangled for a human to review, and offer a guided refactor. Use after writing or changing code, when reviewing a change, when the user asks whether code is too long, bulky or messy, or when the bulk hook reports code over its limits.
---

# Bulk review

Keep each file and function small enough that a human can review it in one sitting.
`measure.py` (next to this file, standard library) finds the candidates; the review explains why
each one is hard to follow. A refactor never starts here: real problems are offered to the
**refactor branch** (`REFACTOR.md`), which asks the owner before anything changes.

```bash
M=~/.claude/skills/bulk-review/measure.py
python3 $M --changed --since HEAD .   # what this change made worse (the usual review)
python3 $M path/ file.py              # full audit of files or folders
python3 $M --all file.py              # every function's numbers
```

The after-edit hook (`hook.py`) runs the `--since HEAD` form on every edited file automatically.

## Limits

| Measure | Limit | Source |
|---|---|---|
| code lines per file | 400 | stricter than pylint `max-module-lines` (1000) |
| statements per function | 50 | pylint `max-statements` |
| arguments per function | 5 | pylint `max-args` |
| branches per function | 12 | pylint `max-branches` |
| nesting depth | 5 | pylint `max-nested-blocks` |
| cyclomatic complexity | 10 | McCabe's usual limit (ruff `C901`) |
| cognitive complexity | 15 | SonarSource rule S3776; adds a penalty for each level of nesting |
| function docstring | required | project rule (put it in `CLAUDE.md` / `AGENTS.md`); test functions exempt |
| loop comment | required | same rule; loops with a one-statement body exempt |

New code may be held to stricter limits (e.g. `--max-cognitive 10`); state the reason. Use `--no-docs` to
skip the two documentation checks when auditing old code.

## Steps

1. **Measure.** For a change, use `--since HEAD`: old problems the change didn't touch stay
   quiet, as in CodeScene's "code health decline" gate. Use a full run for an audit.
2. **Read every flagged item** in the code; a number is only a pointer. Name the smell:
   - **Brain method:** one function holds most of the behaviour (long, branchy, deeply nested).
   - **Bumpy road:** one function holds several separate chunks of logic, each its own little task.
   - **Mixed triggers:** setup, per-item work and periodic work in one unit (compare the blocks of
     the folder's `STRUCTURE.md`).
   - **Long argument list:** several arguments that always travel together.

   Or call it **harmless:** a flat table of constants, one linear validation list, a CLI argument list.
3. **Report**, per item: the verdict, the smell in one sentence, and the likely fix from the
   catalogue below. List harmless items with a one-line reason.
4. **Offer the refactor branch** if any item is real: *"N items are worth refactoring. Plan the
   refactor together?"* On yes, follow [`REFACTOR.md`](REFACTOR.md). On no, stop. Never refactor
   from this step.

**Done when** every flagged item has a verdict, and the refactor branch was offered for the real ones.

## Fix catalogue

| Smell | Usual fix |
|---|---|
| deep nesting | guard clauses / early returns |
| bumpy road | extract each chunk into a named function |
| mixed triggers | one function or file per trigger, matching the `STRUCTURE.md` blocks |
| long `if`/`elif` chain on a value | lookup table or dict dispatch |
| long argument list | a small dataclass for the values that travel together |
| file over the limit | split by job; each new file gets a one-line docstring |

## Frozen code

Sealed, vendored or upstream code (anything the project marks frozen, e.g. hashed by a registered
protocol) is **report-only**: list its bulk as known debt and do not offer the refactor branch.
When porting such code into a new package, the limits apply to the new copy.
