# Postmortem template

Use this as a content contract, not text to copy mechanically. Adapt it to the active
organization policy and remove all angle-bracket prompts before sharing the document.
Keep required headings when facts are unknown; mark the exact gap and follow-up needed.
Omit optional sections that add no information.

# Postmortem: <short incident title>

| Field | Value |
| --- | --- |
| Incident date | <YYYY-MM-DD> |
| Status | <Draft, In review, or Final> |
| Severity | <organization's incident label and source> |
| Impact window | <start to recovered, duration, timezone> |
| Authors | <names or Owner pending> |
| Incident record | <link or identifier when available> |

## Summary

In two to four natural sentences, state what failed, who or what was affected, how long
impact lasted, how service recovered, and the confirmed cause or current causal status.
Do not claim a root cause if it remains under investigation.

## Impact

Describe customer, business, operational, data, safety, privacy, and service-level impact
that is relevant to this incident. Label estimates and bound the blast radius. State a
confirmed absence, such as no data loss, only when the evidence supports it.

For several dimensions, a small table may help. For a simple incident, use a short
paragraph or bullets instead of an empty or mostly blank table.

## Timeline

State the timezone once and use absolute timestamps. Include the incident milestones that
the evidence supports: impact start, detection, declaration, investigation decisions,
mitigation, recovery, resolution, and important communications. Do not manufacture events
to fill a standard sequence.

| Time | Event and evidence |
| --- | --- |
| <absolute time> | <confirmed event, decision, or correction; link when useful> |

## Technical and process causes

Explain the causal model in direct prose. Distinguish:

- the trigger;
- confirmed technical and process causes;
- contributing conditions;
- detection, coordination, or response gaps;
- hypotheses or unresolved causal questions.

Do not repeat the timeline or reduce the cause to a person's action.

## Resolution and recovery

Explain what reduced impact, what restored service, how recovery was verified, and which
parts are temporary mitigation versus durable correction. Note relevant backlog,
downstream, or data-integrity checks.

## What went well

Record specific systems, decisions, or coordination that limited impact or shortened
recovery. Omit generic praise.

## What did not go well

Record specific system, process, detection, or response gaps. Describe the conditions and
consequence without blaming an individual.

## Action items

Each action needs a concrete deliverable, the system outcome it establishes, and an
acceptance check. Add owner, due date, tracking ticket, priority, component, and
prevent/detect/mitigate classification when active policy requires them. Never invent a
missing field. Do not manufacture actions to cover every classification. Keep an
evidence-based idea as a proposed candidate until the relevant owner validates it.
Describe the required outcome rather than guessing an unverified implementation detail.

For a small list, use readable checklist items:

- [ ] <action>. Outcome: <security or reliability property>. Verification: <observable
  check>. Owner: <name or pending>. Tracking: <ticket or pending>.

Use a table when several actions need comparison. A Draft may contain pending ownership;
a Final document may not omit required accountability.

## Open evidence gaps

Include this section only when material facts, causal questions, review decisions, or
required action ownership remain unresolved. For each gap, name the evidence or owner
needed to close it.
