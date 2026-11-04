# Implementation Ledger — <plan title>

<!-- implementation.md, saved beside plan.md. Controller-owned: workers report to you, they
do not write this file. Strict mode uses ledger-template.md instead, which adds the gate and
approval-schema fields this one deliberately leaves out. -->

Keep current state at the top and append history below it. The value of this file is that a
different agent — or you, after a compaction — can resume without re-deriving what happened,
so record what was actually run and actually found, including the failures.

## Controller and handoff

- Current controller: <agent/session identity>
- Plan and revision: <absolute plan.md path, and the revision this work implements>
- Next action: <actor and pending step>
- Last update: <timestamp; not proof that another controller is inactive>
- Takeover evidence: <prior controller's release, or confirmation its session ended and its
  outstanding workers were reconciled; leave blank for a new ledger>

Before taking over from another controller, establish that it released ownership or its
session ended, and that no worker is still writing. A stale timestamp is not that evidence.

## Approval checked

- Workflow: simple
- Status read from the plan: <Approved, and the revision it covers>
- Review entry relied on: <reviewer identity, date, verdict, or the user's approval message>
- Accepted non-blocking items: <what was left open at approval, and who owns each>

If the plan's revision moved past the reviewed one, stop: that is a new candidate and it
returns to `plan-and-challenge` rather than being implemented on the old approval.

## Baseline and workspace

- Repository root and branch: <path and branch, or non-Git>
- Starting revision: <SHA or unavailable>
- Existing staged / unstaged / untracked changes: <paths and whose they are, or none>
- Execution route: <sequential delegation | controller-executed | parallel isolated, with
  the authorization covering integration when parallel>
- Agent artifacts: <task-folder .gitignore with *, how exclusion was verified, or not applicable>

Record pre-existing changes before editing anything. Work you did not make and cannot
attribute is work you must not revert, reformat or stage.

## Tasks

| # | Exact plan task | Owner and workspace | State | Evidence |
|---|---|---|---|---|
| T1 | <task name from the plan> | <agent or self; path> | Not started / In progress / Implemented / Reviewed / Integrated / Done / Blocked | <changed files, commands run and real results, review outcome> |

States are distinct on purpose: Implemented means the code exists, Reviewed means someone
checked it against the plan, Done means its verification and any required integration are
finished too. Check a task off only at Done.

## Commands

| Command and scope | Result | Evidence |
|---|---|---|
| <exact command, working directory, files it covered> | pass / fail / unavailable / not applicable | <output, and how a failure was resolved> |

`unavailable` and `not applicable` are not passes. A missing tool leaves verification
incomplete; a check the project never defined is simply absent. Say which one it was.

## Decisions and blockers

- <time, actor, what happened, the repository evidence behind it, which task it affected>
- <blocker: the task, the exact plan wording that failed, the contradicting evidence, the
  preserved changes and their workspace, and whether it went back to planning>

## Completion

- [ ] Focused tests for changed files — <command and real result>
- [ ] Lint on changed files — <command and real result>
- [ ] Typecheck and build where the project defines them — <commands and real results>
- [ ] Task reviews and the final whole-change review recorded, blocking findings resolved
- [ ] Result compared with task.md, the approved plan and the accepted non-blocking items
- [ ] Final diff and repository status checked; unrelated changes preserved; artifacts unstaged
- [ ] Any external action covered by authorization the user actually gave for that action
