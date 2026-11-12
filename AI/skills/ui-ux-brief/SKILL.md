---
name: ui-ux-brief
description: >-
  Use when creating or updating an implementation-ready UI/UX brief or DESIGN.md
  for a product, feature, or screen; reconciling UI work with an existing design
  system; or defining flows, states, tokens, responsive behavior, content, and
  accessibility before frontend implementation. Scale the output to the request
  and preserve established product patterns by default. Do not use for direct UI
  implementation, user research, visual regression review, or an isolated design
  opinion unless the user asks to capture it in the brief.
---

# UI/UX brief

Produce a design contract that a designer can challenge and an engineer can
implement. Ground it in the product, the people using it, and the system that
already exists. Do not turn a small question into a full design-system exercise.

## Operating rules

1. Preserve approved patterns by default. Existing design guides, tokens,
   components, platform conventions, and shipped behavior outrank personal taste.
2. Scale the work. A quick decision belongs in chat. A screen change needs a
   focused brief. A new product may need the full document.
3. Separate evidence from judgment. Label assumptions and proposals. Never invent
   research, metrics, approved terminology, legal copy, or compliance.
4. Make decisions testable. Describe behavior, states, responsive changes,
   localization, accessibility, and the checks that remain after implementation.
5. Write plainly. Prefer concrete rules and examples over design jargon or
   adjectives such as modern, premium, delightful, clean, or intuitive.

## Choose the output mode

Read references/evidence-and-modes.md before choosing.

| Request | Mode | Default output |
| --- | --- | --- |
| One design choice or opinion | Quick decision | Short answer in chat |
| One screen, component family, or bounded feature | Feature brief | Focused sections in chat or a named file |
| New product or broad redesign | Full brief | DESIGN.md or the user-specified destination |
| Existing product with a design contract | Refresh | Proposed patch to the existing source |
| Consistency, readiness, or design-system review | Audit | Findings and recommendations, without rewriting |

Do not create or overwrite a file merely because this skill triggered. Write only
when the user asked for an artifact or approved a proposed update. If a design
guide already exists, update it in place only with authorization. Otherwise
present the proposed change first.

## Workflow

### 1. Discover what is authoritative

Read the available inputs before asking questions:

- repository and agent instructions;
- the current design guide, brand rules, tokens, components, and routes;
- approved product requirements, tickets, research, content, analytics, and
  accessibility requirements;
- supplied screenshots, prototypes, Figma files, or live product references;
- platform and framework constraints.

Use this precedence when sources conflict:

1. explicit user direction and approved product requirements;
2. approved design guide, brand system, and accessibility policy;
3. shipped behavior, current tokens, and reusable components;
4. verified platform and regulatory requirements;
5. current category research;
6. agent judgment.

Record conflicts instead of silently choosing. For an existing product, use
scan-and-adopt unless the user explicitly requested a redesign.

Run this skill's `scripts/extract-tokens.py <path>` first, resolved against the skill
directory as described under Supporting material. It inventories declared tokens — CSS
custom properties, Tailwind theme values, `tokens.json` — classifies them by role,
counts who consumes each one, and emits the adoption table section 9 of the template
asks for. Adopting should be cheaper than inventing, and gathering this by hand is what
made it expensive.

When it finds no declared tokens, it reports the hardcoded values that repeat across
stylesheets. Those are *observed*, never *approved*: a value repeated twice is a
convention at best and a copy-paste at worst. Reconcile them before proposing anything
new, and say which they are.

### When there is genuinely no system

Only when the inventory comes back empty does the brief select a foundation, and it
selects from this product's constraints rather than from fashion: platform and
framework, information density, accessibility target, locale and script coverage,
licensing, and what the team already knows.

Present two or three candidates with tradeoffs and a recommendation rather than
defaulting silently to one. Propose first and let the user choose — a concrete
comparison they can react to beats a blank interview.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final brief, and every external write
stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means one pass per evidence stream: design-system inventory, journeys and
content, responsive and localization behavior, or accessibility evidence. Subagents
return sources, conflicts, and gaps; they never choose authority, approve a divergence,
invent copy, or claim compliance. Design decisions, tradeoffs, cross-flow consistency,
and user questions stay with the main agent. Keep unresolved evidence visible rather
than narrowing the brief or filling gaps with assumptions. Quick decisions and tightly
coupled feature briefs stay in the main agent.

### 2. Identify the decision that must be made

State the scope in one or two sentences:

- who performs the task and in what conditions;
- the outcome they need and the mistake they must avoid;
- the screens, flows, or components in scope;
- fixed constraints and decisions still open;
- how success will be checked, if evidence exists.

Do not manufacture a persona or success metric from a thin request.

### 3. Ask only material questions

If missing information would change the design, ask one short batch. Use the
interaction method available to the current agent. Do not depend on a named
question tool.

Ask no more than six questions. Prefer choices grounded in the supplied context.
Common gaps are the primary actor, critical journeys, platform and environment,
existing-system authority, supported locales, and safety or regulatory
constraints. Skip questions whose answers are already available.

For a quick decision, ask only what is needed for that decision. Do not require a
product-wide interview.

### 4. Research only where it changes the answer

Current research is required when a decision depends on:

- accessibility standards, law, regulation, or platform guidance;
- font licensing, script coverage, browser or framework behavior;
- safety-critical or specialized domain conventions;
- a supplied external product or design-system reference.

Current category research is also a legitimate input when choosing a foundation for
greenfield work, or when a pattern's conventional form is genuinely in question. It
informs a decision; it never substitutes for one.

Use primary sources for standards and platform behavior. Cite the source and the date
checked. Whenever research feeds a decision:

- **adapt the pattern, never the identity** — do not reproduce another product's trade
  dress, proprietary assets, or distinctive visual signature;
- record what is being adopted, what is being rejected, and why it fits this product;
- keep a reference product as evidence for a decision, never as the decision itself.

If current research is unavailable, state the limitation and avoid claims that
depend on it.

### 5. Make the design decisions

Use references/anti-generic.md for decision quality and references/tokens.md when
tokens are in scope.

Every consequential decision should include:

- the decision;
- the evidence or constraint behind it;
- the tradeoff;
- its status: adopted, proposed, or open.

Do not repeat this ceremony for routine inherited tokens. A compact adoption note
is enough when the existing system already settled the choice.

Cover only the modules the request needs:

- product context and design principles;
- journeys, information hierarchy, and screen inventory;
- per-screen layout and primary action;
- component reuse, variants, interaction states, and content;
- tokens and visual direction;
- responsive and input behavior;
- localization, bidirectional layout, and content expansion;
- accessibility target and implementation checks;
- assumptions, divergences, and open decisions.

Derive the component inventory from the actual screens and flows. Do not generate
a generic library of unused primitives.

### 6. Write the artifact

For a feature or full brief, use references/design-md-template.md and omit
sections that do not apply. Say why a consequential section was omitted.

Copy must be handled honestly:

- reuse approved product terminology when available;
- label newly written interface text as draft;
- do not invent policy, pricing, safety, or legal claims;
- show enough copy to settle layout and recovery behavior without pretending it
  has been approved.

Keep the document readable. Use short paragraphs, tables where comparison matters,
and diagrams only when they clarify structure or flow. Avoid a table for material
that is easier to understand as two sentences.

### 7. Specify accessibility without claiming compliance

Read references/accessibility.md whenever interactive UI is in scope.

WCAG 2.2 AA is the default design baseline for new web work unless the product has
another approved target. Native products also need current platform guidance.
Legal obligations must be verified for the jurisdiction and product.

Distinguish clearly:

- target: what the design intends to meet;
- specification: behavior the brief requires;
- verification: checks that must run on the implementation;
- compliance: a claim that needs complete evidence and, where applicable,
  qualified review.

Use this skill's scripts/contrast.py, resolved against the skill directory, only for
opaque sRGB hexadecimal colors. Do not estimate
ratios. Alpha colors must be composited to their rendered opaque value first.

### 8. Check the brief

Before handing it over, confirm:

- scope matches the request;
- approved existing patterns were preserved or divergences are explicit;
- facts, assumptions, proposals, and open decisions are distinguishable;
- every key journey includes failure and recovery behavior;
- screen, component, and state inventories agree;
- responsive behavior describes reflow rather than device labels alone;
- keyboard, focus, zoom, touch, motion, screen-reader, and localization behavior
  are specific where relevant;
- contrast values came from the helper;
- no compliance, research, or approval was invented;
- the prose sounds like a practical teammate, not a design generator.

Handoff with the artifact location or proposed patch, the few decisions most worth
reviewing, the assumptions that remain, and the implementation checks still
required.

## Supporting material

Every path below is relative to the directory containing this `SKILL.md`, not your
working directory. Resolve that directory once and use absolute paths when running the
scripts.

- references/evidence-and-modes.md: scope, authority, and change safety
- references/anti-generic.md: product-specific decision checks
- references/tokens.md: token design and adoption guidance
- references/accessibility.md: standards, interaction requirements, and testing
- references/design-md-template.md: modular brief template
- scripts/contrast.py: WCAG 2.x contrast helper
