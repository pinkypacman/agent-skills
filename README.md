# skills

Agent skills (Claude Code and Codex) maintained by hand, versioned here.

Each folder is one skill (`<name>/SKILL.md` plus any scripts). Claude Code reads user skills from
`~/.claude/skills/` and Codex from `~/.codex/skills/`, so each skill is linked into both:

```bash
cd /path/to/this/repo
ln -s "$PWD/<name>" ~/.claude/skills/<name>
ln -s "$PWD/<name>" ~/.codex/skills/<name>
```

Edit the files here; both tools see the change through the links. Relink only when a skill is
added, renamed or moved. The after-edit bulk hook (`bulk-review/hook.py`) is Claude-only: register
it as a `PostToolUse` hook on `Edit|Write|MultiEdit` in a Claude Code settings file.

| Skill | What it does |
|---|---|
| `structure` | draws a code folder as an Input → Process → Output figure in its `STRUCTURE.md` |
| `bulk-review` | flags code too long or tangled to review; `REFACTOR.md` branch plans a refactor with the owner |
| `spec` | turns a goal into a reviewable spec: aim, acceptance checks, file map, planned IPO figure |
| `ticket-review` | reviews a Scrum ticket (plan or hand-off) with independent reviewer subagents and a verifying arbiter; project specifics come from a private review config named in the project's `CLAUDE.md` / `AGENTS.md` |
