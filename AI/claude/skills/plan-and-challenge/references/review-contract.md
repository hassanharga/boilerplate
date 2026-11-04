# Review Contract

Read before challenging and before recording approval. Schema: `plan-approval-v2`.

## Findings and evidence

Classify the effect of implementing the plan as written:

| Severity | Boundary | Approval |
|---|---|---|
| Blocker | Wrong, unsafe, data-losing or impossible implementation. | Blocked. |
| Major | Missing/weakened/contradictory requirement, unsupported observable constraint, or missing/stale/wrong-target reference. A reasonable implementer can build the wrong thing. | Blocked. |
| Minor | Clarity/naming/order that cannot change observable behavior and a competent implementer resolves correctly. | May remain open with an explicit disposition. |

Valid source/specification targets may be outside the task folder. Resolve paths from the
plan's intended directory; containment is not a requirement. Do not downgrade Blocker/Major
to obtain approval. A requirement conflict needs a task-owner decision, not an agent rewrite
of the normative source.

Use category Scope, Correctness, Architecture, Reliability, Security, Testing or Execution.
Assign stable `PLAN-NNN` IDs sequentially across the review history and preserve earlier
findings. The controller may normalize IDs, not invent actor responses.

```markdown
### PLAN-001 — <title>
- Severity: <Blocker | Major | Minor>
- Category: <category>
- Status: <Open | Resolved | Rejected | Deferred>
- Source evidence: <exact requirement, or none — plan adds this>
- Document evidence: <plan/specification location>
- Repository evidence: <file and symbol, or not applicable>
- Risk: <concrete consequence>
- Suggested resolution: <smallest sufficient correction>
- Planner response: Pending
- Verification: Pending
```

`Pending` stays until actual output returns. Rejection requires evidence and independent
verification; a planner calling its own correction resolved is not verification.

Both directions are required before any `CLEAR`, including lightweight and clean challenges:

```markdown
## Requirement Coverage
| Source requirement | Exact plan location | Status | Evidence |
|---|---|---|---|
| <each task/specification requirement> | <executable step> | <Covered / gap> | <same modality and qualifiers> |

## Plan Constraint Evidence
| Material plan constraint | Plan location | Source or repository evidence | Status |
|---|---|---|---|
| <one observable behavior> | <step> | <exact quote or file + symbol> | <Supported / gap> |
```

A pointer to a specification, a test assertion replacing an ambiguous step, or an inference
is not coverage. Preserve `return` versus `throw`, exact counts, identity and relative order.
Split combined constraints into atomic rows. Independent requirements do not establish their
relative ordering. Reopen cited sources. Where evidence does not select one valid behavior,
leave bounded discovery or report ambiguity; never invent a stricter contract.

Lightweight may render these as two short lists with the same information. Save them, not
only a verdict. Full verifiers rebuild both tables rather than adopting the challenger's.

## Execution readiness and replanning

Before CLEAR, verify that each executable task has a stable name or ID, intended behavior,
owned file paths or bounded directory scope, and a focused verification command (or a concrete
reason a check does not apply). Record dependency task IDs and required interface names and
signatures when tasks depend on one another; use explicit none when independent. Repository
inspection may supply mechanical brief details, but may not invent scope, contracts or
ordering after approval. One task is sufficient for small work. Missing information that
prevents a complete implementer brief or requires a design decision is Major.

On return from execution, the controller, planner/reviser and reviewer must read the existing
`implementation.md` beside the plan, or the workflow ledger explicitly linked by plan/review.
Inspect preserved changes in their recorded workspaces, including unintegrated work, actual
command results, local decisions and blockers. Do not treat a missing checkout as unfinished
work. Resolve unavailable workspaces or unknown ownership before replanning affected tasks.

Record the ledger path, observed revision/time and repository/worktree baselines in review
Inputs. In the revised plan, map each completed or partial task to retain, adapt, or supersede,
with evidence and its remaining work; preserve stable IDs or record their mapping. Superseding
work does not authorize deleting it. Carry forward unresolved blockers and dependencies.
Review this reconciliation along with the full revised plan. Before approval, recheck the
ledger/workspace evidence; a material change requires reconciliation and renewed review of
the affected candidate. The ledger stays mutable execution evidence, outside approval hashes.

## Run state and ownership

`Inputs` records task provenance/update/capture time, normative extract, task/specification
paths and ownership, plan path, repository/root/branch, artifact-ignore result, and any
mechanical reference-transport mapping. Use absolute document paths in dispatches.

For a new run, choose a unique identifier (for example `1`, `2` or a UUID). Before revising
or dispatching, append this invalidation with real run ID and controller identity:

```markdown
## Run <unique-run-id>

## Protocol State
- Mode: <full | lightweight | local-fallback>
- Challenge venue: <fresh subagent | separate session | local fallback>
- Current owner: <agent/session>
- Next action: <actor and pending step>
- Required review lens: <general plus domain when needed>
- Round: <1 of 2>
- Review dispatches used: <0 of 4>
- Reviser dispatches used: <0 of 2>
- Delegation: <usable and authorized, or failure/restriction evidence>

## Final Decision
- Status: Pending
- Approval schema: plan-approval-v2
- Run ID: <same-run-id>
- Recorded by: <controller>
```

The gate reads this block in the latest run, so every field must hold a real value: an
unfilled `<placeholder>` fails just as a missing line does. `Mode` must equal the approved
decision's `Review mode`. `Round` counts from 1 and stops at 2; review dispatches stop at
4 and reviser dispatches at 2, each written as `N of <limit>`. Full approval requires at
least 2 recorded review dispatches, because full mode spends a challenger and then a fresh
verifier per completed round. Lightweight permits one round, one initial review and at
most one revision/recheck, even though its counter denominators retain the full-run limits
for possible escalation. The gate checks declared counts, not actual dispatch history:
consistent invented counters or reviewer identities are not authenticated by this check.

Pending may be followed by round activity and another decision. READY_FOR_USER_APPROVAL
may be followed only by explicit user approval through local-fallback; it cannot reset to
Pending. APPROVED and BLOCKED are terminal: neither may be followed by another decision in
the same run. Round-level BLOCKED verdicts belong in round reports, not terminal decisions,
unless the run is ending. The gate validates these transitions in the latest run.

The last decision contains only its declared schema fields and blank lines. Visible prose,
unknown fields, bullets, bold text and headings after it invalidate approval. Fenced examples
and HTML comments are non-protocol text and ignored; actual activity must never be recorded
there. Begin a new run before new review activity after a terminal decision. Never edit old
decisions or reuse a run ID. Within a run, transfer controller ownership explicitly;
only the recorded current owner writes `review.md`.

Resume at the saved Next action with existing counts and pending work. Do not rerun completed
review roles, restart counters, or consume a verifier before a required revision returns.
If a run exhausts its budget or cannot obtain required review, record BLOCKED or Pending
as appropriate; user direction is needed before a fresh run to continue the same unresolved work.

## Bind each verdict to its candidate

Each reviewer computes task/plan/specification fingerprints immediately before reading them,
reads them in full, then recomputes before returning. A changed file means `BLOCKED`, never
`CLEAR`. It returns the actual hashes it reviewed, alongside full findings and tables.
Use the skill-owned script's print mode:

```bash
python3 <skill-dir>/scripts/fingerprint.py <task-path> <plan-path> [<specification-path>]
```

The controller preserves each real report in a new file, e.g. `verdict-<run>-r1-verifier.md`.
Copy its returned evidence block exactly; use the absolute paths the reviewer received.
Do not overwrite earlier reports or substitute controller-computed candidate hashes.

```markdown
## Review Evidence
- Run ID: <current-run-id>
- Role: <challenger | verifier | lightweight-challenger>
- Reviewer: <actual agent/session identifier>
- Verdict: <CLEAR | BLOCKED>
- Task snapshot: <absolute-task-path>
- Task fingerprint: <reviewed-digest>
- Plan: <absolute-plan-path>
- Plan fingerprint: <reviewed-digest>
- Specification: <absolute-specification-path-or-none>
- Specification fingerprint: <reviewed-digest-or-none>
```

Use exactly one Review Evidence block per saved report, with no duplicate keys. Do not put
active metadata inside a Markdown fence or comment. Paths in a report resolve from that
report's directory; approval paths resolve from the review directory. Digests cover exact
saved bytes. For no specification, both specification fields must be literal `none`.

## Approval preflight and final decision

Check all of the following before writing `APPROVED`:

- No Blocker/Major remains. Record open Minor count/IDs and dispositions. Use `0` or `none`
  for no open Minors. Otherwise use `N; PLAN-001: address in task T1; PLAN-002: leave because
  <concrete reason>` on one line, with N matching the number of unique IDs. Each disposition
  must identify a task or explain why it is left open; semicolons separate findings. When a
  disposition assigns an ID-shaped task, that ID must appear in the approved plan — an
  assignment to a task nobody will execute is an open finding wearing a closed one's clothes.
- `Verdict by` and `Recorded by` are different actors. The controller records the decision;
  someone else cleared the plan. One identity in both fields is self-approval, and the gate
  rejects it regardless of the role written on the evidence.
- Full mode has the current round's actual fresh verifier `CLEAR`; lightweight has its
  permitted challenger `CLEAR`. An older candidate's or another run's verdict is invalid.
- Each current input matches the report's path identity and reviewed digest. `task.md` is
  a regular non-symlink file beside the supplied plan. Its Review/Specification declarations
  match these saved inputs.
- The saved evidence file contains the actual returned report; hash that file too.
- All paths and digests are concrete, and all actor identities are real. No placeholders,
  `Pending` input fields or all-zero digests may appear in an approved decision.

Append this as the terminal section in the current run, using concrete values:

```markdown
## Final Decision
- Status: APPROVED
- Approval schema: plan-approval-v2
- Fingerprint algorithm: sha256-exact-bytes-v1
- Run ID: <current-run-id>
- Review mode: <full | lightweight | local-fallback>
- Task snapshot: task.md
- Task fingerprint: <digest matching the reviewer report>
- Plan: plan.md
- Plan fingerprint: <digest matching the reviewer report>
- Specification: <path-or-none>
- Specification fingerprint: <digest-or-none>
- Evidence: <saved-qualifying-report-path>
- Evidence fingerprint: <hash-of-saved-report>
- Open minor findings: <0 or none; otherwise N; PLAN-NNN: address in task T1 or leave because reason>
- Verdict by: <same identity as report Reviewer>
- Recorded by: <controller>
```

Then run `fingerprint.py --verify <review> --plan <plan>` and require exit 0.
The gate rejects legacy schemas, pending runs, duplicate fields, illustrative decisions,
unmatched declarations, missing required artifacts, changed evidence, candidate drift,
self-approval, unfilled or overspent run state, and Minors assigned to absent tasks.
It checks record consistency; it does not authenticate an agent or judge its reasoning.
Two identities in the record still prove only that two identities were written down.
Never fabricate independence or replace actual reviewer evidence with plausible prose.

## Local fallback and user approval

When independent review is unusable, complete and save the same checks locally. All
Blocker/Major findings must be resolved before `READY_FOR_USER_APPROVAL`; unresolved ones
remain BLOCKED. Record why independent review was unavailable. The execution gate rejects
both states.

Only explicit user approval of the reviewed candidate can convert READY. Present its
saved paths and fingerprinted candidate first. If any input changed since the local review,
review it again and obtain approval of that changed candidate. Preserve the actual user
message/time and candidate hashes in a new evidence file using Review Evidence with
`Role: user`, `Reviewer: user`, `Verdict: APPROVED`, and a concrete `User approval` field
containing the message reference or exact approval wording. Retain the local findings/tables.
Append a new Final Decision with `Review mode: local-fallback` and `Verdict by: user`.
Do not rewrite READY history or interpret elapsed time as consent.

For an `address in task T99` Minor disposition, declare that exact ID in a task heading,
list entry or table row (for example `### T99 — Follow up`). A prose mention or the
substring T99 inside T990 is not a task declaration. Named prose targets still require
the reviewer to verify that the task exists; the gate does not parse their meaning.
