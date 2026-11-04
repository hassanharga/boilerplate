---
name: implement-plan
description: Use when executing or resuming a written implementation plan approved by plan-and-challenge or saved under docs/agent-plans/ - including "implement the plan", "start on the plan", "carry on where the last session stopped" - when delegating a plan's tasks to implementers, or when checking whether a plan is approved before writing code. Use it whenever the work to do is already written down in a plan file. Use plan-and-challenge for planning or replanning.
---

# Implement Plan

Check the approved handoff, implement its tasks, and keep progress visible and
resumable. User and repository instructions take precedence. Approval to implement
does not authorize commits, publication, destructive actions or shared-system writes.

Strict approval requires `python3`. Artifact setup uses Python when available and
otherwise the manual equivalent below; Git is needed to verify repository exclusions.

## Choose the protocol

Use the approved plan's recorded protocol; do not choose a default or ask the user
to choose it again during execution. If neither a workflow label nor the strict
evidence below establishes the protocol, return to `plan-and-challenge` to obtain
an explicit choice and the corresponding approval. Resolve conflicting records there.

Read the supplied plan and its approval record before editing. An execution-gate
stamp, fingerprint approval or `plan-approval-v2` record requires **strict** mode:
read [strict-workflow.md](references/strict-workflow.md) and follow its gate and
workflow instead of the simple steps below. A simple label cannot override strict
evidence. Never downgrade a failed strict gate to bypass it.

For **simple**, require `Workflow: simple`, `Status: Approved`, and the latest Review
entry for the current plan revision with an actual independent `CLEAR` report or
explicit user approval after recorded self-review. Read task.md and any specification
too. Missing approval, unresolved material findings or conflicting mode, revision
or requirements return to `plan-and-challenge`; a plan's existence is not approval. Simple mode does not run
the fingerprint gate or use strict templates. Old unmarked handoffs need planning
to establish their protocol and approval before execution.

## 1. Reconcile and show the tasks

Read applicable project instructions and inspect the branch, worktree and existing
staged, unstaged and untracked changes. Protect the user's and other agents' work.
Read `implementation.md` beside the plan, if present. Confirm recorded completed
work in its actual workspace and integration state before deciding what remains;
an absent change in a different checkout is not evidence that work must be redone.
Reuse verification when its code, dependencies, configuration and environment match.

Before creating execution artifacts, run this skill's helper:

```bash
python3 <skill-dir>/scripts/artifacts.py <absolute-task-folder>
```

Keep the task-folder `.gitignore` containing `*`; never change the repository-root
ignore file or Git's `info/exclude` for this workflow. Resolve helper failures;
never force-add or untrack artifacts to bypass them.

If `python3` is unavailable, use this manual artifact-hygiene equivalent only:
resolve the intended folder and Git root first; reject the repository root and folders
containing tracked/staged files (`git ls-files -- <relative-folder>`). Reject a symlink
`.gitignore`; preserve its existing bytes and append `*` as the last rule, adding a
newline first if needed. Confirm exclusion of `.gitignore`, `task.md`, `plan.md`,
`review.md` and `implementation.md` with `git check-ignore -q -- <relative-path>`
from the repository root. Do not overwrite existing rules. Outside Git, create only
the folder; exclusion is not applicable. If Git status or locality cannot be established,
stop and report the blocker. Record the fallback and checks. This does not bypass the
strict fingerprint gate, which still requires Python and has no manual equivalent.

One controller owns the execution record; use
[simple-ledger-template.md](assets/simple-ledger-template.md) for its layout. Record
controller/session, plan revision,
workspace/baseline, tasks and next action. Before taking over from another controller,
obtain its release or verify its session ended and reconcile outstanding workers;
a stale timestamp alone is insufficient. Workers report back without editing this file.

Show all approved task IDs/names with reconciled states, current work and blockers.
Use the native visible task list when available, otherwise a Markdown checklist.
The execution record is the persistent source of truth; an old UI state is not.

## 2. Execute and review

Follow the plan's required route. Otherwise use one implementer at a time when
usable and authorized, or execute sequentially in the controller. A separate
agent/session can implement an owned task with the same brief. If delegation fails,
reconcile its partial work and liveness before takeover; never create two writers.
A required route that is unavailable without an allowed fallback returns to planning.

For each task, give the implementer the absolute plan/task/specification paths,
exact task ID/name, owned files, dependent interfaces, workspace, existing work to
preserve, project constraints and focused checks. It must return changed files,
actual check results, decisions and blockers. Workers do not revise approved inputs,
change the design, edit the shared execution record or perform unauthorized writes.
Use a concise self-contained brief; strict mode's fingerprint brief is not required.

Parallel implementation is allowed for independent tasks with separate workspaces,
non-overlapping ownership and a clear integration owner. Never run several writers
in one working tree. Obtain any missing authorization for the specific integration
method, worker commits or shared-branch mutations before using them. Integrate and
verify one result at a time; keep workspaces until cleanup is authorized. Coordinate
expensive verification serially unless concurrent runs were explicitly agreed.

Implement the smallest approved change. Add a focused regression test for changed
behavior when practical. Run applicable typecheck, lint, build and directly affected
tests using project commands and resource limits; no package installation or automatic
full-suite fallback. Preserve failures and distinguish missing checks from passes.

Before dependent work or integration, review the actual task diff and evidence
against the plan. Use an independent reviewer when useful and available; otherwise
the controller reviews and labels that fact. Fix implementation defects within the
approved design. The controller makes the final assessment, not the worker's summary.
At the end, review the combined change and cross-task interactions as well. The reviewer
brief and the pass/fail/unavailable/not-applicable distinctions in
[execution-review.md](references/execution-review.md) apply here too — read it when
dispatching a reviewer or deciding what a missing check means.

Update `implementation.md` and the visible checklist on state changes: Not started,
In progress, Implemented, Reviewed, Integrated (when needed), Done, or Blocked.
Check a task off only after its implementation, review, applicable verification and
required integration are complete. In chat, use compact changed-task rows between
full starting and final lists. Do not update the frozen plan to track progress.

## 3. Replan only for material changes

A requirement, design, interface or task-scope defect returns to `plan-and-challenge`.
Stop affected/dependent work, preserve edits, and record the task, evidence, workspace,
verification and next action. Send the absolute execution-record path to planning.
An independent isolated task may continue, but do not integrate while reapproval is
pending. Resume only after the revised plan is approved and preserved work is
reconciled with it. Routine local choices that preserve behavior need only a note.

## 4. Finish or hand off

Compare the result with task.md, the approved plan and accepted review items. Reuse
valid check evidence; run remaining applicable checks and the final change review.
Report PASS, FAIL, BLOCKED, NOT RUN or NOT APPLICABLE with reasons and scope. Do not
mark Done with a confirmed blocker or missing required verification.

Show final task states, blockers and the execution-record link. Check the final diff
and repository status, preserve unrelated changes and keep agent artifacts unstaged.
On interruption, leave current states, workspace and next action for the next agent.
Stop at external-action boundaries unless the user already authorized the exact action.

## Skill maintenance

Simple mode uses `assets/simple-ledger-template.md` and the review guidance in
`references/execution-review.md`. The implementer brief and `assets/ledger-template.md`
belong to strict mode; the simple execution record needs only the fields above, not that
template's approval schema. Keep shared scripts and `tests/test_contract.py` identical in
both skills. After changes, run each skill's focused `test_contract.py` tests serially.
