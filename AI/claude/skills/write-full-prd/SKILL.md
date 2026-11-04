---
name: write-full-prd
description: >-
  Use when drafting, reviewing, or updating a product requirements document,
  product spec, feature requirements, release scope, user stories, or acceptance
  criteria before design and implementation. Do not use for technical
  architecture or RFCs, UI design briefs, implementation plans, or individual
  Jira tickets.
---

# Write a product requirements document

Create a decision record that explains the problem, intended outcome, release
boundary, and observable product behavior. Make missing evidence visible. Do not
turn a small feature request into an initiative-sized document.

## Choose the mode, then state the readiness

Mode and readiness are independent. Mode is which artifact to produce; readiness is how
much the evidence supports. Every output carries both.

**Mode — which artifact:**

| Request | Mode | Default output |
| --- | --- | --- |
| Bounded change for one team or release | Lean feature spec | Focused requirements and acceptance criteria |
| New product, initiative, or multi-team change | Full PRD | Complete product and release contract |
| Existing PRD needs correction or expansion | Review or refresh | Findings or a focused update |
| User stories or acceptance criteria only | Requirements-only | Requested requirement set |
| Thin idea with no established output shape | Hypothesis brief | Hypothesis, assumptions, risks, and decisions needed |

If the user asks for a full PRD, use full mode regardless of how thin the evidence is —
then say so in the readiness.

**Readiness — how far the evidence goes:**

| Readiness | Meaning |
| --- | --- |
| Discovery draft | Key claims are assumptions or proposals. Not build-ready. Blocking decisions are named. |
| Review-ready | Evidence is sufficient for stakeholders to validate and decide. |
| Build-ready | Requirements, acceptance criteria, and accountability are resolved. |

Any mode can be a discovery draft. A requirements-only set, a lean spec, and a full PRD
can each be one. Never raise readiness to compensate for a request; if the evidence is
thin, the document says so.

## Rules

1. Read repository instructions and existing sources before asking questions.
2. Preserve the approved template, terminology, requirement IDs, and source of
   truth.
3. Distinguish confirmed facts, observations, proposals, assumptions, and open
   decisions.
4. Never invent research, personas, quotes, baselines, targets, legal
   interpretations, approvals, or constraints.
5. Scale the document to the request and agreed release.
6. Do not create, overwrite, or publish an artifact without authorization.

## Product boundary

| Material | Treatment |
| --- | --- |
| User need, product behavior, policy, permission, outcome | Specify in the PRD |
| UI layout, tokens, component behavior | Link to a design brief — use `ui-ux-brief` |
| Architecture, API, schema, infrastructure algorithm | Link to a design doc — use `write-rfc` |
| Delivery tasks and sequencing | Out of scope; the RFC's rollout section normally covers it |
| Individual work items | See work-item breakdown below |

Record technical constraints only when they change product behavior. Do not
design the solution in the PRD.

## Workflow

### 1. Establish authority

Locate the existing PRD, research, strategy, tickets, policy, analytics, design
guides, RFCs, shipped behavior, and repository conventions.

Use this precedence:

1. explicit user direction and approved requirements;
2. current approved product, legal, security, and policy sources;
3. existing PRDs and accepted decisions;
4. observed product and repository behavior;
5. current primary research and standards;
6. agent recommendation.

Report conflicts. Do not treat an old ticket, a draft, or current implementation
as approved intent without evidence.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final document, and every external
write stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means one pass per evidence or cross-functional domain: research and
analytics, policy and privacy, shipped behavior, operations, accessibility, or rollout.
Each returns sources, evidence status, conflicts, and open decisions as advisory input.
Source precedence, the release boundary, requirement wording and stable IDs, user
questions, and readiness stay with the main agent. Never omit a domain or raise
readiness because an independent pass was unavailable. Lean and requirements-only work
usually stays in the main agent.

### 2. Clarify material gaps

Read references/interviewing.md when evidence is thin or contradictory. Ask one
bounded question batch after reading available sources. Ask a targeted follow-up
only when an answer changes the problem, release boundary, safety, or legal
interpretation.

Clarification fills gaps politely; it does not test whether the plan survives contact
with reality. When the user wants a draft stress-tested rather than completed — or when
the requirements look agreed but under-examined — use `grill-me` for an adversarial pass
and fold its resolved decisions and parked unknowns back into this document.

If the user says to skip discovery, produce a discovery draft with visible
assumptions. For regulated or safety-sensitive work, request the jurisdiction,
current authoritative source, effective date, and accountable interpretation
owner. Do not claim compliance.

### 3. Set the release boundary

Anchor scope on the smallest valuable or mandatory outcome. Use the team's
language: in scope and deferred, deadline release, experiment, migration phases,
or MVP and later.

Do not force MVP language or experimental kill criteria onto mandatory,
operational, migration, or regulatory work.

### 4. Describe actors from evidence

Use roles, jobs, context, access, and decision authority. Named personas are
optional and require research. Never invent names, demographics, quotes, buyers,
or behavioral conflict.

### 5. Write the selected document

Read references/template.md and use the matching mode.

For each consequential requirement:

- preserve an existing stable ID, or use REQ-001, REQ-002, and so on;
- identify the actor or boundary;
- state observable behavior, policy, permissions, limits, and failure behavior;
- add acceptance criteria with a clear pass or fail;
- label its evidence status and unresolved decisions.

Never renumber an accepted ID because sections moved. Use Given/When/Then only
when state or branching makes the example clearer. Keep unapproved architecture
and UI decisions out of product requirements.

### 6. Cover applicable cross-functional behavior

Read references/cross-functional.md. Include only areas that change the product
or release: security, privacy, accessibility, localization, reliability,
analytics, support, migration, rollout, dependencies, or AI and automation.

Testing and coverage policy must come from repository instructions, acceptance
criteria, or approved policy. Preserve 100% unit coverage where required. Do not
introduce a numeric threshold in repositories that do not use one.

Use evidence-backed outcomes and guardrails. When a baseline or target is
unknown, record the measurement plan instead of inventing a number.

### 7. Check and deliver

Verify:

- document size and scope match the request;
- accepted sources, structure, terminology, and IDs were preserved;
- every claim has the correct evidence status;
- in-scope journeys map to observable requirements and acceptance criteria;
- failure, permissions, data, accessibility, operations, migration, and rollout
  are covered where relevant;
- no unapproved architecture, UI, metrics, research, or compliance claim appears;
- assumptions and open decisions name an owner and blocking status;
- the document has no internal contradiction.

State whether it is a discovery draft, review-ready, or build-ready.

Read references/publishing.md only when a file or shared destination is in scope.
External publication requires explicit authorization. Handoff with the artifact
location or proposed patch, the decisions worth reviewing, and blocking open
items. Do not restate the document.

## Work-item breakdown

Breaking a PRD into work items is a separate, explicitly requested action. Never create
tickets as a side effect of writing or publishing the PRD.

When the user does ask for the breakdown, ask where the items should live unless they
have already said:

- **Jira** — hand off to the applicable Jira workflow, which owns the project's field
  rules, components, and classification. For Yassir Core Mobility that is
  `core-mobility-jira-ticket`.
- **Local markdown tracker** — useful when the release shape is still moving and filing
  thirty tickets would be premature.

For the local tracker:

- One file per item at `tickets/<ID>-<slug>.md`, carrying the same field set,
  description, and acceptance criteria the Jira path would produce.
- `tickets/INDEX.md` as the tracker: a table of ID, title, component or area, status, and
  file link. Status changes update the index.
- Each item records the `REQ-` ID it derives from. That feeds the traceability section of
  the full PRD directly, and it is the reason to prefer this over an ad-hoc list.
- **Local IDs never imitate a real tracker key.** Use `T-001`, not a plausible-looking
  `CMB-1234`. A fake key that later collides with a real one is genuinely hard to
  untangle, and a distinct prefix stays greppable.
- When an item is promoted to Jira, write the real issue key back into the local file and
  mark it promoted, so the same work never exists in two places without a link.

## References

- references/interviewing.md: evidence-aware clarification
- references/template.md: mode-specific templates and requirement checks
- references/cross-functional.md: product quality, rollout, and AI coverage
- references/publishing.md: portable artifact and publication safety
