# Challenge Round

Read for every review unless it is skipped under "When to skip". After the draft
findings pass the finding gate and verification, one independent challenger reviews the
same change by running this same skill as a full review, blind to the draft. It then
tries to disprove the draft's findings. The primary reviewer, which is whichever agent is
running this skill, compares the two reviews, verifies every finding against the code,
and writes one merged report in which each finding appears once.

A second reviewer catches what one context misses. A primary reviewer that has spent an
hour on a diff develops blind spots; a fresh context does not share them. The challenger
supplies evidence, not decisions, so the report keeps one owner and one standard.

## When to skip

- `REVIEW_CHANGES_CHALLENGER=1` is set in your environment. You are the challenger; do
  not start another round.
- The user asked for a quick review, said to skip the challenge, or declined a
  challenger when asked.
- The change has no behavior to challenge, such as a lone version bump or a rename.

State a skip and its reason in one Summary clause.

## Choose the challenger

Ask the user which challenger to use. Ask it in the same message as the step 1
intent-source question so the review interrupts only once. Skip the question when the
user already named a challenger for this review, and reuse their choice for the rest of
the review.

Build the options from what can actually run here:

1. Detect installed CLIs: `command -v codex opencode pi claude`.
2. Remove your own CLI. A Codex primary does not offer Codex; a Claude Code primary
   does not offer `claude`. Launching your own CLI gives the same model as a fresh
   subagent, at higher cost and with a new process to manage. The fresh-subagent
   option covers that case.
3. Add **Fresh subagent** when your runtime can dispatch a clean-context subagent. It
   runs on the same model provider, so no code leaves the current one.

| Option          | Runs as                                  | Read-only by                                                     |
| --------------- | ---------------------------------------- | ---------------------------------------------------------------- |
| Codex           | `codex exec`                             | `-s read-only` sandbox; apps, plugins and MCP servers disabled    |
| OpenCode        | `opencode run --standalone --agent plan` | per-run config denies every tool except read, grep, glob, list    |
| Pi              | `pi -p`                                  | `--tools read,grep,find,ls` plus `--no-mcp --no-extensions`       |
| Claude Code     | `claude -p`                              | `--tools Read,Grep,Glob`, plan mode, `--strict-mcp-config`        |
| Fresh subagent  | this runtime's subagent tool             | brief, and read/search tools only when the runtime allows         |

Read-only includes MCP servers and app connectors. Each CLI otherwise loads the user's
servers (Jira, Notion, GitHub and others), and their tools can post, merge, or deploy
from outside any file sandbox. A fresh subagent that inherits those servers must be
told not to call them; prefer a subagent type without them when the runtime offers one.

In the question, note that an external CLI sends the diff and surrounding code to
whatever model provider it is configured with. Accept an optional model name. Otherwise
keep the model the user already uses with that CLI. For OpenCode the script reads the
model last chosen in its TUI, because `opencode run` would otherwise fall back to a
different default. Do not change any CLI's global configuration.

In a non-interactive review nobody can answer. Use a fresh subagent and disclose that.
If the runtime has none, skip the round and disclose that. Do not choose an external
CLI on your own, because that would send code to a provider the user did not pick.

## Build the packet

Reuse the packet `scripts/collect.sh` wrote in step 2; it is already outside the
reviewed target and holds `diff.patch`, `meta.json`, `manifest.json`, `snapshot/`, and `base-snapshot/`. Point the
challenger's working directory at `snapshot/` unless a fuller checkout of the same
revision is available. Never write the packet inside the repository. Add:
- `draft-findings.md`: each draft finding in the output-contract finding shape, numbered
  `D1`, `D2`, … in report order. Include Questions and design Suggestions. If there are
  none, write `None.`
- `existing-feedback.md`: built from `existing-feedback.json`, one entry per existing PR thread or review comment, with
  author, path:line, resolved/outdated state, its claim in one line, and your status for
  it from the review workflow. Write `None.` when there is none or the target is local.
- `prompt.md`: the template from [challenger brief](../agents/challenger.md) with every
  placeholder filled.
- `skill/`: a copy of this skill's `SKILL.md` and `references/`. The dispatch script
  creates it; for a fresh subagent, copy them yourself.

Point the working directory at the reviewed snapshot: the checkout for a PR or commit,
or an isolated copy when the working tree differs from the target. When no local
checkout exists, say so in the brief. The challenger then reviews from the diff alone,
with less context, and you note that limit in Summary.

## Dispatch

For an external CLI, run the bundled script. It holds the verified read-only flags for
each CLI:

```bash
bash <skill-dir>/scripts/run-challenger.sh <codex|opencode|pi|claude> <workdir> <packet> [model]
```

It writes `<packet>/challenger-<agent>.md` and `.log`. A run usually takes several
minutes. Use your runtime's background execution when available and keep working on the
report in the meantime. macOS has no `timeout` command, so rely on your tool's own time
limit rather than wrapping the call.

For a fresh subagent, copy `SKILL.md` and `references/` into `<packet>/skill/`, then
send the contents of `prompt.md` as its task. Tell it the packet paths, and give it only
read and search tools when the runtime lets you choose.

A full review by the challenger takes longer than a targeted check. Start it as soon as
the draft and packet are ready, keep verifying your own findings while it runs, and
wait for its result before writing the report. If the subagent cannot start (for
example a concurrency limit), retry once after your own other subagents finish. If it
still cannot start, or fails or never returns: in an interactive review, tell the user
and offer the other installed challengers; in a non-interactive review, skip the
round. Either way say so in Summary and Verdict, and do not present the review as
challenged. Run every "Reproduction to
run" the challenger proposes yourself, under [prove it](prove-it.md), before you
accept or reject that finding.

After changing the script, run `bash <skill-dir>/scripts/test-run-challenger.sh`. It
uses stub CLIs, so it makes no provider calls.

If your installed CLI rejects a flag, check its `--help` and adjust that call only. A
prompt that says "read-only" is not a sandbox. If you cannot establish real read-only
execution for the chosen CLI, do not run it. Tell the user and offer the other options.

## Accept the result

A usable report has all three sections from the brief, a verdict for every draft
finding, and a `Matches:` line on every independent finding. Exit code 0 alone does not
make it usable. Some CLIs (OpenCode, Pi) print narration before
`## Independent findings`; ignore it and read from that heading. A report whose
Coverage shows it did not follow the skill, or skipped the design pass, counts as a
partial review: use what it found and name the gap in Summary.
Check the result:

- Empty output, an auth or quota error in the log, or a truncated report: retry once
  only when the log points to a transient cause. Otherwise treat the run as failed.
- After a failure, tell the user what failed and offer the remaining options once. In a
  non-interactive review, fall back to a fresh subagent and disclose it. Do not keep
  cycling through CLIs.
- Confirm that `git status` of the reviewed target did not change during the run. If it
  did, stop and report it. Do not clean up or revert anything yourself.

## Compare and merge

The challenger provides evidence. You decide what the report says. Check every claim
against the code yourself. Do not count votes, and do not defer to a confident tone.

First line up the two reviews. Use the challenger's `Matches:` lines as a starting
point, but decide equivalence yourself by the defect, not the wording or line:

| Found by | What you do |
| -------- | ----------- |
| Both reviews | One finding. Keep the clearest wording and the strongest evidence from either; take the tighter anchor. If the Types differ, re-run the Type decision from the output contract. |
| Only the challenger | Treat it as a missed finding (below). |
| Only the draft | Apply the challenger's verdict on it (below). |
| An existing PR thread | Not a new finding. If the challenger shows the thread's fix is incomplete, put that through the finding gate as a new finding about the gap. |

Then settle each verdict and each challenger-only finding:

| Challenger says | What you do |
| --------------- | ----------- |
| CONFIRMED | Keep the finding. Agreement adds no evidence beyond what you already had. |
| REFUTED | Open the cited code. If the refutation holds, drop the finding. If it does not, keep the finding and sharpen its `Issue:` so the next reader does not make the same mistake. |
| DOWNGRADE / UPGRADE | Re-run the Type decision from the output contract. Change it only when the challenger's evidence changes the impact. |
| UNVERIFIABLE | Keep or drop it based on your own evidence. If neither of you can verify it, it becomes a `Question - Non-blocking` at most. |
| Missed finding | Apply the full finding gate and deduplicate it against existing PR feedback, exactly as for your own findings. Add it only when it passes. Re-anchor it to an exact changed line. |

The result is one merged list: every finding appears once, whichever review found it,
and the design Suggestion cap of three applies to the merged list. A challenger finding
that you add enters the report as a normal finding. Do not tag which agent found it. The
author needs the defect, not its origin.

When you and the challenger still disagree after you have checked the evidence, and the
point is material, keep your position. Record the disagreement in Conflict notes in one
line with both views, so the author can judge.

This is one round. Do not send the merged result back for another pass unless the
user asks. Further rounds cost time and tokens and mostly produce argument, not new
evidence.

## Report it

Inside the six report parts, with no new section:

- **Summary:** one sentence naming the challenger and its model if known, and the
  outcome in counts. For example: "Challenged by Codex (<model>), which ran its own full
  review: 2 findings found by both, 1 draft finding dropped after its refutation held,
  1 challenger finding added, 1 rejected at the finding gate." Say so when the round was
  skipped, failed, or ran as a partial review.
- **Review path:** add `→ Finding:` pointers for findings added in this round, and add a
  stop when a finding sits outside the existing path.
- **Findings:** the merged list only.
- **Conflict notes:** unresolved material disagreements, one line each.
- **Verdict:** if the challenger could not cover part of the target, name that part with
  the other coverage limits.

Keep the packet until the review ends. It is the record of what the challenger saw.
