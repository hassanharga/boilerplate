# Strict mode routing

This is the existing strict protocol. Paths such as `agents/`, `assets/`,
`references/` and `scripts/` below are relative to this skill directory, not this
reference file. Read this workflow only for strict handoffs.

# Implement Plan

Verify the reviewed handoff, then implement its approved behavior. The task snapshot,
plan, normative specification and saved verdict evidence are immutable. Discoveries and
progress belong in the controller-owned execution ledger.

## Protocol and supporting files

User instructions and active repository instructions take precedence over workflow defaults.
This skill defines the execution gate, approved routing, immutability, replanning and
verification boundaries. Do not invoke a workflow or required subskill that demands forbidden
installation, commits, destructive cleanup, full-suite tests, concurrent writes or design changes.

- `agents/implementer.md`: read before delegating; fill its full self-contained brief.
- `references/execution-review.md`: read before the first implementation task; defines task
  review and final review for every route, including controller execution.
- `assets/ledger-template.md`: execution state and resume evidence.
- `scripts/fingerprint.py`: read-only gate; use this skill's own copy.
- `scripts/artifacts.py`: creates a task-folder `.gitignore` containing `*` and verifies it.
- `tests/test_contract.py`: run focused checks after changes with
  `python3 -B -m unittest discover -s <skill-dir>/tests -p test_contract.py -v`.
  Keep these scripts and tests byte-identical to the copies in `plan-and-challenge`.

## 1. Verify the Execution Gate

Require the plan path and read its complete saved contents. Resolve its single literal
Review declaration from the plan directory and read that complete review, including history.
Reject missing, duplicate, malformed, placeholder or unreachable metadata. Read its explicit
Specification declaration, which is either a real path or `none`.

An approved plan carries exactly this metadata, with the gate line copied verbatim and the
Specification declaration either a real path or `none`:

```markdown
> **Execution gate:** REQUIRED: Before implementation, invoke `implement-plan` with this plan path. It opens the linked review, requires `APPROVED`, and recomputes the exact-byte fingerprints. A missing or mismatched approval returns to `plan-and-challenge`; a valid approval continues with the execution workflow or routing rule named by this plan.
> **Review:** `./review.md`
> **Specification:** `<real-path-or-none>`
```

Read it to recognize a valid handoff, never to add or repair one: writing this stamp is
`plan-and-challenge`'s controller step, and a plan you stamp yourself is not an approved plan.

Run before any code change:

```bash
python3 <skill-dir>/scripts/fingerprint.py --verify <review-path> --plan <plan-path>
```

Exit 0 is the only pass. The script requires `plan-approval-v2`, the latest run's `APPROVED`
decision, exact saved input fingerprints, the qualifying saved verdict and its fingerprints,
the literal gate stamp, and matching review/specification declarations. It also requires
`task.md` beside the supplied plan. Fenced examples, duplicate fields, pending runs and
legacy approvals cannot authorize execution.

A nonzero exit returns the evidence to `plan-and-challenge` without implementing. Missing
or unusable script: stop and restore the tested tool; do not substitute manual hashes.
`READY_FOR_USER_APPROVAL` is not `APPROVED`. Only the user's explicit approval recorded by
`plan-and-challenge` can convert a completed local fallback. Do not repair or upgrade an
approval yourself. Record the exact script path, result and current run ID in the ledger.

## 2. Refresh Context and Reconcile a Resume

Read repository instructions (`AGENTS.md`, `CLAUDE.md`, `learnings.md`) before editing or
running project commands. Read frozen `task.md`, the declared specification, plan, review
and approved open Minor findings. Do not refetch Jira during normal execution. A changed
user requirement returns to planning for a refreshed snapshot and review.

Derive the task folder from the exact supplied plan, normally
`docs/agent-plans/<task-id-or-slug>/`. Find its existing `implementation.md`, or its explicitly
recorded workflow ledger. An existing ledger means resume; append evidence without deleting
prior history. Never search unrelated roots or create a second ledger to bypass a blocker.

Before editing or writing the ledger, identify its current controller/session and next
action. Before taking over from a different controller, obtain its explicit release or verify
that its session has ended, then reconcile outstanding workers and writes. Record the new
controller and takeover evidence before proceeding. A stale
timestamp alone does not prove inactivity; resolve unknown liveness before takeover. For a
new ledger, record yourself as controller. This is an ownership protocol, not a filesystem lock.

Before editing:

1. Record repository root/identity, starting revision, branch, current worktree, and existing
   staged, unstaged and untracked changes. Protect user changes as well as other agents' work.
2. Match the current workspace to the ledger. For each completed task, inspect its recorded
   worktree and whether its changes were integrated. Missing work in another checkout does
   not prove the task is incomplete. If a recorded workspace is unavailable, record that
   uncertainty and resolve its location before redoing or overwriting work.
3. Re-run the approval gate on resume, then verify completed work in its actual workspace
   and run only its directly affected tests. Reconcile the ledger with that evidence.
   Distinguish `Implemented`, `Reviewed`, `Integrated` and `Done`; resume the first genuinely
   incomplete task and carry forward blockers.
4. Verify planned files, symbols, commands and dependencies against the current tree. A
   material scope, contract, architecture or stale-path defect needs replanning. Local choices
   are allowed only when they preserve the approved design and observable behavior.
5. For each open Minor, record `address in task N` or `leave because <reason>`. A correction
   that edits a frozen input is not an execution task: leave it with a reason or replan.

## 3. Resolve the Approved Execution Route

Resolve the route or allowed alternatives named by the approved plan first. Do not choose
an internal default over an explicit named route. Perform compatibility checks transitively
through every required subskill. If a required route is incompatible or unavailable and the
approved rule contains no applicable alternative, return the routing defect to planning.

| Approved route | Conditions |
|---|---|
| Internal sequential delegation | One worker at a time; use the full implementer brief. This is the default only when the plan authorizes it. |
| Named sequential workflow | Its whole dependency chain must respect this gate, immutability, verification, ownership and active permissions. |
| Parallel isolated delegation | Independent tasks, one worktree per worker, non-overlapping ownership, and authorized integration method. |
| Controller-executed sequential | Delegation is unusable or prohibited, and the approved rule allows this fallback. All checks still apply. |

Delegation must be both usable and authorized. Missing tools, explicit restrictions and
exhausted capabilities count as unavailable. Allow at most one evidence-supported retry
for a transient failure. Before takeover, stop/reconcile a possibly running worker and its
partial edits; never create two writers. Record why the route changed and its approved basis.

Do not invoke `superpowers:subagent-driven-development`; it conflicts with this protocol.
Do not assume `superpowers:executing-plans` is compatible by name: inspect its current
required workflows too, including redirects and worktree/finishing setup.

Parallel setup must respect repository rules and available dependencies. From the repository
root, choose unique sibling worktrees, for example:

```bash
git worktree add ../<repo-name>-<task-slug>-<worker-id> -b <branch-name>
```

Do not nest worker checkouts in the project or install dependencies ad hoc. If prerequisites
are missing, use an approved compatible route or return that assumption to planning. Provide
absolute paths to the frozen documents in the original task folder; ignored artifacts need
not exist in each worker checkout. Outside Git, only sequential routes are possible.

Before parallel dispatch, confirm existing explicit authorization covers the exact integration
method, destination and scope. Merge/cherry-pick requires authorized worker commits too;
a patch route may remain commit-free. Record the authorizing message and constraints. Reuse
still-valid authorization on resume; ask only when it is missing, expired or out of scope.
Integrate one completed branch at a time and verify after each. Leave worktrees intact until
cleanup is explicitly authorized.

## 4. Execute, Review and Track

Prepare the ledger directory before creating or updating agent artifacts:

```bash
python3 <skill-dir>/scripts/artifacts.py <absolute-task-folder>
```

The task-folder `.gitignore` contains `*`, ignoring itself and all handoff artifacts. Never
write that wildcard in the repository-root `.gitignore` or edit Git's `info/exclude`.
The helper rejects tracked/staged task artifacts; do not force-add or untrack them to bypass
it. Preserve existing rules and verify actual Git exclusion. Outside Git, exclusion is not
applicable. If Git is unavailable, report hygiene as unverified and do not stage artifacts.

Use `implementation.md` beside `plan.md` and `review.md`, or the workflow ledger explicitly
recorded there. Only the controller writes the canonical ledger. Workers return reports;
never let several worktrees write it. Update it as work happens: owner/workspace, task state,
real command results, approved Minor outcomes, local decisions, review results and blockers.

After the gate and resume reconciliation, show the user a compact checklist of all
approved tasks before starting or resuming implementation. Use the plan's exact task
IDs/names and the ledger's reconciled states, including the current task and blockers.
Use a visible native task list when available; otherwise show a Markdown checklist
in chat. Keep `implementation.md` as the persistent source of execution state.

Update the ledger and visible checklist when a task changes state, becomes blocked,
or resumes. Refresh the same task list when supported; in chat, report compact
changed-task rows between the full starting and final lists. Preserve the distinction
between Implemented, Reviewed, Integrated and Done in labels; check a task off only
at Done. On resume, rebuild the display from reconciled evidence, not an old UI state.
UI unavailability falls back to chat and never bypasses the gate or blocks execution.
Do not edit the frozen plan to track progress. Include the final task states and any
remaining blockers in the completion or interrupted-handoff response.

For each task:

1. Dispatch the owned task with all global constraints and absolute source paths, or execute
   it yourself under an approved controller route. Never run implementers concurrently in
   the same working tree; file ownership cannot isolate shared outputs or lockfiles.
2. Apply TDD to behavior changes and fixes: observe the relevant failing test, make the
   smallest correction, and re-run it. Preserve unrelated work and stay within scope.
3. Run tests only for changed files and their directly affected tests. A full suite requires
   explicit user authorization and runs serially. Lint only changed files; typecheck and
   build remain project-wide where those commands exist. A pre-commit hook does not replace
   checks whose successful output has not actually been observed.
4. Apply `references/execution-review.md` before advancing dependent work or integrating.
   Fix implementation defects within the approved design; plan defects go back for review.

When an approved task proves unimplementable, stop it, preserve its partial edits, and record
its exact plan text, contradictory repository evidence, workspace and focused command results.
Return the absolute ledger path, affected task IDs, preserved-work baselines and current
controller/next action to `plan-and-challenge`. Planning must read and reconcile that ledger
before revising; reports from memory do not replace the saved execution evidence.
In a shared sequential tree, pause further implementation. An independent task may continue
only in a separate isolated worktree without depending on the blocker. Do not integrate any
parallel branch while reapproval is pending. After a revised plan passes its new gate, compare
all preserved work against that revision and reverify before resuming or integrating.

## 5. Complete the Handoff

- Run focused tests and changed-file lint, plus project-wide typecheck and build. Report
  exact commands and pass/fail/unavailable/not-applicable evidence. Missing tools or commands
  are not passing checks; never suppress a failure to report completion.
- Complete task reviews and the final whole-change review using
  `references/execution-review.md`. Resolve blocking findings and record Minor dispositions.
- Compare the final result against frozen task, specification, plan and assigned Minors.
- Re-run the gate after the last change. An input/evidence mismatch returns to planning;
  never reapprove your own implementation changes to the handoff.
- Check repository status and confirm agent artifacts are not staged. Preserve baseline
  user changes and identify remaining blockers or verification limits honestly.
- Stop at authorization boundaries: commits, pushes, integration, publication, deployment,
  messaging and shared-state cleanup require explicit authorization covering that action.
  Existing valid authorization need not be requested again.
