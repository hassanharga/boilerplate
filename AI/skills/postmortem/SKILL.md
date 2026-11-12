---
name: postmortem
description: >-
  Use when writing, revising, or publishing a blameless post-incident review or
  RCA after an outage, degradation, data issue, failed deployment, security
  incident, or meaningful near miss. Includes evidence synthesis, impact and
  timeline reconstruction, causal analysis, response lessons, and trackable
  follow-up actions. Do not use for live incident response or unrelated project
  retrospectives.
---

# Postmortem

Turn a resolved incident into a clear, evidence-led account that helps a future reader
understand what happened and reduces the chance or impact of recurrence.

## Operating contract

- Use this skill after customer impact has ended or the incident has entered a stable
  post-incident phase. Use `incident` while response and mitigation are still active.
- Read applicable organization, repository, severity, postmortem, privacy, and retention
  policy before selecting headings, deadlines, audiences, or required fields.
- For a Yassir Mobility incident, read `../incident/references/yassir-policy.md`
  directly. Do not wait to be called from the `incident` workflow — a postmortem written
  two days later is usually invoked on its own, and without that file the seven required
  sections, the same-day/48-hour deadline, and the `Postmortem` component silently
  disappear. Keep the generic craft here so copied policy cannot drift.
- That path assumes the `incident` skill is installed alongside this one. If it is not
  there, say so before drafting: for a Yassir incident the output is missing its required
  sections, deadline, stakeholder list, and Jira action-item rules, and the correct fix is
  to install `incident` rather than to reconstruct the policy from memory. Everything in
  this skill still applies to a non-Yassir incident with no policy file at all.
- Treat every source as evidence, not truth by default. Never invent a timestamp, metric,
  cause, owner, due date, ticket, severity, decision, quotation, or citation.
- Keep the work blameless without erasing accountability. Describe decisions, available
  information, system conditions, and missing guardrails. Do not frame a person as the
  root cause.
- Drafting and analysis are read-only. Creating a file, publishing a page, creating Jira
  actions, sending messages, or changing incident records are separate mutations and
  require authorization for that exact action.

## Output and authorization

Default to a complete draft in chat. Create a Markdown file only when the user asks for a
file or clearly requests a durable local artifact; use their destination when supplied and
otherwise propose a safe path outside application source. Do not leave an unsolicited
postmortem file in a repository.

Publish only when explicitly asked. A request to publish the postmortem does not authorize
creating follow-up tickets or sending announcements. Read
[publishing.md](references/publishing.md) immediately before any publication attempt.

## Reference routing

- Read [evidence-and-analysis.md](references/evidence-and-analysis.md) for every postmortem.
- Read [template.md](assets/template.md) when preparing the document.
- Read [publishing.md](references/publishing.md) only when publication is requested.

## Workflow

### 1. Establish the incident and policy

A near miss inverts two sections and leaves the rest intact. Impact becomes *what would
have happened and what stopped it* — the control that held, whether it held by design or
by luck, and how close it came. The timeline centres on detection rather than recovery.
Everything else — evidence states, causal model, action quality — is unchanged. Do not
manufacture customer impact to make it look like a real incident, and do not downgrade
the analysis because nobody was hurt; a near miss is the cheapest evidence you will get.

Confirm the incident is stable enough for post-incident analysis. Identify the incident
record, organization, severity vocabulary, required sections, completion deadline,
audience, confidentiality level, and requested output destination. Do not translate one
organization's severity label into another without an explicit mapping.

For a Yassir Mobility incident, use the `incident` skill's current seven-section,
deadline, stakeholder, and Jira action-item requirements. If that policy source is not
available — the skill is not installed, or the file cannot be read — name the missing
policy and what the draft therefore cannot guarantee, rather than reconstructing it from
memory.

### 2. Build the evidence map

Gather the supplied or authorized incident record, timeline, logs, alerts, dashboards,
communications, deployment and configuration history, relevant code or pull requests,
tickets, and recovery verification. Use neutral terms such as commit or deployment
history, not `git blame`.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final document, and every external
write stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means one pass per evidence stream: chronology, impact, change history,
response evidence, or candidate actions. Each carries the same source, timestamp,
confidentiality, and evidence-status rules, and returns sourced facts, conflicts, and
hypotheses — never final causes. Causal analysis, the action set, document state, and
every file, ticket, message, or publication stay with the main agent. A small postmortem
stays in the main agent entirely.

Separate confirmed facts, estimates, supported inferences, unknowns, and conflicts before
writing. Preserve useful source links. Use absolute timestamps with a timezone and
distinguish impact start, detection, declaration, mitigation, recovery, and resolution.

### 3. Close only material gaps

Read available evidence before interviewing people. Ask a small group of focused questions
that could change impact, chronology, causes, recovery confidence, or action items. Do not
block a useful draft on facts nobody currently knows. Mark the gap and name the evidence
or owner needed to close it.

### 4. Explain causality without forcing a story

Distinguish the initiating trigger from technical and process causes, contributing
conditions, and detection or response gaps. Use Five Whys, a causal graph, or another
method only when it fits the evidence. Do not force multiple causes into one linear chain.

A cause is useful when changing it would prevent a similar failure or reduce its impact.
"Human error" and "be more careful" do not meet that test. If causality is still under
investigation, say so and avoid presenting correlation as a confirmed cause.

Do not turn unavailable telemetry, missing documentation, or another evidence-collection
limitation into an incident cause unless evidence shows that it contributed to impact,
detection, or response. Keep a limitation in the evidence-gaps section when that is all it
proves.

### 5. Produce accountable actions

Tie every action to a demonstrated cause, contributing condition, or response gap. State
the system outcome and an observable acceptance check. Prefer prevention, detection, and
mitigation guardrails over reminders or training alone.

Do not invent one action for each prevent/detect/mitigate category. Propose only actions
supported by the causal or response evidence. Label an idea based on an unconfirmed gap as
a candidate for owner validation rather than an accepted action item.

State the required reliability or security property without guessing an implementation,
protocol rule, threshold, or vendor behavior that the evidence does not establish. Leave
the implementation choice to the accountable owner unless an approved design is already
part of the incident record.

Use the owner, due date, priority, ticket, and component required by active policy. Never
invent them. `Owner pending` or `Tracking ticket pending` is acceptable in a Draft, but a
postmortem cannot be marked Final while required accountability fields are unresolved.

Creating those tickets requires separate authorization. Once the user approves it, hand
the actions to the applicable ticket workflow rather than filing them directly — for
Yassir Core Mobility that is `core-mobility-jira-ticket`, which owns the component,
squad, and classification rules and can hold them in a local tracker until you are ready
to file. Where no such workflow applies, create them with the project's own conventions
and report exactly what was created.

### 6. Draft for a human reader

Use [template.md](assets/template.md) as a content contract, then adapt it to active policy
and the evidence. Write natural, direct prose for someone who was not present. Expand an
internal acronym on first use, keep technical detail only where it explains impact or
causality, and remove all raw placeholders and template instructions.

Avoid canned conclusions, repeated summaries, generic "lessons learned," forced lists of
three, and inflated language. Keep required headings even when the evidence is missing,
with a concise `Unknown` or `Needs follow-up` statement. Omit optional sections that have
no useful content.

### 7. Review the state honestly

Before calling the document complete, check that:

- impact and duration are supported and estimates are labeled;
- the timeline is ordered, timezone-qualified, and explicit about corrections or gaps;
- causes are supported by evidence and separated from hypotheses;
- response observations are specific and blameless;
- actions cover prevention, detection, and mitigation where applicable;
- required actions have owners and tracking according to policy;
- sensitive information is appropriate for the intended audience;
- no placeholder, invented fact, or unsupported certainty remains.

Use `Draft` when evidence, review, or ownership remains open; `In review` when the document
is complete enough for stakeholder validation; and `Final` only after required review and
accountability gates pass. Report any remaining gaps plainly.
