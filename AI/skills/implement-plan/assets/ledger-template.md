# Implementation Ledger — <plan title>

<!-- implementation.md beside the approved plan/review. Controller-owned. Maintain current
state while appending event/evidence history; never erase earlier runs or command failures.
Frozen inputs and saved verdicts are not edited during execution. -->

## Controller and handoff
- Current controller: <agent/session identity>
- Next action: <actor and pending step>
- Last update: <timestamp; not proof that another controller is inactive>
- Handoff/takeover evidence: <prior controller release or confirmed ended session, reconciled workers/writes, or new ledger>

Only the recorded controller writes this ledger. Before takeover, establish that the previous
controller has released ownership or its session has ended, and outstanding workers/writes
are reconciled; unresolved
liveness blocks takeover. Append transfers to event history. Planning reads this ledger and
preserved workspace evidence before revising, and checks for material changes before approval.

## Gate
- Task snapshot: <absolute task.md>
- Plan: <absolute path>
- Normative specification: <absolute path or none>
- Review: <absolute path>
- Qualifying verdict evidence: <absolute path>
- Approval schema and run: <plan-approval-v2, run ID>
- Gate command: <python3 ABSOLUTE-SKILL-DIR/scripts/fingerprint.py --verify ABSOLUTE-REVIEW --plan ABSOLUTE-PLAN>
- Gate result and time: <actual exit/output and timestamp>
- Approved open Minors: <each ID, assigned task or leave with reason>

## Baseline and current workspace
- Repository identity/root: <path and remote identity when available, or non-Git>
- Starting revision: <SHA or unavailable>
- Starting branch/worktree: <name and absolute path>
- Existing staged changes: <paths/ownership or none>
- Existing unstaged changes: <paths/ownership or none>
- Existing untracked changes: <paths/ownership or none>
- Current workspace matched to ledger: <evidence or unresolved mismatch>
- Execution route: <approved rule, selected route and fallback basis>
- Delegation: <usable/authorized or actual failure/restriction>
- Agent artifacts: <task-folder .gitignore with *, Git verification result, or not applicable>

## Authorization
- Action/method: <patch | worker commit plus merge/cherry-pick | other exact action | none>
- Source: <actual user message/reference and time>
- Targets and scope: <branches/worktrees/destination/files covered>
- Constraints/expiry: <actual limits or none stated>
- Still applicable on resume: <evidence; reuse valid authorization, ask only if scope changed>

## Tasks

| # | Exact plan task | Owner and absolute workspace | State | Evidence and integration |
|---|---|---|---|---|
| 1 | <task> | <agent or self; path> | Not started / In progress / Implemented / Reviewed / Integrated / Done / Blocked | <diff/revision, report, tests and integration status> |

Verify work in each recorded workspace before reconciling. A branch not yet integrated is
not missing implementation. Unavailable workspaces and unknown ownership remain unresolved;
do not redo or overwrite their work based only on a different current checkout.

## Event and decision history

- <time, actor, event, repository evidence, design-preserving decision, affected task>

## Commands

| Exact command and scope | Actual result | Evidence / failure resolution |
|---|---|---|
| <command, cwd, affected paths> | pass / fail / unavailable / not applicable | <output and any later resolution> |

## Task and final reviews

| Scope | Reviewer and independence | Reviewed diff/revision | Findings and actual responses | Verdict |
|---|---|---|---|---|
| <task N or final> | <identity; independent or self with reason> | <evidence> | <IDs, corrections, Minor dispositions, verification limits> | CLEAR / BLOCKED / verification incomplete |

## Blockers and preserved partial work

- <task, exact plan text, contradictory evidence, changed files/workspace, dependency impact,
  pending owner/action, returned to plan-and-challenge and new run when applicable>

## Completion

- [ ] Focused tests — <exact command and real result>
- [ ] Changed-file lint — <exact paths/command and real result>
- [ ] Project-wide typecheck — <command and real result or unavailable/not applicable>
- [ ] Project-wide build — <command and real result or unavailable/not applicable>
- [ ] Task and final review outcomes recorded; blocking findings resolved
- [ ] Result compared with task, specification, plan and all assigned Minors
- [ ] Authorized integration performed sequentially and verified, or not applicable
- [ ] Gate passed after final changes using the absolute skill-owned script
- [ ] Git status checked; no agent artifacts staged; baseline user changes preserved
- [ ] Any external action covered by recorded applicable authorization
