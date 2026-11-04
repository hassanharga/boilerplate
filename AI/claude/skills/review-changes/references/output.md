# Review Output Contract

Every review emits exactly six parts, in this order, and nothing else:
**Summary → Review path → Findings → Conflict notes → AC coverage → Verdict**.
Do not invent sections. Verification, evidence, and scope notes belong inside
those six parts, not in blocks of their own.

## Print findings as text, not through a finding tool

Findings are markdown in the response body. Do not call `ReportFindings` or any
other structured finding reporter during a review, and never emit the same
finding twice. A rendered finding panel pushes the substance off the page and
makes each review a different shape; the author should reach the defects by
reading straight down the reply.

## Change map

The map is how the reader understands what the PR does before reading defects.
It lives **inside Summary**, right after the prose — it is not a separate part.
Include one whenever the change has a traceable flow; omit it only when there is
no behavior to draw (a version bump, a rename) or when no faithful version fits
the cap below.

Pick the rendering from the surface, not from taste:

- **Terminal (Claude Code CLI and any plain-text harness): compact ASCII/Markdown
  flow.** Mermaid does not render there and arrives as raw source.
- **GUI surfaces that render Mermaid (Codex, web, IDE panels): Mermaid.** Use
  `flowchart` for directed flows, `stateDiagram-v2` when state transitions are the
  subject.
- Unsure which surface you are on: ASCII.

Make the nodes behavior-first: the trigger or input, the changed decision,
validation, transformation, or orchestration, the data or event crossing a
boundary, the resulting state mutation or side effect, the downstream outcome, and
what protects it. Label arrows with the condition, value, or event when the flow
needs it. Mark `CHANGED`, `NEW`, or `REMOVED` where the relationship to unchanged
context would otherwise be ambiguous. Group into `Setup` / `Execution` / `Teardown`
when lifecycle is part of the changed behavior.

Use a file or symbol name only as an optional anchor. A path inventory such as
`controller.ts -> service.ts -> repository.ts` is not a change map — rewrite it as
behavior, for example `request -> CHANGED: reject stale assignment -> persist
Rejected -> publish AssignmentRejected -> consumer stops retrying`.

Cap at 12 semantic nodes and never use Mermaid `mindmap` — a rooted tree cannot
show convergence or feedback. If the smallest faithful version needs more nodes,
drop the diagram and explain the structure in a short paragraph instead; do not
collapse distinct behavior or invent links to fit. The map explains, it does not
duplicate findings or assign severity.

## Review path

The Review path is for the human reviewer who wants to read the change
themselves. The change map says *what* the behavior is; the path says *where to
start reading, in which order, and what to check at each stop*, so the reviewer
follows the flow the way it runs instead of the order files appear in the diff.

Build it from the trace you already did; do not explore again just for it.

- **Start here.** Name the entry point where the changed behavior is triggered —
  HTTP route, message consumer, scheduled job, CLI command, UI event, or public
  function — as `path:line`, plus one sentence on why it is the right first
  read. When the change is mostly a contract (schema, migration, DTO, interface,
  config) that the flow depends on, start at the contract and say so.
- **Stops in execution order.** Follow the data from the entry point to its
  final side effect: validation, the changed decision, state mutation, outbound
  call or event, consumer. Each stop is one line with `path:line` and
  `CHANGED`/`NEW`/`REMOVED` where it helps, then a `Check:` line with the specific
  question the reviewer should answer there (for example "Does the status guard
  run before the write?"), not a generic "review the logic". Add `Tests:` with
  the test that proves this stop, or `none` when nothing does. Unchanged code
  belongs on the path only when the reviewer must read it to judge the change.
- **Findings on the path.** When a finding sits at a stop, end that stop with
  `→ Finding: <finding title>`. Do not restate the finding.
- **Separate flows.** When the change has independent flows, give each its own
  short path, highest-risk flow first. Cap each flow at 8 stops and the whole
  part at 3 flows; beyond that, list the remaining flows as entry points only.
- **Skim.** End with one line naming changed files that need only a glance
  (lockfiles, generated code, mechanical renames, formatting) and why.

Every `path:line` must exist on its identified side of the reviewed comparison. For a trivial change,
the part can be one line: `Start here: path:line — <why>; nothing else changes
behavior.` The Review path stays in the chat report; it is never posted to
GitHub.

```text
Flow: driver accepts a ride (highest risk)
Start here: src/rides/rides.controller.ts:52 — POST /rides/:id/accept, the only caller of the changed service method.
1. src/rides/rides.service.ts:88 CHANGED — rejects acceptance when the ride is no longer Searching
   Check: is the status read and the update in one transaction?
   Tests: rides.service.spec.ts:140 (stale status)
   → Finding: Two drivers can accept the same ride
2. src/rides/rides.repository.ts:31 NEW — conditional update on status
   Check: does a zero-row update surface as a conflict, not a success?
   Tests: none
3. src/rides/events/ride-accepted.publisher.ts:19 — publishes RideAccepted after commit
   Check: is the event skipped when step 2 rejects?
   Tests: rides.service.spec.ts:171
Skim: package-lock.json (patch bump), src/rides/dto/*.ts (field rename only)
```

## Classification and ordering

The `Type:` line is the finding's visible classification and requested action.
It is one of exactly these five strings, copied verbatim:

- `Issue - Blocking`: must be resolved before merging.
- `Issue - Non-blocking`: real defect with limited impact that need not block
  this merge.
- `Question - Non-blocking`: material uncertainty needing evidence.
- `Suggestion - Non-blocking`: improvement, not a demonstrated defect.
- `Nitpick - Non-blocking`: rare, documented convention or clarity issue.

That set is closed. The risk area a finding came from — reliability, testing,
migrations, security, performance, correctness, state machines — belongs in
`Issue:` and `Impact:` as concrete behavior. It is never a `Type:` value, never
a prefix or suffix on one, and never a heading that groups findings. Findings is
one flat ordered list in the shape below, whatever mix of risk areas or review
passes produced it.

Questions are non-blocking until evidence establishes a defect. Do not use a
blocking Question to express uncertainty.

Default to Issues, material Questions, and up to three design Suggestions from
the [design principles](design-principles.md) pass. Include other Suggestions,
more design Suggestions, or Nitpicks only when the user requests them or
applicable project instructions require them. For those categories, cite the
design principle, requested improvement goal, or documented convention,
explain its concrete relevance to this change, and give an actionable next step.
Do not invent a failure or inflate its impact to satisfy the defect gate. Generic
preferences remain out of scope.

Order findings by classification: blocking issues, non-blocking issues,
Questions, Suggestions, then Nitpicks. Within the same classification, put the
most consequential finding first. Do not add a separate priority or severity
prefix to the title.

## Write for the author

The evidence contract is strict, but the prose should sound like a thoughtful teammate,
not a generated audit. Keep the reader's likely question in view: what breaks, when does
it break, why does it matter, and what change would resolve it?

- Use natural, direct sentences and concrete identifiers. Remove every placeholder before
  sharing the review.
- Do not repeat the patch, the same finding in several formats, or an unchanged sentence
  merely to satisfy a template.
- Avoid canned praise, praise sandwiches, rhetorical questions, generic "consider"
  suggestions, and defensive language.
- Titles name the broken behavior or consequence. Do not phrase a proven defect as an
  imperative command such as "Handle errors correctly."
- Keep the explicit `Type:`, `Issue:`, `Impact:`, and `Fix:` fields in findings
  and GitHub comments. Treat the labels as useful metadata and write the content
  under each one in natural, direct language.
- Keep the six required report parts. Use additional formatting within them only
  when it helps scanning; write "None" when there are no Conflict notes.

## Finding shape

```text
Concrete failure or consequence: path/to/file.ts:42
Type: Issue - Blocking

Issue: <Concrete trigger and wrong behavior.>
Impact: <Observable consequence and who or what is affected.>
Fix: <Smallest useful correction or next action.>
```

Append `[LEFT]` to a title anchor for deleted/old-side content, using the old path
and `base-snapshot/`. `[RIGHT]` is optional and defaults to the new-side snapshot.
For example: `Required guard removed: src/old name.ts:42 [LEFT]`. The publication
plan must preserve that side and range. For renames, distinguish the old-side
source path from GitHub's diff-file path; establish the API anchor from the fresh
changed-file metadata instead of assuming the source path is accepted remotely.

Keep line ranges tight; inline findings must overlap the reviewed diff. A qualifying
chat-only finding may cite an exact outside-diff location when its scenario is
introduced or exposed by this change; do not invent an inline anchor. Name
identifiers and runtime values instead of abstract categories. Do not restate the entire patch,
quote long code blocks, or praise before the findings. One finding covers one
distinct issue. Keep each field concise and do not repeat the same sentence
across Issue, Impact, and Fix.

State in `Issue:` what *this* change introduced or newly made reachable. A
coupling that only bites after some hypothetical later edit is weak; the same
coupling is a real finding when the diff itself removed the other path — for
example, a fallback lookup that used to be one of two resolution routes and is
now the only one. `Fix:` may offer two acceptable routes joined by "and/or" when
both genuinely resolve the finding.

For a Question, use `Issue:` for what could not be verified, `Impact:` for why
the uncertainty matters, and `Fix:` for the exact evidence or answer that would
settle it. For a missing-test finding, name the production regression the test
must catch; coverage percentage alone is not the behavior.

## Report shape

These six parts, always, in this order. Never add a seventh.

```markdown
## Summary

<what the PR does and why, the intent source, and — as a sentence, not a table or
bullet list — what verification established: CI status with head SHA, anything run
locally, anything that could not be run. Contract checks that survived scrutiny
belong here too, so the author sees what was proven rather than only what failed.
One more sentence gives the challenge round: challenger, model if known, and counts
found by both / dropped / added, or why the round was skipped or failed. One sentence
names the references loaded and any matching reference skipped, with the reason. For
a PR with existing feedback, one short line per open or resolved-with-gap thread gives
its status (still valid, fixed, fix incomplete, outdated) and path:line; fixed and
outdated threads are counted, not listed.>

<then the change map, rendered for the current surface: ASCII in a terminal,
Mermaid in a GUI. See the Change map section above.>

## Review path

<entry point, ordered stops with Check and Tests lines, finding pointers, and a
Skim line, as described in the Review path section above>

## Findings

<ordered findings in the Finding shape above, printed as text, or “No findings.”>

## Conflict notes

<conflicts between guidance sources hit during the review: a cached rule that did
not match the pinned version, project instructions overriding this skill, two
sources disagreeing, or a material point where the challenger and the primary reviewer
still disagree after checking the evidence (one line, both views). Put stale-guidance
reports here as `Guidance:` lines using the guideline-maintenance reference. Write
"None" when there were none.>

## AC coverage

| Criterion | Status | Evidence or gap |
| --------- | ------ | --------------- |

<when the intent anchor has no criterion-level detail, say so in a sentence
instead of inventing rows>

## Verdict

<blocking findings yes | no | unknown, plus reviewed scope, exclusions, and
material residual risk folded into the same short paragraph>
```

Verification results, scope, and residual risk have no sections of their own —
they are sentences inside Summary and Verdict, and the change map sits inside
Summary. Do not add an "Open questions" section, a "What I verified" block, or a
pass/fail table. Questions are findings with `Type: Question - Non-blocking`.

No findings means no qualifying defect was found in the reviewed scope. It does
not mean the patch is approved or universally correct.

For blocking findings, use `yes` when at least one blocker is confirmed, even if
other coverage is incomplete. Use `unknown` when no blocker is confirmed but a
material evidence gap prevents a defensible assessment; name that gap. Use `no`
when the reviewed scope supports finding no blocker, with exclusions stated.
Partial coverage alone does not force `unknown`, and missing context alone does
not establish a blocking defect.

## Published line comment

The same shape, minus the location line — the comment's anchor already carries
it. Keep all four fields.

Write it so it stands on its own in the sidebar: backtick identifiers and keep
enough context for a reader who sees only this comment. Use a suggestion block
only for exact replacement code, and preserve indentation.
Publication selection, ordering, and verification live in the GitHub publishing reference.
