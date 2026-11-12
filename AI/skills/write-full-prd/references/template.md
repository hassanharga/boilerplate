# PRD templates by mode

Match an existing repository template when one exists. Use these structures only
for a new document or when the user approved a format change.

## Shared metadata

Include only fields that the team can maintain:

~~~markdown
# <Document type>: <Product, initiative, or feature>

| Field | Value |
| --- | --- |
| Status | Discovery draft / Draft / In review / Approved |
| Owner | <Name, role, or TBD> |
| Decision owners | <Relevant owners or TBD> |
| Release or deadline | <Known value or Open> |
| Last updated | <YYYY-MM-DD> |
| Source of truth | <This document or linked source> |
| Related material | <Research, tickets, design guide, RFC, policy> |
~~~

Do not invent an author, reviewer, deadline, approval, or version.

## Discovery draft

Use when the idea is thin, research is absent, or the user asks to skip
clarification. Keep it short and label it not build-ready.

~~~markdown
## Problem hypothesis

<Who may have the problem, in which context, and the suspected current cost.>

Evidence status: <Observed / Assumption / Open>

## Proposed outcome

<What would improve if the hypothesis is true.>

## Smallest useful release hypothesis

<The narrow journey or capability worth validating.>

## Assumptions and risks

| Item | Status | What changes if wrong | Owner |
| --- | --- | --- | --- |

## Evidence and decisions needed

| Question or evidence gap | Why it matters | Owner | Blocks implementation? |
| --- | --- | --- | --- |

## Next validation

<Research, prototype, instrumentation, policy review, or technical discovery.>
~~~

Do not add invented personas, schemas, numeric targets, or complete functional
requirements merely to make the document look finished.

## Lean feature spec

Use for a bounded change owned by one team or release.

~~~markdown
## Context and evidence

<Current behavior, affected actor, problem, evidence, and related approved docs.>

## Outcome and release boundary

### In scope

- <Behavior required for this release>

### Out of scope or deferred

- <Adjacent behavior and why it is excluded>

## Journey

1. <Trigger and precondition>
2. <Actor action and system response>
3. <Safe completion or recovery>

## Requirements

### REQ-001: <Stable title>

Status: <Confirmed / Proposed / Assumption / Open>
Source: <Evidence or decision owner>

<Actor, observable behavior, policy, permissions, limits, and failure behavior.>

Acceptance criteria:

- <Observable pass or fail outcome>
- <Behavioral example in Given/When/Then only if branching makes it clearer>

## Applicable cross-functional behavior

<Only the security, privacy, accessibility, localization, reliability,
analytics, support, migration, or rollout decisions that apply.>

## Dependencies and rollout

| Dependency or step | Owner | Required before | Failure or containment |
| --- | --- | --- | --- |

## Success and guardrails

| Measure or evidence | Current state | Decision threshold | Method | Owner |
| --- | --- | --- | --- | --- |

## Open decisions

| ID | Decision | Recommendation | Owner | Blocks release? |
| --- | --- | --- | --- | --- |
~~~

Omit success metrics when the change is mandatory and success is better expressed
as verified conformance, data integrity, or safe rollout evidence.

## Full PRD

Use for a new product, substantial initiative, multi-team release, or broad
product change. Include each applicable section. Explain a surprising omission.

~~~markdown
## 1. Decision summary

<What decision this PRD asks the organization to make, why now, and current
readiness.>

## 2. Problem and evidence

<Affected actors, context, current workaround or behavior, cost or risk, and
links to evidence. Separate observed facts from hypotheses.>

## 3. Actors, jobs, and access

| Actor or role | Context and job | Needs | Access or policy boundary | Evidence |
| --- | --- | --- | --- | --- |

Add a persona only when research supports it. Do not invent a name or quote.

## 4. Outcomes and decision measures

| Outcome or guardrail | Baseline | Target or threshold | Timeframe | Method | Owner |
| --- | --- | --- | --- | --- | --- |

Use Unknown with a measurement plan when a baseline or target does not exist.

## 5. Release boundary

### In scope

| Capability | Why this release needs it | Evidence status |
| --- | --- | --- |

### Out of scope or deferred

| Capability | Reason | Trigger to revisit |
| --- | --- | --- |

Use MVP, v2, and later only when the team uses those terms.

## 6. Journeys and policy decisions

### <Journey>

Actor:
Trigger:
Preconditions:
Safe completion:

1. <Action and observable response>
2. <Decision branch>
3. <Failure and recovery>

Policy decisions:

| Decision | Rule | Source or owner | Status |
| --- | --- | --- | --- |

## 7. Product requirements

### REQ-001: <Stable title>

Status: <Confirmed / Proposed / Assumption / Open>
Source: <Evidence or decision owner>
Actors: <Applicable actors>

Requirement:

<Observable product behavior, relevant policy, permissions, limits, and failure
behavior.>

Acceptance criteria:

- <Observable pass or fail outcome>
- <Additional example only when needed>

Related: <Journey, measure, design brief, RFC, ticket>

## 8. Cross-functional product behavior

Include applicable decisions from references/cross-functional.md. State product
outcomes and constraints rather than designing the implementation.

## 9. Data and information policy

Use only when the product reads, creates, transforms, shares, or retains important
data.

| Information | Purpose | Source | Access | Retention or deletion | Audit need |
| --- | --- | --- | --- | --- | --- |

Describe product information needs. Put database fields, indexes, and storage
design in the RFC.

## 10. Dependencies, risks, and rollout

### Dependencies

| Dependency | Owner | Needed by | Status | Impact |
| --- | --- | --- | --- | --- |

### Risks

| Risk | Evidence | Impact | Mitigation or decision | Owner |
| --- | --- | --- | --- | --- |

### Rollout, migration, and containment

<Audience, phases, compatibility, historical data, support readiness, monitoring,
rollback where allowed, containment where rollback is not allowed, and
escalation.>

## 11. Assumptions and open decisions

### Assumptions

| ID | Assumption | What changes if wrong | Owner | Validation |
| --- | --- | --- | --- | --- |

### Open decisions

| ID | Decision | Recommendation | Owner | Due | Blocks release? |
| --- | --- | --- | --- | --- | --- |

## 12. Traceability

Use for large, regulated, or multi-team work.

| Requirement | Evidence | Journey | Acceptance evidence | Owner | Delivery link |
| --- | --- | --- | --- | --- | --- |
~~~

## Requirements-only

Use when the user asks only for user stories, requirements, or acceptance
criteria. Return exactly that requested set with enough context to prevent
ambiguity. Do not wrap it in a full PRD.

User stories are optional. When useful, write:

> As <actor>, I need <capability> so that <outcome>.

The outcome must explain the need rather than repeat the capability. Another
format is allowed when it communicates actor, action, and purpose more clearly.

## Review or refresh

For a review, report:

- finding and evidence;
- affected requirement or section;
- product or delivery impact;
- recommended correction;
- whether it blocks review, build, or release.

For a refresh:

- preserve accepted structure and stable IDs;
- update the relevant sections only;
- distinguish inherited and new decisions;
- record superseded decisions without erasing useful history;
- reconcile the summary, scope, requirements, measures, and open decisions.

## Requirement writing checks

A requirement is ready when:

- its actor or boundary is clear;
- its result is observable;
- permissions, policy, limits, and failure behavior are explicit where relevant;
- acceptance criteria can produce a clear pass or fail;
- it does not prescribe unapproved architecture or UI;
- assumptions and open decisions are visible;
- its ID remains stable across document edits.

Avoid vague phrases such as seamless, intuitive, robust, scalable, real time,
supports, handles gracefully, and industry standard unless the document defines
the observable meaning.
