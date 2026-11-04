# Execution Review

Applies to both protocols and every route — internal, named, parallel and controller.
Simple mode uses the same per-task and final review shape and the same reviewer brief; only
the strict-specific steps below (frozen inputs, approved Minor IDs, re-running the approval
gate) are strict's. A named workflow may supply an equivalent review, but record actual
scope/evidence; a checkbox or worker self-report is not a review. Review implementation
correctness against the approved plan; do not revise inputs.

## Per-task review

After the worker's focused checks and before dependent work or branch integration:

1. The controller reads the actual diff in the recorded workspace, the owned plan task,
   relevant global constraints/interfaces, assigned Minors and real command outputs.
2. With usable authorized delegation, send a fresh reviewer those absolute input paths,
   the task scope and diff/workspace. Reviewer must read code and evidence, not trust the
   implementer's summary. No implementation or shared-ledger writes by the reviewer.
3. Without independent review, perform the same check in the controller and record
   `self-review — independent review unavailable`, with the reason. Do not claim independence.
4. Check requirement behavior, edge/failure paths, unintended scope, interfaces and whether
   focused tests can catch the required failure. Return findings with file/line/evidence and
   `CLEAR` or `BLOCKED`. A correctness, safety or requirement defect blocks progress;
   non-behavioral Minors need an explicit disposition.
5. Fix implementation defects within the approved design, re-run the directly affected
   tests, and have the reviewer recheck the changed task. Material design defects return to
   `plan-and-challenge`. Preserve edits and freeze dependent work while blocked.

Record reviewer identity, role (independent/self), reviewed diff/revision or content digest,
commands, findings, actual fix responses and outcome in the ledger. Do not mark a task
Reviewed/Done, advance dependent tasks or integrate while blocking findings remain.
For parallel independent tasks, review each in its own workspace and integrate one at a time.

## Final review

After all tasks and authorized integration, review the complete resulting change in its final
workspace. Repeat the same independent/self selection. Provide task.md, normative specification,
plan, all Minor dispositions, baseline and final diff, task reports and verification evidence.

Compare every source requirement and approved task with actual code; check cross-task
interfaces and integration effects, preserved user changes, unrequested behavior, unresolved
findings and real verification scope. Run focused tests/lint and project-wide typecheck/build
where available. Do not turn missing or failed checks into CLEAR evidence.

Record implementation review `CLEAR` only when no blocking implementation finding remains.
Record verification status separately:

- A check the project/task does not define is `not applicable`, with the repository evidence
  and reason. Do not invent a build or typecheck pipeline for a fixture that has none. This
  is not a passing check, but it does not itself block completion of applicable verification.
- An existing required check that cannot run because its tool, environment or access is
  missing is `unavailable`; verification remains incomplete and completion is blocked.
- A check that ran and failed is `fail`, with the real output; never relabel it unavailable
  or not applicable to obtain a green result.

A CLEAR code review does not override failed or unavailable required verification.
Do not repeat already successful checks without changed code, new failures or another reason.
In strict mode, re-run the approval gate after the last input/code work as the main skill
requires; simple mode instead confirms the plan's revision and approval are still the ones
the work was built against.

## Reviewer brief

```text
Review the actual implementation in <absolute workspace> against <absolute frozen task,
specification and plan paths>. Scope: <owned task or final complete diff>, starting baseline
<revision/dirty-state evidence>, current diff <revision or paths>. Read repository instructions.
Inspect the code, approved constraints/Minors and actual test/lint/typecheck/build evidence.
Check correctness, requirement coverage, edge/failure paths, interfaces and unintended scope.
Do not edit files, approve a plan, run broad suites, or perform external actions.
Return evidence-backed findings with file/line, severity and smallest correction; identify any
missing verification. End with CLEAR or BLOCKED. State whether this was independent review.
```
