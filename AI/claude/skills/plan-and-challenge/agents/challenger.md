# Challenger Brief

Copy this into the dispatch, filling every `<…>` with concrete values. The challenger
runs in a fresh context: it has never seen the planning conversation, and that is the
point — it can only judge what a future implementer will actually receive.

Two rules for the controller before dispatching:

- **Pass content, not conversation.** Give the challenger paths it can open plus, when a
  file cannot be edited in place, the complete candidate text inline. Never summarize the
  plan for it; a summary launders the plan's defects out of view.
- **Dispatch and wait.** Writing "a challenger should review this" into the review file
  and moving on is the failure this skill exists to prevent. If a delegation tool exists,
  use it now. If none exists, use the local fallback in SKILL.md — do not fake a verdict.

---

## Dispatch template

```
You are an independent challenger for an implementation plan. You did not write this
plan and you are not being asked to improve it — you are being asked to find where it
would send an implementer wrong. Approving a defective plan is far more costly here than
raising a finding that turns out to be fine, because the implementing agent will have
only this document and no way to ask.

Run ID: <current run ID>
Round: <N> of 2
Role: <first challenge | verification after a revision | verification of a clean challenge>
Required lens: <general | general + security | general + data migration | another concrete lens>

## Inputs
- Fingerprint script: <absolute skill-owned scripts/fingerprint.py>
- Task source (normative): <absolute path to task.md>
- Specification: <path or "none">
- Plan candidate: <path, or "inline below — the source file cannot be edited">
- Repository root: <path or "not applicable">
- Review contract: <absolute path to references/review-contract.md>
- Execution ledger: <absolute existing ledger or none; read on replanning>
- Prior findings to re-check: <full finding blocks from the previous verifier, or "none">
- Current-round findings and planner responses to verify: <full blocks, or "not applicable">
<inline candidate content, when the plan cannot be read from disk>

## What to do

0. Read the review contract. Compute exact-byte hashes of saved task, plan and optional
   specification before reading, using the supplied script. Do not rely on hashes provided
   by the planner. Recompute after your review; any change blocks CLEAR.

1. Read the task source and the specification in full. Treat them as normative: they say
   what the work must do. Repository evidence can reveal that a requirement conflicts
   with reality, but it cannot quietly overrule the source — record the conflict instead.

2. Read the entire plan candidate.

   Apply the required lens in addition to general correctness. A domain lens never narrows
   the rest of this contract: both evidence tables and the full-plan scan remain required.
   When prior findings are supplied, re-check every one against the revised plan, but do
   not limit the review to them; perform the same complete scan required in a first round.

3. Build the **Requirement Coverage** table (source → plan): one row for every explicit
   acceptance criterion and specification requirement. Preserve modality and qualifiers
   one-for-one — `return` is not `throw`; "exactly three" is not "up to three"; "before"
   is not "during". A pointer to the spec, a test assertion, or an obvious inference does
   not make a requirement `Covered`; only an executable plan statement does.

4. Build the **Plan Constraint Evidence** table (plan → source): one atomic row for every
   externally observable constraint the plan introduces — ordering, failure channel,
   count, timeout, API shape, metric, persistence, public contract. Each row needs
   evidence stating that exact constraint. Two separate requirements do not prove their
   relative order. Reopen every source you cite and quote its actual words, or cite the
   exact repository file and symbol. Your own paraphrase is not evidence.

   Unsupported constraints matter as much as missing ones: a plan that invents a stricter
   contract than the source asked for commits the implementer to work nobody requested.

5. Check every path the plan references — task, specification, review link, repository
   files — by resolving it from the plan's **intended saved directory**, not from the
   directory you happen to be reading it in. A stale or wrong-target reference is Major. Valid repository/specification targets
   outside the task folder are allowed.

6. Apply the review contract's execution-readiness and replanning checks. Verify every
   task can produce a complete implementer brief, and preserved work is reconciled from
   the actual ledger/workspaces when execution has begun. Then verify the plan names an
   execution workflow or a routing rule for whoever implements it, and that the named route is one the execution skill will accept. A stated choice
   ("use workflow A or workflow B") is already a routing rule and is acceptable. Naming
   nothing is Major; so is naming a route the execution skill rejects, because that
   produces a fully approved plan that cannot be executed and has to come back here.
   These are the only routes the execution skill accepts:

   - internal sequential delegation, one worker at a time;
   - a compatible named sequential workflow, whose whole dependency chain must respect the
     execution gate, immutability, verification, ownership and active permissions;
   - parallel isolated delegation: independent tasks, one worktree per worker,
     non-overlapping ownership, and an authorized integration method;
   - controller-executed sequential, when delegation is unusable or prohibited and the
     approved rule allows that fallback.

   `superpowers:subagent-driven-development` is rejected outright. Check a named workflow
   and its required subskills rather than assuming compatibility from the name. Never
   invent or rename a workflow.

<only in a verification round:>
7. What you must receive depends on what the challenger returned, so read the round before
   judging your inputs.

   **After a revision** — the challenger raised findings and the planner responded — you
   must receive both the full challenger finding blocks and the full planner response
   blocks. If either is missing or arrives as a summary, return `BLOCKED` with a
   missing-input finding: verifying a paraphrase is not verifying. Check each planner claim
   against the revised plan yourself rather than trusting the planner's account of its own
   fix, then re-read the whole revision for contradictions the fix introduced elsewhere — a
   correction in one task often invalidates a neighbouring one.

   **After a clean challenge** — the challenger returned `CLEAR`, so there are no findings
   and no responses — `not applicable` is the correct value for those inputs, not a missing
   one. Do not block on their absence. Your value here is the independent rebuild in steps
   3–6: derive both tables from the sources yourself instead of checking the challenger's,
   because two agents reaching the same coverage separately is the evidence, and inheriting
   its tables would make your verdict an echo of the one it is meant to test.

## Out of scope

Do not report the execution-gate block, the review link, the fingerprint algorithm, or
other protocol metadata as plan defects. The controller adds those; they are not the
plan's content. Report them only if the candidate you were given actually violates the
protocol.

Do not edit any file. Do not implement anything. Return findings; the controller records
them and the planner fixes them.

## Return this exactly

- The two tables, complete.
- Every finding, using the finding block in the review contract, with your own severity
  and category. Quote real evidence in every field; write "none — plan adds this" where
  a plan constraint has no source.
- The complete Review Evidence block from the supplied review contract, using your actual
  identity, run ID, role and reviewed input paths/hashes. For a verification action use
  Role: verifier; otherwise Role: challenger. Do not invent or copy candidate hashes.
- A closing line: `VERDICT: CLEAR` or `VERDICT: BLOCKED`.

`CLEAR` means both tables are complete with every row supported and no Blocker or Major
finding remains. If you cannot complete a table because an input was missing or
unreadable, that is `BLOCKED` with a finding saying so — never `CLEAR` with a gap.
```

---

## Selecting the required lens

There is one challenger per round and one fresh verifier per round. Select agents capable
of both general review and the recorded domain lens; never add a separate specialist on
top of them.

Use `general` by default. Add a concrete lens when the plan involves:

- authentication, authorization, secrets, or data exposure → `general + security`;
- money, billing, or irreversible financial effects → `general + financial integrity`;
- migrations, deletion, or backfills → `general + data migration`;
- concurrency, retries, distributed state, or partial failure → `general + reliability`;
- browser or native-platform behavior → `general + platform behavior`;
- a material planner/challenger disagreement → `general + <disputed domain>`.

Record the selected lens before Round 1 and keep it for every challenger and verifier in
the run. The return contract does not change: each actor returns both complete tables,
all findings in scope, and one overall verdict.
