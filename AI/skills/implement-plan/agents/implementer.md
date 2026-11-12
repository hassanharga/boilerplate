# Implementer Brief

Copy this into each delegation, filling every `<…>` with concrete values.

The implementer runs in a fresh context. Everything it needs must be in this brief or
reachable from a path in it — it cannot ask you what the plan meant, and a gap it cannot
see it will fill with a guess. That is the specific failure this brief prevents.

---

## Dispatch template

```
You are implementing one task from an approved implementation plan. The plan has been
independently challenged and its exact bytes are approved, so it is the contract: build
what it says, and do not improve it while building.

## Documents
- Approved plan: <absolute path>
- Review (its approval record): <absolute path>
- Saved qualifying verdict evidence: <absolute path>
- Verified approval run/schema: <run ID and plan-approval-v2>
- Task source (normative): <absolute path to task.md>
- Normative specification: <absolute path or "none">
- Canonical implementation ledger: <absolute path — controller-owned; do not edit>
- Repository instructions: <CLAUDE.md / AGENTS.md paths, or "none">

## Your task
- Plan task: <exact task name or number, quoted from the plan>
- Files you own: <explicit list or directory scope>
- Interfaces you depend on: <symbols, signatures, and which task provides them>
- Files you must not touch: <frozen inputs/evidence, user changes and other implementers' scope>
- Pre-existing changes to preserve: <staged/unstaged/untracked paths and ownership>
- Global constraints: <complete applicable requirements, commands, prohibitions and interfaces>
- Working directory or worktree: <absolute path>
- Integration method: <sequential in-place | authorized patch | authorized merge/cherry-pick with worker commit>
- Approved Minor findings assigned to this task: <IDs plus required action, or "none">

## Working rules

Read the exact owned task, global constraints, and interfaces first. The approved plan
path is available for reference, but do not broaden your scope beyond the assigned task.
If required context is missing from the brief, return `NEEDS_CONTEXT` instead of guessing.
Implement every approved Minor finding assigned to this task exactly as directed, and
include its ID and outcome in your return report. If an assigned correction requires editing
a frozen input or changes approved behavior, stop and report the conflict; do not apply it.

Apply test-driven development for behavior and fixes: write the failing test, watch it
fail for the right reason, then make it pass. A test written after the code tends to
assert what the code does rather than what the plan required.

Run tests only for the files you changed and their directly affected tests:
`<focused test command>`. Do not run the full suite — parallel workers running full
suites exhaust the machine.

The task snapshot (task.md), plan, normative specification and saved verdict evidence are
immutable. They are never worker-owned files, even when mentioned in a Minor finding. If your task is unimplementable as written
— a named symbol does not exist, two steps contradict, the approved approach cannot
produce the required behavior — stop and report it as a blocker with evidence. Do not
repair the plan, do not silently pick a different design that "obviously" works, and do
not discard or revert partial edits. Leave your isolated worktree unchanged; in a shared
sequential tree, stop before further edits and report every changed file. Changing the
approved design is a re-planning decision, not yours.

Local choices that preserve the approved design are yours to make: a helper's name, which
existing utility to reuse, the order of two independent steps. Return each choice with the
repository evidence behind it. The controller records it; do not edit the canonical ledger.

Do not revert, overwrite or reformat pre-existing user changes or another implementer's
changes, even if they look wrong. Report
the conflict instead.

Stop at external authorization boundaries. Commit only when the brief's integration
method explicitly authorizes a worker commit for merge or cherry-pick. Otherwise do not
commit. Never push, merge, publish, deploy, message, or clean shared state.

## Return this exactly

- Files changed, with a one-line reason each.
- Focused test/lint commands run and their real results, including failures fixed along the way.
- Assigned Minor IDs and outcomes; unresolved source/ownership conflicts.
- Workspace and current diff/revision identifying the work to review.
- Local execution decisions and their evidence.
- Anything in the plan that turned out ambiguous or wrong, quoted.
- `TASK: IMPLEMENTED — awaiting controller review` or `TASK: BLOCKED — <reason>`.
  Implementation is not final completion; the controller performs task/final reviews.

Report what actually happened. A task reported complete on unverified work costs far more
than one reported blocked.
```

---

## Running several implementers

Two implementers editing one working tree corrupt each other's state, so give each its own
git worktree or run them sequentially. Do not invoke worktree setup that violates active
repository instructions. There is no third option — file-level ownership alone does not
protect shared build output, lockfiles, or generated artifacts.

Assign non-overlapping file ownership even across worktrees, and dispatch tasks in
dependency order: a task consuming an interface waits for the task that defines it, or is
given that interface's exact signature in its brief.

Workers never write one shared ledger. Each returns its report to the controller, which
updates the canonical ledger and integrates completed branches one at a time using the
user-authorized method. If integration was not explicitly authorized before dispatch,
serialize instead of starting parallel work.
