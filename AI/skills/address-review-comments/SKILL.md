---
name: address-review-comments
description: >-
  Use when the user asks to address, apply, fix, or resolve code-review
  feedback from a GitHub pull request, pasted comments, or another agent's
  review, including replying to each PR thread with a summary of what was
  done and the fix commit. Do not use to produce a code review.
---

# Address Review Comments

Resolve review feedback against the current code, not the reviewer's authority.
Every comment must end with an evidence-backed disposition, and every code
change must be traceable to an actionable comment.

## Operating Contract

- Read the repository's instructions, acceptance criteria, and test conventions
  before deciding or editing. Repository and user instructions take precedence.
- Preserve unrelated working-tree changes. Make the smallest change that
  resolves the verified issue; do not include adjacent cleanup.
- Read-only discovery does not authorize GitHub replies, thread resolution,
  review submission, commits, or pushes. Get explicit approval immediately
  before each outward-facing or shared-state-changing action.
- If ambiguity, conflicting feedback, or a design choice could affect another
  comment or public behavior, stop before editing and ask one focused question.

## Workflow

### 1. Resolve the feedback scope and code revision

Identify:

- where the comments came from: GitHub, pasted text, or another agent;
- which repository, pull request, branch, base, and current head are in scope;
- whether the user requested every actionable comment or only selected items;
- whether local staged or unstaged changes are part of the reviewed code.

If any of these would change what gets edited, clarify before continuing.

### 2. Inventory all feedback before editing

Normalize the feedback into numbered items and read all of it before acting.
Cluster duplicates, dependencies, and contradictions by behavior rather than
blindly following comment order.

For GitHub reviews, retrieve current PR metadata, diff, reviews, inline threads,
and top-level discussion. Thread-aware data must include, where available:

- thread and comment identifiers;
- path and current/original line anchors;
- comment commit and current PR head;
- resolved and outdated state;
- replies that may supersede the original comment.

A flat review-comments list is not complete thread state. Use a connector that
exposes threads or a thread-aware GitHub API/GraphQL read. Refresh the head and
thread state immediately before triage when the PR may have changed.

Treat "address all comments" as all unresolved, current, actionable feedback;
exclude approvals, informational notes, resolved threads, outdated findings
that no longer apply, and duplicates. If the user did not define the scope,
present the actionable list and ask which items to address.

### 3. Triage every item against current code

For each item, inspect its target plus the relevant callers, contracts, tests,
types, and repository rules. Assign exactly one disposition:

| Disposition           | Meaning                                                   |
| --------------------- | --------------------------------------------------------- |
| `valid`               | The issue exists and is in the approved scope.            |
| `invalid`             | Current code or a governing contract disproves the claim. |
| `already-handled`     | Current code or tests already resolve it.                 |
| `out-of-scope`        | Real, but not part of the requested change.               |
| `needs-clarification` | More information or a user decision is required.          |

Resolved threads, outdated findings, and duplicates were already filtered out in
step 2, so they never reach this table. List them in the report as excluded, with
the reason, rather than assigning them a disposition — an item cannot be both out
of scope and dispositioned within it.

Reasons for non-`valid` dispositions must cite checkable evidence: a current
line, test, contract, thread state, or changed behavior. Never dismiss a comment
from its wording alone.

Before editing, surface any material conflict, ambiguity, scope expansion, or
behavioral tradeoff. Do not implement the clear-looking subset when an unresolved
item could change its correct design.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final report, and every external write
stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means triaging independent comments in parallel — each one's code inspection
stands alone. Clustering duplicates, resolving contradictions between comments, and
assigning the final disposition stay with the main agent, because those depend on seeing
every item at once.

### 4. Implement each selected valid item

Work in dependency order: security and correctness blockers first, then simple
independent fixes, then larger dependent changes. For each item:

1. Define the observable behavior that proves the issue and its resolution.
2. If the change is behaviorally unit-testable and the repository has suitable
   unit-test infrastructure, add a focused regression test and run it before the
   production edit. Confirm it fails for the expected reason.
3. Make the smallest production change that resolves the verified issue.
4. Run the focused test again and confirm it passes.
5. Record the code and test evidence for the final report.

If the pre-fix test passes, errors for an unrelated reason, or cannot detect the
reported bug, correct the test or reassess the comment before changing production
code. A test written only after the fix does not prove it catches the regression.

### 5. Verify

Follow the repository's own coverage and verification policy; do not invent a
threshold where none exists. Where the change is not meaningfully unit-testable or
the repository has no suitable test infrastructure, use the project's applicable
verification and disclose the limitation rather than adding a hollow assertion.

Before completion, run the project-defined typecheck, lint, build, and affected-test
checks. Report every command and its actual result, including baseline failures that
were already there.

## Report

Account for every normalized item. Dispositions are for your reasoning; write the
report as a teammate explaining decisions, not as an audit log. Translate them into
plain phrases — "fixed", "already handled", "no change needed" — and include the code
itself only when the user wants an audit trail. Avoid canned acknowledgements and
defensiveness, and do not repeat the reviewer's comment unless a short quote
disambiguates it.

Prefer a short paragraph or a few bullets. For a larger review set, a compact table
may help:

| #   | Comment                | Disposition | Evidence or resolution      | Test/verification      |
| --- | ---------------------- | ----------- | --------------------------- | ---------------------- |
| 1   | Null dereference       | `valid`     | Guard added at `user.ts:42` | Regression test passed |
| 2   | Extract one-use helper | `invalid`   | One caller; no duplication  | Not applicable         |

Finish with:

- fixed items and files changed;
- items not changed, each with its concrete reason;
- items excluded during inventory as resolved, outdated, or duplicate;
- tests, coverage requirement/result, typecheck, lint, and build outcomes;
- remaining decisions or limitations;
- verdict: all requested feedback resolved, or exactly what remains.

## Reply to Each Addressed Comment

When the feedback came from a GitHub PR, finish by replying to every comment you
dispositioned, so the reviewer can see what happened without diffing the branch.
Offer this step after the report even if the user did not ask for it; post only
after approval. Skip excluded items (resolved, outdated, duplicate) — they get no
reply. Pasted or agent-produced feedback has no thread to reply to; skip this step.

### Link the fix commit

A reply to a fixed comment should open with a link to the commit that fixed it,
because that is the first thing a reviewer clicks. The commit must already be on
the remote, otherwise the link 404s for them. So:

1. If the fix is uncommitted or unpushed, ask whether to commit and push first.
   Committing and pushing need their own approval; replying does not imply it.
   If the user declines, draft the reply without a link and say "Fixed locally,
   not yet pushed" rather than inventing a SHA.
2. Map each fixed comment to the commit(s) that contain its change. If one commit
   fixes several comments, every one of those replies links the same commit.
3. Confirm the remote has the commit before posting:
   `gh api repos/{owner}/{repo}/commits/{sha} --jq .sha`.
4. Link format: `[<first 8 chars of sha>](https://github.com/{owner}/{repo}/commit/{full sha})`.

### Write the reply

One short paragraph, two to five sentences, in this order:

1. **Decision and link** — "Fixed in [c4462d33](…)." For no-change outcomes, lead
   with the decision instead: "No change here — …", "Already handled by …".
2. **What changed, as behavior** — describe what the system now does differently,
   not which lines moved. The reviewer cares that "types the verifier can't sample
   now recover without a restart", not that a condition was added to a function.
3. **Edges and limits** — any related case you deliberately kept, narrowed, or
   left alone, so the reviewer doesn't have to ask.
4. **Proof** — which test now covers it, by name or suite, if one was added or
   already exercises it.

Example (a real reply this format is modeled on):

> Fixed in [c4462d33](https://github.com/YAtechnologies/mob-redis-replication-service/commit/c4462d33ccd4f57066183bf9a89f45ac3e3d4c7b).
> After a signature change, a completed full repair with no payload rejections for
> a type now clears its incompatible latch, so types the verifier can't sample
> recover without a restart. Types missing from a fully observed repair are
> retired. Same-generation recovery still goes through the verifier. The guards
> integration tests cover both.

Tone: plain and specific, as a teammate would write it. No disposition codes,
checklist labels, or placeholders. No stock openers ("Addressed", "Good catch!",
"Reviewed against the current code"). If the reviewer was right, the fix speaks for
itself; if no change is needed, cite the evidence calmly without sounding
defensive. Never say a concern is resolved before verification supports it.

### Approve, post, and verify

Show all drafted replies together, each labeled with its comment link, and ask
once. One approval covers the whole set — replies are low-stakes messages inside
existing threads, so do not ask per reply.

Post inline review comments as replies inside their existing thread, addressed to
the thread's **root** comment id (GitHub does not allow replying to a reply):

```bash
gh api -X POST repos/{owner}/{repo}/pulls/{pr}/comments/{root_comment_id}/replies \
  -f body="$REPLY"
```

Top-level PR conversation comments have no thread; post a PR comment that links
the original comment (`gh pr comment {pr} --body ...`) instead.

After posting, read each thread back and confirm the reply exists. If a post
times out or errors ambiguously, check the thread before retrying so the
reviewer doesn't get the same reply twice. Report which replies were posted and
any that failed.

### Thread resolution

Resolving a thread is different from replying. It changes state a reviewer relies
on, so it needs its own explicit approval even when posting the replies was
already approved. Many teams prefer the reviewer to resolve their own threads;
do not offer to resolve unless the user brings it up or the repo's conventions
say authors resolve.
