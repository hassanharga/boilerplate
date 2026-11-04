---
name: service-scope-guide
description: Use when creating, reviewing, updating, or checking a Yassir Mobility microservice Scope Guide or its Functional Requirements rows in Notion. This includes turning raw requirements, kickoff notes, or a PRD for a new service into a Scope Guide, drafting a new requirement or a new version of one, and reconciling a guide with Jira, the Design Guide, or released code. Do not use for PRDs, RFCs, Jira tickets, Design Guide architecture, or requirements documents outside this guide system.
metadata:
  short-description: Maintain evidence-backed Mobility Scope Guides
---

# Service Scope Guide

Create and maintain Yassir Mobility Scope Guides without breaking their established Notion pattern
or presenting an agent's guess as an agreed requirement. The Scope Guide says **what** the service
must do and **why**; its sibling Design Guide says **how**. Preserve human-written reasoning. Change
only what the evidence supports and the user authorizes.

A Scope Guide covers context, problem and solution; functional requirements (one Notion database
row each, with a story and Given/When/Then scenarios); non-functional requirements; constraints;
a glossary; and, in some guides, a requirements map, key concepts, and recorded walkthroughs.

## Operating principles

1. **Intent comes from people.** Requirements, priorities, milestones, and NFR targets are team
   decisions. Draft them from stated sources; never invent a business goal, actor, number, or
   deadline to make a section look complete.
2. **Behavior, not implementation.** Write observable outcomes a stakeholder can verify. Class
   names, databases, queues, and algorithms belong in the Design Guide unless the team made one
   a genuine constraint.
3. **Preserve the live pattern.** Existing guides are living documents, not disposable output.
4. **Separate status clearly.** Mark each claim as agreed, proposed, released, conflicting, or open.
5. **Review before mutation.** A review or drift audit is read-only. External writes need explicit
   authorization for the named destination and change set.
6. **Prefer surgical updates.** Never replace a whole guide or requirement row to change one part.

## Sources and precedence

Read repository instructions first when a repository is involved. Use these sources together:

1. The user's explicit decision in this conversation.
2. Approved content in the Scope Guide and its requirement rows.
3. Product sources: PRDs, RFCs, Jira epics and tickets, meeting notes, recorded walkthroughs, and
   written decisions. These define intended behavior.
4. The sibling Design Guide, which should derive from this guide. Design content that no
   requirement covers is a scope gap or unplanned design; report it, do not back-fill it silently.
5. Evidence of what is **released**: current code and deployed configuration, plus the service's
   User Guide, API specifications, and recent RFCs or adoption reviews that describe live behavior.
   These matter for a requirement's status and for spotting shipped behavior that no requirement
   covers, a common gap in older guides. They never define intent on their own.

Do not silently choose one source when they disagree. Report the conflict, cite both sides, and
ask for a decision only when the requested change depends on it.

If the target guide cannot be identified safely, ask for it. Do not ask for anything already in the
request or context.

Missing inputs are handled differently for a draft and for a write:

- **Drafting:** never block on gaps. When the actor, the benefit, a number, or a failure behavior
  is missing, draft with the gap marked in place (`So that <benefit — to confirm>`, `TBD — <who
  decides>`, *(proposed)*). Collect every gap as a question. Do not invent the missing content.
- **Ready to write to Notion:** the actor and the behavior are known, no template prompts remain,
  and each remaining gap is either answered or visibly marked. The user must have approved writing
  the item with those marks still in place. A row that meets this bar still starts at the initial
  status; "ready to write" is not the team's `Ready`.
- **Optional:** the Jira ticket, priority, and milestone. Fill them only from the user or the
  sources, and leave them empty otherwise.

## Live guide pattern

The page IDs below were last verified on 2026-09-30. They are discovery hints, never write
authority: re-resolve the target, template, schemas, and database identities on every run.
Report the result of that check: which cached IDs you confirmed, which changed or moved, and which
you could not reach. When the date above is more than 30 days old, say so, and suggest refreshing
the cached IDs in this skill if any have changed.

- **Updating an existing guide:** that guide's structure, its requirement database schema, custom
  sections, and human-written rationale take precedence for presentation.
- **Mature exemplar:** Dispatch Service Scope Guide (`17af03bdfe1b81a09405cf1ff1b04c54`),
  Functional Requirements data source `collection://2edf03bd-fe1b-814d-bb27-000bb31a0857`.
  It shows the expected depth: area-prefixed requirement IDs, versioned rewrites, detailed
  scenarios, a synced glossary, a requirements map, and recorded walkthroughs.
- **Creating a guide:** the live blank Scope Guide (`b2f2654057c343caa22acb181dba04d7`) under the
  blank service template (`4cb25d06a5364078b443758dbff71421`) is the structural baseline.
- **Secondary exemplars:** Location (`7878b9f5938a4e97befe2799c8f8c6fa`), Maps & Routes
  (`eec2ca33ec864eb0b93b490124cc9525`), Lead (`1a4f03bdfe1b81ba825fffd9d139c45d`), and Driver
  (`14bf03bdfe1b81e888f0d5b47b9389ae`) show how lighter services fill the same template.

The Mobility Microservices collection was `collection://725a4fed-e1e1-4d1c-9c6f-e2e30ee91238`.

Each guide owns its Functional Requirements database, and **the schemas differ**: the blank
template has `Name`, `Status`, `Version`, `JIRA Ticket`; Dispatch adds `Area`, `Sub-Area`,
`Priority`, `Planned Milestone`, `Summary`, and a `Closed` status; Location adds an `Out of scope`
status. Always fetch the target's live schema. Do not add Dispatch's extra properties to another
guide unless the user asks.

Preserve service-specific extensions such as Dispatch's Key Concepts section, recordings callout,
requirements map, or related-links toggle. Do not impose them on services that do not need them.

## Choose the mode from the request

- **Review or drift audit:** read-only. Return findings and evidence; do not write.
- **Create a guide:** turn the supplied material into a full draft, get approval, then duplicate the
  current blank template under the right service and populate it. When the input is raw notes, a
  PRD, or a feature list, read [references/from-raw-requirements.md](references/from-raw-requirements.md)
  first.
- **Add or revise requirements:** draft the rows, show them, write only approved ones.
- **Update other sections:** propose a numbered change list first; apply approved items only.
- **Draft:** produce a local or conversational draft when the user wants one, or when writes are
  not authorized or not possible.

Infer mode and destination from the request. Ask one concise question only when a missing choice
would materially change the result. "Add this requirement to the Dispatch Scope Guide" already
names the destination; it still needs approval of the drafted row before writing.

## Workflow

### 1. Resolve and verify the target

Search for the exact service page and fetch the Scope Guide and sibling Design Guide. Check the
title, ancestors, service identity, and the guide-local requirements database. Before an authorized
write, re-fetch the target so the plan rests on current content.

Compare the two guides' last-edited times. **When the Design Guide is newer and describes behavior
no requirement covers, say so first.** Usually that means the design moved ahead of agreed scope;
the user must decide whether to scope it or challenge the design. Name the gap in days and the
design sections involved.

### 2. Collect evidence

Read the Scope Guide, all requirement rows relevant to the request (query the database; do not rely
on the inline view), and the product sources the user named or linked. For a review, also look at
the service page's other guides (User Guide first) and search for recent RFCs about the service:
they often describe live behavior the Scope Guide never captured. For status checks, follow code
and configuration far enough to establish whether a behavior is actually released.

When the runtime supports subagents and the work splits into independent read-only passes, such as
the requirement rows, the product sources, and code for status, delegate one pass each. Require
sources in each result. Reconciliation, the final report, approval gates, and every external write
stay with the main agent. Small updates stay in the main agent entirely. If subagents are
unavailable, run the same passes sequentially without reducing coverage.

### 3. Report or propose

Lead with the result. For a small change use concise bullets; use a table only when several rows or
sources need mapping. Number each proposed change with a stable item ID and show the section or
row, what is wrong or missing, the evidence, the proposed action, and any open conflict.

For new or revised requirements, show the full drafted row: the properties and the body, rendered
readably, not as raw tool payloads. Ask the user to approve the exact item IDs. General agreement
or approval of one item is not approval of the whole list.

### 4. Build approved content

Read [references/template-structure.md](references/template-structure.md) for the section contract.
Read [references/requirement-rows.md](references/requirement-rows.md) before drafting or reviewing
any requirement. Read [references/notion-mechanics.md](references/notion-mechanics.md) before any
Notion write. Use `scripts/plantuml_url.py` only when the requirements map is in scope (see the
map section in `template-structure.md`).

Use the guide's own glossary terms, capitalized as the glossary does, and the team's real actor
names. When a requirement introduces a new term, propose a glossary row with it.

### 5. Apply only authorized writes

External writes include creating or duplicating pages, creating or updating requirement rows,
editing page sections, editing the source of a synced block, changing verification, and rendering a
diagram on the internal PlantUML server. Obtain explicit authorization for the destination and the
change set.

Never set a requirement's status to `Ready`, `Released`, or `Closed`, or change `Priority` or
`Planned Milestone`, unless the user asked for that specific value. These are team decisions. New
rows start at the database's initial status (usually `Not Ready`) unless told otherwise.

### 6. Verify the result

After writing, re-fetch every changed page and row. Confirm properties, body content, destination
database, and that no duplicate rows exist. Reconcile partial results before retrying. Report what
changed, what stayed untouched, and every open question or TODO.

## Writing style

Write for engineers, product partners, and operators who need to agree on scope quickly. Requirement
rows and guide sections should read like plain human writing, not a spec dump. Before drafting or
rewording anything, read [references/readable-writing.md](references/readable-writing.md). It holds
the rules, before-and-after examples, and a five-question check to run before presenting. In short:

- lead with the capability and its benefit;
- use short, plain sentences and the guide's glossary vocabulary;
- make every scenario outcome observable from outside the service;
- keep numbers honest: a target with its condition (percentile, load, window), or `TBD` with who
  decides;
- retain established instructional callouts where they help future editors; remove a blue `💡`
  callout only when its section is complete and the guide's convention is to remove them;
- avoid filler, promotional language, and arbitrary entry counts.

## Scope discipline

Touch only requested and approved sections. Mention adjacent drift — broken section numbering,
stale statuses, orphaned requirements — without editing it. Existing guides may contain intentional
service-specific structures; preserve them unless the user explicitly approves their removal.
