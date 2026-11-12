---
name: core-mobility-jira-ticket
description: Use when drafting, splitting, polishing, creating, or updating Jira work items for Yassir Core Mobility/CMB, including Core squad work for Dispatch Service, LTS, Maps and Routes, Backend, bugs, defects, or monthly metrics classification.
metadata:
  short-description: Create CMB tickets with Core squad conventions
---

# Core Mobility Jira Tickets

Produce implementation-ready CMB work items that reflect the requested work, preserve source context, and classify Core squad capacity consistently.

## Authorization

| User request                                          | Allowed result                                              |
| ----------------------------------------------------- | ----------------------------------------------------------- |
| Draft, prepare, split, or polish                      | Return a preview only; do not write to Jira.                |
| Explicitly create or update                           | Perform only the described issue mutation after validation. |
| Transition, assign, comment, link, or add to a sprint | Perform only when explicitly requested.                     |

For every live Jira read or write, use the connected Atlassian Rovo MCP when it
is available. Discover its operations by capability, such as accessible-site
discovery, metadata inspection, JQL search, issue read, create, edit, and
transition, because exposed function names differ across agents. If Rovo is not
available, use an equivalent authenticated Atlassian or Jira connector. If no
authenticated Jira capability is available, provide a complete draft and state
that Jira was not changed. Do not use `curl` or the Jira web UI as an implicit
fallback.

For live creation or editing, read [references/cmb-live-configuration.md](references/cmb-live-configuration.md) first.

## Classify for monthly metrics

Use the metrics guide as policy; recent tickets are context, not authority. The guide
is the Notion page named in
[references/cmb-live-configuration.md](references/cmb-live-configuration.md) — fetch it
rather than relying on the summary below when the classification is contested, when a
requested component or priority conflicts with policy, or when the cached configuration
is stale. The table here is a cache of that policy, not the policy itself.

| Category | Work                                   | Jira classification                                                  |
| -------- | -------------------------------------- | -------------------------------------------------------------------- |
| `Tech`   | Explicit technical-roadmap work        | `Backend` component; not Bug or Defect                               |
| `Prod`   | Feature, microservice, or product work | Non-Backend owning component; not Bug or Defect                      |
| `Main`   | Maintenance or a problem               | Bug for production; Defect before production; P0 or P1 per the guide |

Service-specific work is `Prod` unless the request or source explicitly identifies it as technical-roadmap work. Renovate review work is also `Prod` unless explicitly tied to that roadmap. Default to one owning component. Never combine `Backend` with a non-Backend component. A `Main` ticket with P2, P3, or no priority is invalid under the metrics guide: ask the user to select P0 or P1 before writing. If any requested component, priority, or work type conflicts with metrics policy, surface the conflict and ask before writing; do not silently accept or relabel it.

Jira issue type and metrics category are independent. A Technical Task is not automatically `Tech`; work owned by LTS, Dispatch Service, or Maps and Routes remains `Prod` unless explicit technical-roadmap evidence requires `Backend` and `Tech`.

Example: “Create a Technical Task for LTS secondary-datasource work” maps to Project `CMB`, category `Prod`, issue type Technical Task, Squad `Core`, and component `LTS`.

## Ticket contract

Use:

```text
[Core][<service-or-area>]: <concise outcome or imperative title>
```

Default normal implementation work to Technical Task. Set Squad to Core and select the owning component. Add Story Points only when the user supplies an estimate. Add a sprint only when requested, after resolving the current sprint dynamically. Never invent an estimate, priority, sprint, owner, label, parent, or issue relationship.

Every draft, preview, mutation plan, and post-write verification starts with its authorization outcome and this complete field table:

| Field            | Required value rule                                                          |
| ---------------- | ---------------------------------------------------------------------------- |
| Project          | `CMB` / Core Mobility                                                        |
| Summary          | `[Core][<service-or-area>]: <title>`                                         |
| Metrics category | Exactly `Tech`, `Prod`, or `Main`; never invent another category             |
| Issue type       | Technical Task by default; Bug or Defect for `Main` according to environment |
| Squad            | `Core`                                                                       |
| Component        | Owning component consistent with the metrics category                        |
| Optional fields  | Only values supplied by the user or required by current Jira policy          |

Then provide Description, Acceptance criteria, and any conflicts, open questions, duplicate risk, or unsupported fields. Always name `Core` and the owning component explicitly; do not replace known required values with placeholders such as “from metadata.” An output missing a required row is incomplete.

Keep the table complete but compact. Use one `Optional fields` row that lists only the
values actually supplied, or says `None supplied`; do not add a separate row for every
absent optional field. Omit empty conflict and open-question sections rather than printing
"none." Keep a real limitation, such as an unperformed duplicate search, when the reader
needs it to understand what was not verified.

The complete field table is a pre-write gate. Do not start or describe a mutation sequence until every required row has a concrete value.

Write a concise description followed by observable, testable acceptance criteria. Include relevant behavior, contracts, persistence, integration, rollout, observability, and unchanged behavior only when supported by the request or sources. Do not fabricate implementation details merely to make the ticket look complete; identify material unknowns as open questions.

Write the description and acceptance criteria as a teammate would write them for the
engineer who will pick up the ticket. Lead with the concrete problem and required outcome;
do not repeat the summary as an introduction or add generic benefit language. Use short,
natural sentences and one observable behavior per acceptance criterion. Use Given/When/Then
only when the team or user asks for it. Remove all placeholders before presenting or writing
the ticket.

When polishing an existing issue, read it first; read-only retrieval needs no additional authorization. Preserve still-relevant links, diagrams, schemas, payloads, code blocks, tables, sample data, rollout or migration notes, implementation constraints, and open questions automatically. Reorganize them under clear sections rather than asking whether to retain them. A request to replace or shorten the description authorizes structural rewriting, not removal of these artifacts; remove one only when the user explicitly requests its removal or clearly supersedes it. Without the current issue content, state that no faithful preview can be produced instead of inventing generic text.

## Splitting an item

Two shapes, chosen by what the work actually is:

| Situation | Result | Link |
| --- | --- | --- |
| Work spans several deliverables under one outcome | An Epic with child Technical Tasks | Parent link on each child |
| One oversized item is really several independent pieces | Sibling items at the same level | `relates to` between them |

A split is a draft until the user approves it. Present every child with its own complete
field table before writing anything, then create them sequentially and stop on the first
failure — a half-written split is worse than none.

**Each child is classified on its own work, not inherited from the parent.** The metrics
guide classifies work, not tickets, so a `Main` bug can legitimately split into a `Main`
fix and a `Tech` hardening task. Say so explicitly when a split changes the category mix,
because that moves the monthly numbers and the user may not intend it.

Never invent a parent, an issue relationship, or a child that the source material does
not support. If the right division is unclear, propose one and ask rather than guessing.

## Draft or mutation workflow

1. Establish work intent, environment, owning area, metrics category, issue type, and requested optional fields. Ask one short question only when ambiguity materially changes the ticket.
2. For an existing issue, read its current state. For a new issue, search narrowly for a likely duplicate or related ticket. A clear duplicate requires user direction before creation.
3. Build and present the complete field set and description. A request to draft, split, or polish stops here.
4. Before a write, discover the accessible site and current issue-type fields. Treat cached IDs as hints, not permanent truth.
5. Create or edit only after the authorization and policy gates pass. If a requested optional field requires a create-then-edit sequence, keep both operations within the authorized ticket scope. For multiple tickets, write sequentially and stop on the first failure.
6. If any write result is ambiguous, fetch/search for the expected issue before retrying; never risk duplicate creation.
7. Read the result back and verify summary, type, Squad, components, description, and every requested optional field. Report the issue key and URL plus any rejected, omitted, or partially applied field. Never call a partial result complete.
