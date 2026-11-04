---
name: plan-and-challenge
description: Use when preparing, reviewing, challenging or stress-testing a written implementation plan that another agent, session or person will execute - including "write up a plan for X", "review this plan", "get this plan challenged", or any handoff to docs/agent-plans/ - and when recording plan approval before implement-plan. Use it even when the user only says "plan this out" but someone else will do the work. Do not use to implement the plan.
---

# Plan and Challenge

Capture the requirements, write executable tasks, and get an independent challenge
before handing the plan to `implement-plan`. Planning does not authorize code changes
or external writes. User and repository instructions take precedence.

Strict approval requires `python3`. Artifact setup uses Python when available and
otherwise the manual equivalent below; Git is needed to verify repository exclusions.

**Invoked as `challenge-only`?** You are the reviewer, not the planning owner. Skip
all planning-method, protocol and venue questions, and all controller/approval steps.
Read the supplied task, plan and specification and determine the recorded protocol.
For simple, follow only the challenge-only paragraph in section 2 below. For strict,
read `references/review-contract.md` and the supplied role brief (challenger, fresh
verifier or lightweight challenger); return its complete evidence and reviewed-byte
metadata with CLEAR/BLOCKED. Do not use simple's CHANGES_NEEDED verdict for strict.
If inputs, mode or role are missing/conflicting, return a blocked report to the owner.
For automated CLI review, write nothing; the owner saves your report. A user-requested
manual strict handoff follows the explicit ownership steps in `references/challenge-venues.md`.

## Choose the protocol

For every new plan, ask the user to choose **simple** or **strict**; there is no
default. Explain briefly: simple records an independent review and approval; strict
adds exact reviewed-byte fingerprints, evidence records and bounded review rounds.
Honor an explicit choice already supplied for this plan. Wait for the answer before
starting mode-specific planning or review; silence is not a selection. Record
`Workflow: simple` or `Workflow: strict` in the plan and reuse the choice on resume.
If project instructions require strict, explain that constraint rather than offering
an incompatible simple route.

Recommend one and say why, then let the user decide. Strict earns its overhead when a
wrong plan is expensive to discover late: the implementer is a different agent or session
that cannot ask what you meant; the change touches a public contract, schema, migration,
authorization or money; several workers run in parallel; or the handoff may sit long
enough for its inputs to drift underneath it. Simple fits work you hand over inside the
same session, where a recorded independent review and a revision number catch a wrong
plan early and the byte-level machinery would mostly cost time. When the deciding factor
is uncertain, say which way it cuts rather than defaulting to the heavier protocol.

Also choose the planning method below before either protocol's planning steps.
For **simple**, follow the steps below. For **strict**, read
[strict-workflow.md](references/strict-workflow.md) instead; its full/lightweight
classification belongs only to that protocol and follows its existing criteria.

An existing execution-gate stamp, fingerprint approval, or `plan-approval-v2` record
means strict, even if someone adds a simple label. Never silently downgrade it.
Changing protocols requires the user's explicit decision and a separately reviewed
new handoff; preserve the original. If mode or approval records conflict, resolve
that in planning before any execution.

## Choose the planning method

For each new plan, ask: **Superpowers (default)** or **agent Plan mode**? This is
separate from simple/strict approval; either method can use either protocol. You
may ask both questions together. Honor an explicit method already chosen for this
plan and reuse it through revisions/resumes. Present Superpowers first and select
it when the user says to use the default; wait for the answer rather than treating
silence or a preselected option as a submitted choice. Record `Planning method`.

- **Superpowers:** read and follow `superpowers:brainstorming`, then
  `superpowers:writing-plans` when an implementation plan is warranted. Keep this
  skill's task folder and approval protocol; planning does not start implementation.
- **Agent Plan mode:** use the host's native planning mode when available and save
  the final plan in the task folder. If the agent cannot switch modes itself, ask
  the user to enable it; do not claim that a prompt has changed the host mode.

If the chosen method is unavailable or conflicts with active instructions, explain
the limitation and ask for an alternative; do not silently substitute direct planning.

## 1. Capture and plan

Read applicable repository instructions and any existing handoff before writing.
Follow the planning method selected above, within applicable instructions.

Keep one task folder at `docs/agent-plans/<task-id-or-slug>/`, under the repository
root or current directory outside Git. Resume an existing matching folder; do not
overwrite unrelated work. Before artifact writes, run this skill's helper:

```bash
python3 <skill-dir>/scripts/artifacts.py <absolute-task-folder>
```

It creates/verifies the task-folder `.gitignore` containing `*`. Never put that
wildcard in the repository root, edit Git's `info/exclude`, force-add artifacts or
untrack existing files to bypass a failure. Resolve setup failures before writing;
outside Git, exclusion is not applicable.

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

Use three files, following [simple-handoff-template.md](assets/simple-handoff-template.md)
for their layout:

- **task.md:** captured requirements and acceptance criteria, source/message
  provenance, capture time, and any external specification path. Preserve exact
  normative wording in a regular file; separate inference from user requirements.
  Ask before treating an ambiguous interpretation as a requirement. Keep this
  snapshot on every handoff; execution normally does not refetch Jira.
- **plan.md:** `Workflow: simple`, a revision number, `Status: Draft`, design and
  scope, named tasks with stable IDs, owned files, dependencies/interfaces, and
  focused verification. One task is enough for small work. Name any required
  execution route; otherwise sequential delegation with controller fallback is
  allowed. Parallel work needs independent tasks and isolated workspaces. It also
  carries the **Review** section this skill appends in steps 2 and 3 — reviewer,
  reviewed revision, findings and verdict live in the plan itself in simple mode,
  because there is no separate `review.md` to hold them.
- **implementation.md:** created by the execution controller for progress and resume
  evidence. On replanning, read it and inspect preserved work before changing tasks.
  Retain task IDs or give an explicit mapping; do not respecify completed work blindly.

Resolve supplied plan references from their original location before relocation.
Preserve supplied requirements and specifications; expose conflicts for the user's
decision. Provide absolute paths for cross-session or cross-worktree handoffs.

## 2. Challenge and resolve

After presenting the draft, always ask who will challenge this plan: **a fresh
subagent in the current session** or **another agent through its CLI**. “Same agent”
means a fresh subagent, not the planner reviewing its own work. Honor an explicit
choice already supplied for this plan; record it and reuse it through revisions
and resumes. Wait for the choice before dispatch. Do not infer it from availability.
For another agent, ask which CLI unless already named, then follow
[challenge-venues.md](references/challenge-venues.md) to launch it and exchange
reviews automatically. Use the same reference if a manual handoff is requested.

In **challenge-only**, read those sources and repository evidence, then return:
reviewed plan revision, reviewer identity, concrete findings and their evidence,
and `CLEAR` or `CHANGES_NEEDED`. Do not implement, edit the plan or grant approval.
Check requirements, feasibility, failure paths, interfaces, task ownership and
verification. Do not prescribe style changes without a concrete consequence.

The controller records the actual report in the plan's Review section. Resolve
material findings, revise the plan, and have the reviewer check the revised plan,
including affected interactions. The same independent reviewer may recheck; a
second verifier and fixed full/lightweight rounds are not required in simple mode.
Increment the plan revision for material revisions, including challenge fixes, so
the recorded verdict identifies the candidate it actually reviewed.
Stop and report unresolved blockers when review makes no progress; respect active
retry and resource limits rather than adding review agents indefinitely.

If the selected reviewer is unavailable, report the blocker and ask for another
route. If the user chooses self-review, perform the same checks locally and label
it self-review. Keep `Status: Awaiting user approval` until the user explicitly
approves that reviewed revision. Never invent another agent's report.

## 3. Approve and hand off

When the current revision has independent `CLEAR`, or explicit user approval after
self-review, set `Status: Approved`. In the Review section retain the reviewed
revision, reviewer, date, actual outcome, resolved findings, accepted non-blocking
items and any user approval. Preserve prior review entries when revising.

Before materially changing requirements, design, task scope or interfaces after
approval, set Draft, increment the revision and obtain a new challenge/approval.
Do not carry an old approval onto a new revision. Pure formatting corrections that
preserve meaning may be recorded without another challenge. Workers never revise
approved inputs; implementation discoveries go into the execution record.

Show the user the approved task IDs/names, remaining non-blocking items and absolute
plan path, plus the execution-record link if it exists. Approval is not task completion.
Hand off to `implement-plan`; it shows and updates the task checklist during execution.
Simple approval is a recorded review decision, not an exact-byte or tamper-proof gate.

## Skill maintenance

Simple mode uses `assets/simple-handoff-template.md` and the shared challenge-venues
reference. The review templates, agent briefs and review contract support strict mode;
do not load them for a simple handoff. Keep both skills' shared scripts and
`tests/test_contract.py` byte-identical. After changing either skill, run focused
contract tests serially:

```bash
python3 -B -m unittest discover -s <skill-dir>/tests -p test_contract.py -v
```

The documented strict stamp lives in `references/strict-workflow.md`.
