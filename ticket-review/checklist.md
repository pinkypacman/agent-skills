# Arbiter checklist

Yes/no checks the arbiter runs itself, by reading and grepping, never by a reviewer's opinion. Run
these generic rows, then every row in the project's review config. A failed check becomes a
finding in "Required but not listed", at the severity its row names (Blocker when none is named).
In design mode, check the plan in Do instead of the diff. `bulk-review/` and `structure/` are the
sibling skill folders next to this skill's folder.

| # | Check | How | Severity |
|---|---|---|---|
| G1 | The ticket's Files created / modified all lie inside its Owns paths; none in READ-ONLY / FORBIDDEN. Other tickets' uncommitted files are expected and ignored | compare the two properties; `git status --short -- <read-only paths>` | Blocker |
| G2 | Every file the ticket lists appears in `git status`; files under its Owns paths in `git status` but not listed | `git status --short -- <owns paths>` | Fix |
| G3 | Existing sealed or read-only results unchanged | mtimes; `sha256sum` vs the recorded hashes | Blocker |
| G4 | The ticket's tests pass | run them with the config's interpreter | Blocker |
| G5 | Size, complexity, docstring and loop-comment limits hold for new or edited code (sealed code: report only) | `bulk-review/measure.py --changed --since HEAD` | Fix |
| G6 | Each touched folder's `STRUCTURE.md` still matches | `structure/structure.py check <folder>/STRUCTURE.md` | Fix |
| G7 | No secret (token, password, credentialed URL) echoed in the hand-off, code or logs | grep for token prefixes and `https://*@` | Blocker |
