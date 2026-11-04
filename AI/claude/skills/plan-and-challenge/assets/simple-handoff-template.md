# Simple Handoff Template

Two files, saved side by side in the task folder. `implementation.md` joins them later and
belongs to `implement-plan`. Strict mode uses `review-template.md` instead; the fingerprint
fields and separate `review.md` do not appear here.

Keep the field names literal. `implement-plan` reads `Workflow`, `Status`, `Revision` and
the newest Review entry to decide whether this handoff is approved, so a renamed or missing
field reads as "not approved" and sends the plan back here.

---

## task.md

```markdown
# <task title>

- Source: <Jira key/URL, file path, or "user message in this conversation">
- Source last updated: <timestamp or unavailable>
- Captured at: <timestamp>

## Normative requirements

<The exact wording of the request or ticket, quoted. Preserve modality and qualifiers:
"return" is not "throw", "exactly three" is not "up to three". This is the text every
later agent treats as authoritative — do not paraphrase or tidy it.>

## Acceptance criteria

- <observable condition, one per line>

## Inferred, not stated

- <anything you concluded rather than read, kept separate so a reviewer can see the seam>

## Open questions

- <ambiguity that needs the task owner's decision before it becomes a requirement>
```

## plan.md

```markdown
# <plan title>

- Workflow: simple
- Revision: 1
- Status: Draft
- Planning method: <Superpowers | agent Plan mode>
- Challenge venue: <fresh subagent | another agent's CLI, named>
- Task snapshot: <absolute path to task.md>
- Specification: <absolute path, or none>
- Execution route: <internal sequential delegation with controller fallback, or the
  user's explicitly named route>

## Design and scope

<What changes and why. Name what is deliberately out of scope — an implementer with only
this document cannot tell an omission from an exclusion.>

## Tasks

### T1 — <name>

- Behavior: <what is true after this task that was not true before>
- Files owned: <explicit paths or a bounded directory>
- Depends on: <task IDs and the exact interface names/signatures, or none>
- Verify: <focused command, or a concrete reason no check applies>

### T2 — <name>

<Same shape. One task is enough for small work; do not split to look thorough.>

## Review

### Revision 1 — <date>

- Reviewer: <actual agent/session identity, or "self-review" labelled as such>
- Reviewed revision: 1
- Verdict: <CLEAR | CHANGES_NEEDED>
- Findings: <each finding, its evidence, and how it was resolved or why it was rejected>
- Accepted non-blocking items: <what is knowingly left open, and why>
- User approval: <quote or message reference, when approval rests on it>

<Append a new entry per reviewed revision; never edit an earlier one. The verdict names
the revision it actually reviewed, which is why material changes increment Revision
and return Status to Draft.>
```

---

## Moving from Draft to Approved

Set `Status: Approved` only when the newest Review entry covers the current revision and
records either an independent `CLEAR` or the user's explicit approval after a labelled
self-review. Then hand `implement-plan` the absolute plan path.

A simple approval is a recorded decision by real reviewers, not a tamper-proof gate: it
depends on these entries being honest. That is the trade the user accepted when choosing
simple over strict, and it is the reason never to write a verdict an agent did not return.
