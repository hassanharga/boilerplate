# Clarifying product requirements

Use this reference when missing evidence would change the problem, release
boundary, product behavior, safety, or measurement plan.

## Read before asking

Inspect the sources already available. Do not ask the user to repeat:

- the problem and acceptance criteria in an approved ticket;
- current behavior visible in the product or repository;
- constraints in the design guide, RFC, policy, or repository instructions;
- baselines present in approved analytics;
- decisions already recorded in the existing PRD.

When two sources disagree, ask about the conflict directly and name both sources.

## One bounded question batch

Choose only the gaps that matter. Ask no more than six questions in the first
batch. A lean feature spec usually needs fewer.

### Problem evidence

- Who experiences the problem, during which task, and how do they handle it now?
- What evidence shows the problem exists: research, support cases, observed
  behavior, analytics, customer commitment, audit, or policy?
- What is the cost or risk of the current state?
- Why is the decision needed now?

### Outcome and scope

- What outcome must this release achieve?
- Which journey must work from trigger to safe completion?
- Which adjacent requests should be explicitly excluded?
- Is this an experiment, a deadline release, a migration, or a permanent product
  capability?

### Actors and policy

- Which roles act, approve, administer, audit, or receive the result?
- How do permissions, tenancy, geography, age, or account state change behavior?
- Who owns product, policy, legal, security, and operational decisions?

### Constraints and delivery

- Which existing product, APIs, data, design system, and contracts must be
  preserved?
- Which platforms, locales, accessibility needs, connectivity states, or release
  lead times matter?
- Which teams, vendors, migrations, or external approvals are dependencies?

### Measurement

- What outcome or guardrail should change, and what evidence exists today?
- How will the team know the release is safe enough to continue?
- If no baseline exists, what instrumentation or research can establish one?

## Ask a targeted follow-up only when needed

A second round is justified when an answer:

- changes the primary problem or actor;
- makes an included capability unnecessary;
- introduces safety, legal, privacy, or migration risk;
- conflicts with an authoritative source;
- leaves the release impossible to verify.

Quote the answer briefly and ask about the unresolved decision. Do not reopen
questions that were already answered. After that, document the remaining gaps.

## Challenge weak requirements constructively

Lead with the concrete problem in the answer and offer a recommendation.

| Answer | What is missing | Useful response |
| --- | --- | --- |
| "Everyone needs this" | Actor and context | "Which role would notice first if this were removed, and during which task?" |
| "Make it intuitive" | Observable outcome | "Which task should a first-time user complete without help, and what would count as failure?" |
| "Increase engagement" | Product outcome and measure | "Which action represents value, and do we have a baseline for it?" |
| "AI handles it" | Quality boundary and recovery | "Which sources may it use, how is a wrong answer detected, and when must a person take over?" |
| "Everything is required" | Release boundary | "If the date cannot move, which capabilities preserve the required outcome?" |
| "We will decide later" | Owner and blocking status | "Who owns the decision, and can the release proceed safely without it?" |

State what you recommend and why. The user can overrule it. Do not turn the
conversation into a test of product-management vocabulary.

## When the user asks to skip discovery

Respect the request. Produce a discovery draft that:

- labels unsupported statements as assumptions or proposals;
- avoids fabricated personas, targets, limits, and approvals;
- names the decisions that block implementation;
- does not claim to be build-ready;
- keeps the scope smaller than a fully researched PRD.

The draft should help the user react to concrete choices without disguising
guesses as requirements.

## Current-source gate

For regulated, policy-sensitive, or safety-critical work, request the current
authoritative source, its jurisdiction and effective date, and the accountable
owner who interprets it. External research can help locate and understand a
source, but it does not replace the organization's legal or policy decision.

Do not convert an unsourced statement about a regulation into a confirmed
requirement.
