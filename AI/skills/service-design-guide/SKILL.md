---
name: service-design-guide
description: Use when creating, updating, reviewing, or checking a Yassir Mobility microservice Design Guide, including its C4 diagrams, domain model, service contract, ports, adapters, or guide-local Notion databases. Also use when a Mobility architecture guide may be stale or must be reconciled with code and its Scope Guide. Do not use for generic architecture documentation outside this guide system.
metadata:
  short-description: Maintain evidence-backed Mobility Design Guides
---

# Service Design Guide

Create and maintain Yassir Mobility Design Guides without breaking their established Notion pattern
or presenting intended behavior as implemented behavior. Preserve useful human reasoning. Change only
what current evidence supports and the user authorizes.

## Operating principles

1. **Evidence before content.** Do not invent architecture, contracts, events, or adapters.
2. **Preserve the live pattern.** Existing guides are living documents, not disposable output.
3. **Separate status clearly.** Label claims as current, planned, deprecated, conflicting, or unverified.
4. **Review before mutation.** A review or drift audit is read-only. External writes require explicit
   authorization for the named destination and proposed changes.
5. **Prefer surgical updates.** Never replace a whole guide merely to change one section.

## Sources and precedence

Read repository instructions first. Record the repository path, current revision, relevant deployed
configuration, and version-pinned framework or chassis guidance.

Use these sources together:

1. Current repository code and deployed configuration describe implemented behavior.
2. The sibling Scope Guide describes intended requirements and planned behavior.
3. The existing Design Guide preserves rationale, terminology, and previous decisions.
4. Current, version-compatible Yassir DDD and hexagonal guides define shared conventions.
5. Schema registries, broker configuration, IAM, API specifications, and rollout documents provide
   evidence for deployed integrations.

Do not silently choose one source when they disagree. Report the conflict, cite both sides, and ask
for a decision only if resolving it is necessary for the requested change.

If the repository or target guide cannot be identified safely, ask for that missing information. Do
not ask routine questions whose answers are already present in the request or context.

## Live guide pattern

The page IDs below were last verified on 2026-08-23. They are discovery hints, never write
authority: re-resolve the target, template, schemas, and database identities on every run.
When this date is more than 30 days old, expect at least one ID to have moved and say in the
output that the cached IDs were not revalidated.

Use live pages in this order:

- **Updating an existing guide:** that guide's structure, guide-local databases, custom sections,
  and human-written rationale take precedence for presentation.
- **Mature exemplar:** Dispatch Service Design Guide
  (`17af03bdfe1b81f7a5a0e0db609a18f6`) demonstrates the expected depth and established pattern.
- **Creating a guide:** the live blank Design Guide
  (`5f9ac6581c754099a28f5d2709078370`) is the structural baseline.
- **Secondary exemplars:** Location (`7f8b91a700dd4ada9a7f40fe5a3d118e`), Lead
  (`1a4f03bdfe1b813989bedb69601d6ae2`), and Maps & Routes
  (`ec9de6d74743451abe7b3e8cab910087`) help identify shared patterns.

The Mobility Microservices collection was `collection://725a4fed-e1e1-4d1c-9c6f-e2e30ee91238`
at that verification date.

Preserve the recognizable pattern: metadata and table of contents; columns, toggles, callouts, and
navigation; C4 container and component diagrams; domain language/model/events; commands, queries,
and integration events; presentation, infrastructure, and application layers; appendices; and
guide-local inline databases. Preserve service-specific extensions such as Dispatch recordings,
orchestration flows, Engine, or EDB sections when present. Do not impose those extensions on services
that do not need them.

## Choose the mode from the request

- **Review or drift audit:** read-only. Return findings and evidence; do not write.
- **Create:** duplicate or instantiate the current blank template, then populate it.
- **Update:** inspect the existing guide and propose a drift report first. Apply only approved items.
- **Draft:** produce a local or conversational draft only when the user requests one.

Infer the mode, destination, and diagram scope from the request. Ask one concise question only when a
missing choice would materially change the result. A request that already says “update this Notion
guide” does not need another destination question. A row-only change does not need a diagram question.

## Workflow

### 1. Resolve and verify the target

Search for the exact service page and fetch the Design Guide and sibling Scope Guide. Check the page
title, ancestors, service identity, and guide-local databases. Before an authorized write, re-fetch
the target so the plan is based on current content.

Compare the two guides' last-edited times. **When the Scope Guide is newer than the Design
Guide, say so before doing anything else.** It usually means requirements moved and the
design was never reconciled, so the drift you are about to report may be intended change
rather than documentation rot — and the user may want the Scope Guide's new content brought
across rather than the code's current state written down. Name the gap in days and the Scope
Guide sections edited since.

For creation, resolve the current blank template from the Mobility Microservices database rather
than trusting the cached ID alone. Duplicate the template when that capability is available so the
page structure, databases, relations, views, and database templates are preserved.

### 2. Collect evidence

Inspect the current code and configuration relevant to the requested sections. Follow handlers,
controllers, consumers, producers, schemas, ports, implementations, persistence, and external
clients far enough to establish behavior. Read the Scope Guide and current Design Guide.

When the runtime supports subagents and the work splits into independent read-only passes,
delegate. Give each subagent a disjoint scope and the same evidence standard, and require it to
return findings with sources — never decisions, conclusions, or writes. Reconciliation, conflict
resolution, the final drift report, and every external write stay in the main agent. If subagents
are unavailable or a pass fails, run the same passes sequentially without reducing coverage.

Here that means one pass per evidence stream: code and configuration, the live Design and Scope
Guides, contracts, or diagrams. Each returns source links plus revision or last-edited evidence.
Source-precedence decisions, the unified drift report, approval gates, and every Notion or
repository write stay with the main agent. Small or tightly coupled updates stay in the main agent
entirely.

For each claim, keep a compact evidence record:

- status: current, planned, deprecated, conflicting, or unverified;
- code/config evidence with revision;
- Scope Guide evidence and last-edited time when available;
- existing Design Guide evidence and last-edited time;
- verification date and unresolved questions.

### 3. Produce a human-readable drift report

Lead with the decision or result. For a small change, use concise bullets. Use a comparison table only
when several sections or sources need mapping. Number every proposed change with a stable item ID,
then show:

- section or row;
- what is wrong, missing, or stale;
- evidence;
- proposed action;
- confidence or unresolved conflict.

Keep raw tool names, payloads, and template prompts out of user-facing content. Preserve valuable
existing rationale even when wording is imperfect. Do not rewrite adjacent material for polish.
Before a mutation, ask the user to approve the exact numbered items; do not treat general discussion
or approval of a different item as authorization for the whole report.

### 4. Build approved content

Read [references/template-structure.md](references/template-structure.md) for the section contract.
Read [references/notion-mechanics.md](references/notion-mechanics.md) before any Notion work. Read
[references/diagrams.md](references/diagrams.md) only when diagrams are in scope.

Use the service's actual vocabulary and real class, schema, topic, API, and file names. Do not promote
a local domain event to an integration event without concrete boundary-crossing evidence. A diagram
relationship is a clue to investigate, not proof of a current contract.

### 5. Apply only authorized writes

External writes include creating, duplicating, or updating Notion pages or rows; editing the source
of a synced block; changing page verification; rendering or uploading a confidential diagram; and
writing documentation into a repository. Obtain explicit authorization for the affected destination
and change set.

Use precise updates that preserve child pages, inline databases, synced blocks, custom sections, and
unrelated reasoning. A synced-source edit requires a separate impact preview and confirmation because
it changes every embedding page.

Record the baseline in the guide itself as part of the write: the repository commit SHA and
the date the content was verified against it. Without it the next reader cannot tell whether
the guide is a month or a year behind the code, and the whole drift audit has to be redone
from scratch. Put it where the guide already carries metadata rather than inventing a new
section, and update it only for the sections the write actually covered — a partial update
that stamps a fresh baseline across the whole guide is worse than no baseline.

### 6. Verify the result

After writing:

- re-fetch every changed page and row;
- confirm properties, body content, relations, destination databases, and templates;
- confirm no duplicate rows were created;
- reconcile partial or ambiguous results before retrying;
- verify diagrams contain the intended content, not merely an HTTP 200 response;
- report what changed, what remained untouched, and every TODO or conflict.

Do not mark a page verified unless the user explicitly authorizes that separate action and the guide
has been checked against current evidence.

## Writing style

Write for engineers who need to understand the service quickly:

- lead with what the component or contract does;
- use plain sentences and the team's vocabulary;
- name real artifacts instead of describing hypothetical ones;
- explain important tradeoffs and constraints without promotional language;
- define only domain-specific terms needed for shared understanding;
- retain established instructional callouts where they help future editors;
- avoid artificial completeness, filler sections, and arbitrary entry counts.

## Scope discipline

Touch only the requested and approved sections. Mention adjacent drift without editing it. Existing
guides may contain intentional service-specific structures; preserve them unless the user explicitly
approves their removal.
