# Pitfalls

Tool traps that have each cost an earlier loop from 20 minutes to an hour. Check the line that matches what you are about to do.

## Notion updates

- `update_content` takes `content_updates: [{old_str, new_str}]`. Each `old_str` must match the page text exactly once.
- Anchor on a short bold marker or heading line (`## Hand-off\n*pending*`). These fail to match:
  - table rows and anything containing `|`;
  - text containing a URL or a mention;
  - image blocks.
- A `|` inside a table cell splits the cell; write "given" or "/" instead.
- To add rows to a table, put a small new table after the toggle's summary text rather than extending the old one.
- A whole-page replace over ~90 KB can be cut off by the output guard, and then nothing applies. Keep pages smaller, or post figures last.
- After every write, re-fetch the page and grep it for each new string and each retired one. Keep the page's TL;DR property in sync with its body.

## Subagents and headless sessions

- Pin the model on every call. Environment defaults (`CLAUDE_CODE_SUBAGENT_MODEL`) are not visible to Bash, so check the model id the first subagent returns.
- A Workflow task's output file is a JSON wrapper `{summary, agentCount, logs, result}`; read `result`.
- Headless `claude -p` needs:
  - `--output-format stream-json --verbose`: plain JSON keeps only the last turn;
  - `< /dev/null`;
  - an absolute prompt path from `readlink -f`: a `cd` before a relative `cat` launches an empty prompt.
- A subagent cannot save a tool result to disk verbatim. Recover it from the subagent's transcript JSONL (the result text is JSON inside JSON).
- Re-query related tickets' statuses right before each review round; facts change under the loop.

## Worktrees

- A worktree holds only tracked files. `worktree.sh` links every ignored path from the main checkout; a run that fails on a missing file in a fresh worktree usually needs a path that was ignored after the worktree was made — rerun the link step for it.
- Code that finds the repo root with `Path(__file__).resolve()` inside a linked folder resolves to the main checkout, and may then import the main checkout's tracked code. Print the resolved module paths in the smoke check.
- Run `git` for the ticket with `git -C <worktree>`; a bare `git` in the main checkout sees master.

## Shell

- `cmd | tee file | head` truncates `file`. Write the file first, then view slices.
- Parallel Bash calls share one cwd: use absolute paths or `( cd … && … )` subshells.
- `rm` inside `bash -c` or with a variable is blocked by the safety check; delete with literal absolute paths.
- Chain dependent long jobs into one background script: one exit notification and one writer per folder.

## Evidence

- Snapshot outputs (copy, or per-table content hashes) **before** any rerun, not after.
- Exclude the log folder from a manifest that is hashed before the log is appended.
- Rerun every step on the final code before hand-off; carried-over tables and figures keep stale provenance.
- Never apply a reviewer's "line is off by one" or direction label without re-grepping yourself.
- Decide a reading rule's direction and the statistical scheme (bootstrap form, horizon) before the real run. A decision that lives only in the orchestrator's head goes into the Hand-off as a "confirm or overrule" item.
- Read every conclusion sentence against its table cell and ask "what is the other reading?"; wording rounds converge slowly.
