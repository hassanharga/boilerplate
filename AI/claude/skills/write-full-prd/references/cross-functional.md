# Cross-functional product behavior

Use only the sections that change the scoped product behavior or release
decision. Do not fill every category with generic statements.

## Security, privacy, and permissions

Clarify:

- roles, tenant boundaries, and delegated access;
- sensitive actions and re-authentication needs;
- information collected, purpose, consent, access, correction, export, deletion,
  and retention;
- secrets or sensitive values that must never be exposed;
- audit evidence and administrator visibility;
- abuse, fraud, or cross-user access paths relevant to product behavior.

Do not invent a retention period, legal basis, certification, or regulatory
mapping. Name the accountable owner and current source.

## Accessibility and localization

Specify product outcomes such as:

- supported platforms, input methods, assistive technology, zoom, and text scale;
- keyboard, focus, announcements, time limits, and recovery requirements;
- supported locales, approved terminology, content expansion, and formatting;
- right-to-left reading and focus order, icon exceptions, mixed-direction data,
  and numeral behavior.

Link detailed visual and interaction design to the UI/UX brief. Do not claim
accessibility compliance from the PRD alone.

## Reliability and degraded behavior

For each important journey, decide what the user experiences during:

- no data, stale data, or partial data;
- duplicate requests and concurrent changes;
- no permission or expired session;
- network loss, dependency timeout, and partial failure;
- retry, resume, idempotency, and cancellation;
- overload, maintenance, and recovery.

State the product-visible result and safe next action. Architecture belongs in
the RFC.

Use numerical latency, availability, recovery, or scale limits only when they
come from approved requirements or evidence. Otherwise record the owner and
decision needed.

## Analytics, audit, and decision evidence

Define only events and measures needed to:

- evaluate the product outcome and guardrails;
- operate and support the feature;
- investigate material decisions or failures;
- meet an approved audit requirement.

For each measure, identify its owner, source, audience, privacy classification,
and required decision. Avoid collecting data merely because it may be useful.

## Support and operations

Cover:

- support-agent visibility and safe corrective actions;
- user-facing status and escalation routes;
- operational ownership and hours of coverage;
- runbook, alert, dashboard, and audit needs at product level;
- back-office tools or manual work required for launch;
- training, policy, content, and communication dependencies.

Do not assume a manual process is free. Record its volume, owner, and failure
mode when known.

## Compatibility, migration, and rollout

Consider:

- existing users, historical records, and grandfathering;
- client, API, event, and integration compatibility;
- data backfill, reconciliation, and irreversible changes;
- release audience, phases, feature controls, and app-store lead times;
- validation before expansion;
- rollback when permitted;
- containment, exception handling, and escalation when rollback is unsafe or
  prohibited;
- deprecation and customer communication.

Mandatory changes still need release boundaries. The boundary should separate the
required deadline behavior from optional improvements without weakening the
obligation.

## Dependencies and ownership

Record a dependency when another team, vendor, policy, contract, dataset, design,
or approval can block the outcome. Include:

- accountable owner;
- decision or deliverable required;
- needed-by date;
- current status;
- consequence if late or unavailable.

## AI and automation

When a product delegates judgment, generation, classification, or action to an
AI or automated system, define:

- allowed use cases, actors, sources, and data boundaries;
- outcomes the system may produce and actions it may not take;
- quality dimensions and an evaluation set that represents the intended use;
- abstention, uncertainty, review, override, and human handoff;
- harmful, hostile, sensitive, or out-of-scope input behavior;
- source attribution and freshness where answers depend on knowledge;
- logging, audit, feedback, appeals, and incident handling;
- model or vendor change evaluation;
- privacy, data use, retention, regional, latency, and cost guardrails.

Do not invent a quality threshold or describe a model choice as a confirmed
product requirement. Record the evaluation and decision owner.

## Experiments

For a reversible experiment, define:

- hypothesis and intended audience;
- exposure and exclusions;
- primary outcome and guardrails;
- minimum evidence or decision window;
- stop, continue, or expand criteria;
- cleanup and treatment of collected data.

Do not apply experimental kill criteria to mandatory work when disabling the
change would violate a requirement. Use go/no-go evidence and containment rules
instead.

## Engineering quality policy

Capture an engineering test or coverage requirement only when an approved source
makes it part of the release contract.

- If the repository or acceptance criteria require 100% unit coverage, preserve
  that exact requirement and define the measured scope.
- If another repository has no numeric coverage policy, do not introduce one.
- Do not replace behavior-level acceptance criteria with a statement about test
  coverage.
- The implementation plan should choose the test layers unless a regulated or
  contractual requirement specifies them.
