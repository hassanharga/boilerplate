# Strict mode routing

This is the existing strict protocol. Paths such as `agents/`, `assets/`,
`references/` and `scripts/` below are relative to this skill directory, not this
reference file. Read this workflow only for strict handoffs.

# Plan and Challenge

Save a plan a fresh agent can execute, obtain independent review, and bind approval to
exactly the saved bytes that reviewer inspected. Do not implement code or perform external
writes while using this skill. User instructions and repository instructions take precedence.

## Protocol essentials

- `task.md` and any normative specification define requirements. Preserve their modality,
  counts, ordering and failure channels; repository evidence cannot silently override them.
- The controller alone writes `review.md`. Challengers/verifiers return actual evidence;
  the planner/reviser writes the plan. Never invent another actor's output or approval.
- A qualifying independent verdict can authorize `APPROVED`. A self-review can only reach
  `READY_FOR_USER_APPROVAL`; conversion requires the user's explicit approval.
- Use approval schema `plan-approval-v2` and fingerprint algorithm `sha256-exact-bytes-v1`.
  Legacy approvals need a new review; never add new fields to pretend old review covered v2.
- Every new review run invalidates prior approval immediately. Approved input changes
  require another review. Execution discoveries belong in the execution ledger.

Supporting files, read when needed:

- `references/review-contract.md`: findings, both evidence tables, reviewer fingerprints,
  run state and approval schema. Read before the first challenge and before approval.
- `references/challenge-venues.md`: automated CLI review and manual session handoffs.
  Read when launching another CLI or preparing/receiving a manual challenge-only handoff.
- `references/lightweight-mode.md`, `agents/lightweight-challenger.md`, and
  `assets/light-review-template.md`: lightweight procedure, brief and saved evidence.
- `agents/challenger.md`, `agents/reviser.md`, `assets/review-template.md`: full-mode roles.
- `references/red-flags.md`: responses to proposed protocol shortcuts.
- `scripts/fingerprint.py`: read-only hashing and gate verification. Use this skill's own copy.
- `scripts/artifacts.py`: task-folder `.gitignore` setup; read its help before first use.
- `tests/test_contract.py`: focused behavioral tests. After editing either skill, run
  `python3 -B -m unittest discover -s <skill-dir>/tests -p test_contract.py -v`.
  Keep both scripts and the test file byte-identical in the two skills.

## 0. Select the Review Mode

| Observable state | Action |
|---|---|
| No written handoff; implementation stays with this agent in this conversation | Do not use this skill. Follow the user's normal design/implementation workflow. |
| A handoff exists and all five criteria below hold | Lightweight; read `references/lightweight-mode.md`. |
| Any other handoff, including an unclear criterion | Full. |

Lightweight requires all five:

- one clear behavior change;
- at most two source files plus their directly affected tests;
- no public API, schema, migration, authorization, security, concurrency, retry,
  infrastructure or cross-service surface;
- no unresolved design question;
- reversible by reverting one commit, if committed.

Assess the task and specification, not the apparent size of the plan. Record the mode;
never downgrade a full run. A supplied specification is normative in either mode.

## 1. Prepare the Sources and Plan

Read repository instructions (`AGENTS.md`, `CLAUDE.md`, `learnings.md`) before setup.
If supplied a plan, read its existing review link and history from its original directory
before choosing a destination. On return from execution, read `implementation.md` beside
that plan, or the workflow ledger explicitly linked by the plan/review. Follow the execution
reconciliation requirements in `references/review-contract.md` before revising; do not plan
from review history alone. Preserve the plan and any user-selected planning method.
For a new plan, use the entrypoint's “Choose the planning method” question in both full
and lightweight mode: Superpowers (default) or agent Plan mode. Follow that selection
and its availability rules; do not silently substitute a direct plan. A Spike or
Bounded outcome from brainstorming need not become an implementation plan.

Save handoffs in `docs/agent-plans/<task-id-or-slug>/`, rooted at the repository root or
current directory outside Git. Use a ticket key or `YYYY-MM-DD-<task-slug>`. Detect an
existing folder; resume the same handoff or choose a unique sibling, never overwrite an
unrelated task. Use `plan.md`, `review.md`, `task.md`, and later `implementation.md`.

Record `Workflow: strict` in the plan beside its revision. The stamp and the approval
record also prove strict, but only after Section 2 writes them; the label is what lets an
agent reading an interrupted handoff name the protocol without guessing from absence.

Before saving artifacts, run:

```bash
python3 <skill-dir>/scripts/artifacts.py <absolute-task-folder>
```

This creates a `.gitignore` containing `*` inside that task folder, ignoring itself and
its artifacts. It preserves existing folder rules, rejects tracked/staged artifacts and
repository-root targets, and verifies exclusion with Git. Never write a wildcard in the
repository-root `.gitignore`, edit Git's `info/exclude`, force-add artifacts, or untrack
existing files automatically. A setup failure stops artifact writes until resolved.
Outside Git the script creates the directory without needing exclusion. If Git is unavailable
in a possible repository, exclusion remains unverified: do not stage or claim Git hygiene passed.
Without `python3`, use the manual `.gitignore` equivalent in the entrypoint's Section 1 and
record how exclusion was verified. That allowance covers artifact hygiene only; Section 4's
approval gate has no manual substitute.

Create `task.md` before challenging: title, description, acceptance criteria, source URL/ID,
source-updated time when available, capture time, and exact normative wording. Record the
source provenance in review Inputs. Later agents normally read this snapshot, not newer Jira.
Keep `task.md` as a regular file beside the plan, never a symlink. Without Jira or a supplied
specification, preserve the user's explicit request verbatim with its message provenance;
separate inferred requirements and unresolved questions from that normative text. Obtain the
user's decision before promoting an inference or ambiguous interpretation into a requirement.
An exact copy of an already explicit request needs no repeated sign-off. Only a task-owner
change refreshes normative requirements and triggers a new run.

Distinguish an externally supplied normative specification from a planner-owned design
note. The reviser cannot weaken the normative specification to accommodate the plan.
A requirements conflict needs the task owner's explicit decision before updating its snapshot.

Persist output-only plans exactly. For a relocated supplied plan, preserve body content;
mechanically rebase relative document/code references to their original resolved targets
and record that transport mapping. Do not repair existing broken references or substantive
requirements before Round 1. Relative paths resolve from the intended saved plan directory;
valid absolute paths and targets outside the task folder are allowed. Missing or wrong-target
references block clearance.

Ignored artifacts travel by accessible filesystem paths or a user-authorized copy of the
whole task folder, not automatically through Git. Verify all document paths are reachable
from the receiving session or worktree.

## 2. Establish the Handoff and Invalidate Older Approval

For the same plan, preserve review history and append a new run. For a new immutable-source
copy, create its own sibling task folder and review; never reuse an ambiguous old review link.
Before revising or dispatching, append `## Run <unique-run-id>` and its Pending decision using
`references/review-contract.md`. If interrupted after the run heading, the gate rejects the
older decision even before Pending has been written. Record the current owner and next action.

Add this literal stamp, normalizing metadata to exactly one of each declaration:

```markdown
> **Execution gate:** REQUIRED: Before implementation, invoke `implement-plan` with this plan path. It opens the linked review, requires `APPROVED`, and recomputes the exact-byte fingerprints. A missing or mismatched approval returns to `plan-and-challenge`; a valid approval continues with the execution workflow or routing rule named by this plan.
> **Review:** `./review.md`
> **Specification:** `<real-path-or-none>`
```

The Specification declaration is `none` when absent; otherwise use its real path. Resolve
both declarations from the plan's directory. Copy the Execution gate line verbatim. Metadata
normalization and reference transport are controller setup; record them outside findings.
The challenger must receive the exact saved, post-stamp candidate.

Before approval, make the plan dispatchable using the execution-readiness requirements in
`references/review-contract.md`: stable task names, file scope, required interfaces/dependencies
and focused verification. One named task is enough for small work. Preserve all worker-handoff
instructions. A missing execution route or an incompatible
required route is Major; the planner resolves it during review. `implement-plan` is the
route authority. Accepted routes are internal sequential delegation, a compatible named
sequential workflow, parallel isolated delegation with authorized integration, and controller-
executed sequential when delegation is unusable and the approved rule permits fallback.
For a new default plan, name internal sequential delegation with that controller fallback.
Never replace a user's explicit named route silently. Reject `superpowers:subagent-driven-development`.
Check a named workflow and all its required subskills against active instructions before approval.

## 3. Challenge and Revise

After presenting the draft, always ask who will challenge this plan: a fresh subagent
in the current session or another agent through its CLI. “Same agent” means a fresh
subagent, not self-review. Honor an explicit answer for this plan, record `Challenge
venue`, and reuse it through revisions and resumes. Wait for the choice before dispatch.
For another agent, ask which CLI unless already named. Follow
`references/challenge-venues.md` for automated CLI review or a requested manual handoff.
An unavailable selected venue may require a new user choice; do not silently change it.

Read the review contract. Select general correctness plus any required domain lens from
`agents/challenger.md`. Keep that coverage in every challenge and verification. Every
verdict must include both complete evidence tables/lists and exact reviewed-byte metadata.

Full mode has at most two rounds. Each round permits one independent challenger, at most
one reviser, and one fresh verifier: four review dispatches and two reviser dispatches total.
A domain lens changes reviewer selection, not the dispatch count.

1. Dispatch one challenger against the complete task, specification, saved candidate and
   repository evidence. It reopens sources and returns `CLEAR` or `BLOCKED` with evidence.
2. If blocked, record findings and obtain the planner/reviser's actual saved changes and
   full responses. Do not prefill them. If clear, skip revision.
3. Dispatch a fresh verifier in either case. After revision, pass every full finding and
   actual response; after a clean challenge, use `not applicable`. The verifier independently
   rebuilds both tables, checks all responses and scans the whole candidate.
4. Only a fresh verifier's qualifying `CLEAR` ends a full round in approval. A blocked
   verifier starts Round 2 with its findings. A second blocked verifier ends `BLOCKED`;
   return unresolved findings to the user without implementation or extra review dispatches.

Minor findings may remain open if they cannot change observable behavior. Any ambiguity
with a reasonable wrong implementation is Major. Never downgrade severity to obtain approval.
Lightweight transitions and their dispatch accounting are defined in `references/lightweight-mode.md`.

Delegation is available only when usable and authorized. A missing tool, explicit prohibition,
or exhausted capability is unavailable. After a transient failure, allow at most one retry
when new evidence supports it; count attempted dispatches against the run's limits and
inspect any partial output first. Never invent a verdict or expand the budget to hide failure.
When independent review cannot complete, record Pending and the failure. A local fallback
may perform all checks and record `READY_FOR_USER_APPROVAL` only after all Major/Blocker
findings are resolved; otherwise record `BLOCKED`. Only the user can approve that fallback.

## 4. Approve the Reviewed Bytes

Read the approval/evidence format in `references/review-contract.md`.

1. Preserve the real final reviewer report as a uniquely named evidence file in the task
   folder. Do not overwrite earlier evidence files. The report contains the reviewer's
   task/plan/specification paths and hashes from its actual review, checked before and after
   reading. The controller must not replace those hashes with later computed values.
2. Compare the saved task, plan and specification with those reviewed hashes. Any change,
   including transport or formatting after review, needs another independent review within
   the remaining budget; never approve by merely rehashing it.
3. Hash the saved evidence file. Append a complete `## Final Decision` for the current run
   with schema, mode, input hashes, evidence path/hash, real identities and Minor dispositions.
   Full needs verifier/CLEAR; lightweight needs lightweight-challenger/CLEAR. Local fallback
   needs explicit user approval of the unchanged reviewed candidate, preserved as user evidence.
4. Verify the actual handoff:

   ```bash
   python3 <skill-dir>/scripts/fingerprint.py --verify <review-path> --plan <plan-path>
   ```

   Exit 0 is the only pass. On failure, correct recording mistakes only when the original
   returned evidence supports them; changed inputs require renewed review. If the script is
   missing or unusable, stop and restore the tested tool. There is no manual-hash bypass.

`APPROVED` and `BLOCKED` decisions are terminal within their run. Pending may advance to a
final result; READY may advance only through explicit user approval in local-fallback mode.
A terminal decision contains only the schema fields; put reports and narrative before it.
New review activity after a terminal decision begins a new run;
operational execution notes belong in `implementation.md`. Hashes prove consistency of
recorded bytes, not reviewer authenticity or correctness: retain actual independent outputs.
After approval, task snapshot, plan, normative specification and saved verdict evidence stay
immutable. Give the next agent the absolute plan path and its gate invocation.
In the user-facing approval handoff, show a compact list of the approved plan's exact
task IDs/names and link any existing execution ledger. Approval does not mean those
tasks are complete. `implement-plan` reconciles and displays their execution states
on start/resume, then keeps its visible checklist synchronized with the ledger.
