---
name: address-review-comments
description: >-
  Work through a set of code-review comments and actually resolve them — verify
  each comment against the real code, implement fixes for the valid ones, add
  tests covering 100% of the lines each fix touches, and for every comment left
  unaddressed give a concrete technical reason. The comments can come from a
  GitHub PR (fetched with gh), a list pasted into the chat, or feedback another
  agent left on the current local/working-tree changes. Use whenever the user
  says "address these PR comments", "apply the review feedback", "fix the review
  comments", "handle the reviewer's notes", "got review comments", "the reviewer flagged X, Y, Z — sort
  them out", "go through this PR feedback and fix what's real", or hands you
  review output and asks you to act on it. This is the CONSUME side of review.
  DO NOT USE to PRODUCE a review of a diff (use code-review), for a single
  verbal instruction that isn't review feedback, for pure git workflow, or for
  conceptual questions — answer those directly.
---

# Address Review Comments

You have been handed a review — a list of comments about code — and your job is
to close the loop on it: work out which comments are real, fix those, prove the
fixes with tests, and explain the ones you don't touch. This is the opposite of
writing a review. A reviewer's job is to raise concerns; yours here is to
**resolve** them honestly.

The failure mode to avoid is performative compliance — implementing every comment
because a reviewer said so, without checking whether it's correct for _this_
codebase. A reviewer can be wrong, lack context, or ask for something the code
already does. Equally bad is the reverse: hand-waving a real bug away as "won't
fix" to save effort. Both erode trust. Verify against the actual code, then act
on what you find, and make your reasoning legible.

## The core loop

For **each** comment, run the same five moves. Never batch-implement before you've
verified — a wrong fix applied confidently is worse than no fix.

1. **Understand** — restate the comment in your own words. If you genuinely can't
   tell what it's asking, mark it `needs clarification` and move on; don't guess.
2. **Verify against the code** — open the file and lines the comment points at.
   Does the problem actually exist? Is the reviewer working from stale or partial
   context? Does an existing test, type, or invariant already prevent it? Read
   enough surrounding code (callers, siblings, the contract it depends on) to be
   sure — don't judge from the comment text alone.
3. **Decide** — land on one verdict: `valid` (real, fix it), `invalid` (reviewer
   is wrong or it's a non-issue — say precisely why), `already-handled` (code or
   a test already covers it), `out-of-scope` (real but belongs in separate work),
   or `needs clarification`.
4. **Act** — for `valid`, make the smallest change that resolves the comment. Fix
   one comment at a time; don't let an unrelated cleanup ride along. If two
   comments touch the same code, resolve them together and note it.
5. **Prove it** — add or extend tests so that **100% of the lines your fix
   touches** are exercised (see [Testing rules](#testing-rules)). Run the tests
   for the changed files and confirm they pass before calling the comment done.

Work valid comments in a sensible order: blocking/correctness/security first, then
trivial fixes (typos, imports), then larger refactors. Test each before the next.

## Discovering the comments and the code

First figure out which of the three shapes you're in — the source of the comments
and the source of the code under review can differ.

**Where the comments come from:**

| Situation                                              | How to get them                                                                                                                                                                                    |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub PR (number or URL given, or the branch has one) | `gh pr view <n> --json title,body,reviews` and `gh api repos/{owner}/{repo}/pulls/{n}/comments` for inline threads. Note each comment's `id`, `path`, and `line` so you can reply in-thread later. |
| Pasted into the chat                                   | Parse the message into discrete comments. Number them yourself if the user didn't.                                                                                                                 |
| Another agent reviewed local changes                   | The review is already in the conversation (e.g. code-review output). Treat each finding as a comment.                                                                                              |

**Where the code under review lives** — establish this before verifying, because
"the actual code" means different things:

| Situation                  | Command                                                                                         |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| GitHub PR                  | `gh pr diff <n>` for the changes; check out or read files on the PR branch.                     |
| Local working-tree changes | `git diff` / `git diff --staged` / `git status --short` — the review is about uncommitted work. |
| A branch vs base           | `git diff <base>...HEAD`.                                                                       |

If the source is ambiguous, ask one short question rather than assume — verifying
against the wrong tree wastes the whole pass.

## Testing rules

Tests are how you _prove_ a fix is real rather than asserting it. The target is
**100% coverage of the lines your fix added or changed** — patch coverage, not the
whole file and not the whole project. You are not on the hook for pre-existing
untested code near your fix; you are on the hook for every line you write.

- **Write the failing test first when you can.** For a bug fix, a test that
  reproduces the bug (red) then passes after the fix (green) is the strongest
  proof the comment was real and is now resolved. For a behavior change, assert
  the new behavior directly — not that a mock was called.
- **Match the project's test conventions.** Find a neighboring test file, use the
  same runner, structure, and naming. Don't introduce a new framework.
- **Run only the affected tests**, not the whole suite (a full run can exhaust
  memory when several agents run at once). Report the command and the pass/fail
  result honestly — never claim green you didn't see.
- **If the repository has no tests at all** — no test files, no test runner in the
  manifest, no test script — **do not bootstrap a test framework**. Writing tests
  that resolve the fix but skip verification is a bigger change than the user
  asked for. Make the fix, then flag in the report: "no test infrastructure in
  this repo — fix applied without an automated test; suggest adding tests."
- If a fix is genuinely untestable (config value, generated file, pure rename with
  compiler coverage), say so explicitly rather than writing a hollow test that
  asserts nothing.

## Reporting

Always produce a **per-comment triage table** so the user can see at a glance what
happened to every comment — nothing silently dropped.

```
| # | Comment (short) | Verdict | Resolution | Test |
| - | --------------- | ------- | ---------- | ---- |
| 1 | Null deref in parseUser | valid | Added guard at user.ts:42 | user.test.ts +1 case ✅ |
| 2 | Extract helper for DRY | invalid | Only used once; extracting adds indirection (YAGNI) | — |
| 3 | Missing await on save() | valid | Awaited at repo.ts:88 | repo.test.ts covers reject path ✅ |
| 4 | Rename to camelCase | already-handled | Lint autofix already enforces this | — |
| 5 | Rework caching layer | out-of-scope | Real, but unrelated to this PR; suggest separate ticket | — |
```

Then a short summary:

- **Fixed:** `<n>` comments, `<n>` tests added/extended, all passing (`<command>`).
- **Not fixed:** list each with its one-line reason (invalid / already-handled /
  out-of-scope / needs clarification).
- **Verdict:** `All comments resolved` | `Resolved except <n> needing your input`.

For every `invalid` / `out-of-scope` verdict, the reason must be **concrete and
checkable** — cite the line, the existing test, or the contract that makes it a
non-issue. "Looks fine to me" is not a reason. This is the part the user most needs
to trust, so make the reasoning legible enough that they could disagree with a
specific claim.

## Posting back to GitHub (offer, don't assume)

When the comments came from a GitHub PR, **offer** to post the resolutions back —
don't do it unprompted, since it's outward-facing and visible to the team. Ask
something like: "Want me to reply in each PR thread with the resolution (and the
reason for the ones I didn't change)?"

If they say yes, reply **in the comment thread**, not as a top-level PR comment:

```
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies \
  -f body="<resolution or reason>"
```

Keep each reply short and factual — what changed and where, or the specific reason
it wasn't changed. No performative thanks; the resolution speaks for itself. Get
the user's explicit OK before posting, per the rule on outward-facing actions.

## Calibration

- **Skepticism cuts both ways.** Don't rubber-stamp comments (implement blindly)
  and don't rubber-stamp the code (dismiss real bugs). Each verdict is earned by
  reading the code.
- **Smallest change that resolves the comment.** Don't gold-plate a fix or refactor
  adjacent code the comment didn't mention.
- **Surface disagreement plainly.** If you think a comment is wrong, say so with
  reasoning — that's more useful to the user than silent compliance or silent
  omission.
- **Match the change's weight.** A batch of typo comments gets terse handling; a
  comment about a concurrency bug gets a real reproduction test.
