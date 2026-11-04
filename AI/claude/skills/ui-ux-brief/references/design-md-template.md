# Modular design brief template

Use the smallest set of sections that answers the request. Preserve an existing
guide's structure during refresh work. This template is the default only for a
new artifact.

## Quick decision

Do not create a file. Use:

1. Recommendation
2. Evidence or inherited rule
3. Tradeoff
4. Missing decision, if any

## Feature brief

Use these sections when relevant:

~~~markdown
# <Feature or screen> design brief

Status: <proposed, approved, or mixed>
Scope: <included surfaces and journeys>
Sources: <approved guide, requirements, research, code>
Last checked: <date>

## Context and decision

<Actor, conditions, outcome, costly mistake, fixed constraints.>

## Existing patterns

| Area | Source | Adopted behavior | Exception |
| --- | --- | --- | --- |

## Flow and layout

<Steps, decision points, recovery, hierarchy, and primary action.>

## Components and states

| Component | Reuse or change | Variants and states | Interaction |
| --- | --- | --- | --- |

For a component being built or changed, add its prop contract using the shape in
section 7 of the full brief.

## Responsive and input behavior

<What reflows, what remains visible, touch and pointer differences.>

## Content and localization

<Approved terms, draft copy, content expansion, RTL behavior.>

## Accessibility specification

<Target and the concrete focus, keyboard, announcement, motion, and contrast
requirements.>

## Implementation checks

| Check | Required result | Status |
| --- | --- | --- |

## Assumptions and open decisions

| Item | Status | Impact | Owner |
| --- | --- | --- | --- |
~~~

## Full brief

The full brief may use the structure below. Omit a section that is genuinely not
applicable and explain any omission that could surprise an implementer.

~~~markdown
# <Product> design brief

Status: <proposed, approved, or mixed>
Scope: <release, platforms, and exclusions>
Authority: <guide owner or decision owner>
Sources: <approved inputs with links or paths>
Last checked: <date>
Accessibility target: <design baseline, not a compliance claim>

## 1. Product context

<Who, conditions, critical job, costly mistake, business evidence, and hard
constraints. Mark assumptions.>

## 2. Design decisions

| Decision | Evidence | Tradeoff | Status |
| --- | --- | --- | --- |

Include only principles that settle recurring arguments.

## 3. Existing system and divergences

| Area | Authority | Adopted pattern | Proposed divergence | Cost |
| --- | --- | --- | --- | --- |

## 4. Journeys and information architecture

### <Journey>

Actor:
Trigger:
Safe completion:
Frequency:

1. <Action and system response>
2. <Decision and branch>
3. <Recovery when it fails>

## 5. Screen inventory

| Screen | Purpose | Entry | Primary action | Safe completion |
| --- | --- | --- | --- | --- |

## 6. Screen specifications

### <Screen>

Job:
Primary action:
Hierarchy:
Regions:
Components:
Failure and recovery:
Draft content:

Add a compact diagram only when it clarifies hierarchy.

## 7. Components

Document components used by the scoped screens.

| Component | Source | Variants | States | Input behavior | Accessibility |
| --- | --- | --- | --- | --- | --- |

### Contract: <new or changed component>

Only for a component being built or changed. A reused component's contract already
exists — link it instead.

| Prop | Type | Required | Default | Meaning |
| --- | --- | --- | --- | --- |

Events: <name, when it fires, what it carries>
Slots or children: <what the consumer supplies, and what the component owns>
Controlled or uncontrolled: <who owns the state, and what happens if both do>
Forbidden: <what a consumer must not be able to express — a variant that cannot
be disabled, a state with no recovery, a required label that can be omitted>

The last row is the point of the contract. Variants and states describe what the
component looks like; the contract decides what a consumer is *able* to build, and
an invalid combination that the props permit will eventually ship.

## 8. State behavior

| Surface | State | Trigger | Visible result | Announcement | Recovery |
| --- | --- | --- | --- | --- | --- |

Consider first use, no results, initial load, partial refresh, recoverable error,
blocking error, success, stale data, offline, permission denied, and session
expiry only where they apply.

## 9. Visual system and tokens

### Adopted tokens

| Area | Source | Decision | Exception |
| --- | --- | --- | --- |

### Proposed tokens

| Token | Value | Usage | Evidence | Status |
| --- | --- | --- | --- | --- |

Include implementation output in the project's maintained source format.

## 10. Responsive and input behavior

| Content pressure or breakpoint | Layout change | Priority retained | Input differences |
| --- | --- | --- | --- |

Describe per-screen reflow, text scaling, touch targets, hover alternatives, and
keyboard behavior.

## 11. Content and localization

<Voice, approved terms, draft strings, content expansion, locale formatting,
bidirectional layout, icon mirroring, and mixed-direction data.>

## 12. Accessibility specification

Target:
Current source and date checked:

### Contrast

| Pair | Foreground | Background | Ratio | Requirement |
| --- | --- | --- | --- | --- |

### Semantics, keyboard, focus, and announcements

<Requirements for the actual screens and widgets.>

### Motion, zoom, reflow, and alternate input

<Required behavior.>

## 13. Implementation checks

| Check | Method | Required result | Status | Evidence |
| --- | --- | --- | --- | --- |

Use required for work that has not run. Do not prefill passed.

## 14. Assumptions, decisions, and open questions

| Item | Status | Impact | Owner or source |
| --- | --- | --- | --- |
~~~

## Writing rules

- Use approved product language. Mark new interface text as draft.
- Explain a consequential choice once. Cross-reference it later.
- Use tables for comparison, not for ordinary prose.
- Keep diagrams coarse and functional.
- Do not claim a source, approval, test result, or compliance status that is not
  supported by evidence.
- Avoid promotional language and generic mood adjectives.
- Make inherited decisions visibly different from proposed ones.
