# Review template

Plain language first: the owner should understand the situation in under a minute without
knowing the review's internals. No internal codes in the visible part (checklist row numbers,
CONFIRMED / PLAUSIBLE, reviewer names). Code locations stay visible: every item names its
`path:line`. Sort by what the owner must do, not by review category. At most 6 numbered fixes.
Write "none" for an empty section so it is visibly checked. The whole review fits on one screen:

- **Nice-to-haves are filtered.** One survives only if ignoring it could break later work or
  mislead a later reader; cosmetics (naming, formatting, receipt pointers) are dropped and only
  counted. Survivors are sorted most to least important (breaks later work or data integrity →
  could mislead a reader or a claim → process and receipts), one line each: plain title — `path:line`.
- **Evidence is on request.** In the conversation, print it only when the owner says "show
  evidence" (or asks to see the dropped points), then in full, never elided. When posting to the
  tracker, always include it, collapsed.

```markdown
### <KEY> — <ticket title, short>

**Bottom line:** <2–3 plain sentences: did the work do what the ticket asked, and what is left>.
**Recommendation: <Approve | Send back for fixes (about <effort>) | in design mode: Ready to build | Revise plan>.**
<If sending back: say which fixes could instead be approved now and tracked as follow-ups.>

**Did it meet the acceptance criteria?** <Yes, all N | N of M>.

| What the ticket asked | Result | Where |
|---|---|---|
| <criterion in plain words> | ✅ met / ⚠️ partly / ❌ not met — <one phrase> | `path:line` or receipt |

(design mode: "Will the plan meet it?" instead of Result)

**Decisions for you (<n>)**
**<Question in plain words>?** <What happened and why it is a choice, 1–2 sentences.>
Where: `path:line`. → I recommend <option>, because <reason>.

**Must fix before approval (<n>)**   (only Blocker items; omit the heading if none)
1. **<Plain title>.** <What is wrong, 1–2 sentences.> *Why it matters:* <one sentence>.
   Where: `path:line`. Fix: <≤ 10 words>.

**Developer should fix (<n>)**   (Fix items; bugs say "Needs a fix and a regression test")
1. **<Plain title>.** <What is wrong.> *Why it matters:* <one sentence>. Where: `path:line`.

**Outside this ticket** — <items a related ticket owns (→ its key, plus any note it needs), and
candidate follow-up tickets with suggested Owns paths; or "none">.

**Earlier findings** (re-review only) — <finding: resolved / not resolved>.

**Nice-to-haves (<n>)** — <k> cosmetic points dropped, ask to see
- <plain title> — `path:line`   (most important first)

<details><summary>Evidence</summary>   (tracker post always; conversation only on "show evidence")

Per item: which reviewers raised it, what the arbiter opened or ran, the output that confirmed it
(CONFIRMED / PLAUSIBLE). The dropped cosmetic points, one line each. Dropped or merged findings
with the reason; severity or AC changes and why; commands run and their results.
</details>
```

Severity behind the headings: **Blocker** = "Must fix before approval" · **Fix** = "Developer
should fix" (waivable by the owner as a follow-up) · **Optional** = "Nice-to-haves". A finding that
needs the owner's judgment goes under "Decisions for you", never in a fix list.
