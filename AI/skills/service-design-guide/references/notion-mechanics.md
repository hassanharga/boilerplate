# Notion mechanics

Use this reference only for Yassir Mobility Design Guides. Treat every identifier, schema, template,
and Markdown shape as live data that must be fetched again before a write.

## Operations

With the connected Notion MCP, these are the operations this skill needs. Names differ across
agents, so each row also states the capability to look for when these exact tools are absent:

| Operation | Tool | Capability if unavailable |
| --- | --- | --- |
| Find a guide | `notion-search` | Search or resolve a page by title |
| Read a page or database | `notion-fetch` | Fetch page, database, data source, and current Markdown spec |
| Read rows | `notion-query-data-sources` | Query rows in a data source |
| Instantiate a template | `notion-duplicate-page` | Duplicate a page or instantiate a template |
| Add rows | `notion-create-pages` | Create pages under a data source with a database template |
| Edit content or properties | `notion-update-page` | Update exact page content or properties |
| Wait on async work | `notion-get-async-task` | Poll asynchronous work |

Verification re-fetches with the same read operation. Inspect the active contract before
calling: payload shapes differ even where names match, so do not copy a JSON shape from this
skill. If the connector exposes the enhanced Markdown resource (commonly
`notion://docs/enhanced-markdown-spec`), read the current version before creating or changing
content.

If a required safe capability is unavailable, stop at a draft or write plan. Do not approximate an
external write with an unsafe whole-page replacement.

## Resolve the exact guide and local databases

Every Design Guide owns its own contract databases. Their display names repeat across services, so a
global name search is not enough.

1. Fetch the exact Design Guide and verify its title, ancestor service, and sibling Scope Guide.
2. Read the inline database or data-source references in the section being changed.
3. Match the data source by both its containing section and its live schema.
4. Fetch that data source to obtain current property names, types, select values, relations, views,
   and database templates.
5. Confirm relations point to databases belonging to the same guide when that is the intended model.

Never reuse a Dispatch data-source ID for another service. Cached collection and page IDs in this
skill are discovery hints only.

## Live schema wins

The guides currently use databases for domain events, commands, queries, integration events,
presentation adapters, infrastructure adapters, and ports. Common properties include:

| Section | Typical title | Typical additional properties |
| --- | --- | --- |
| Domain events | `Name` | `Version`, system-managed ID |
| Commands | `Command` | `Story`, system-managed ID |
| Queries | `Query` | `Story`, system-managed ID |
| Integration events | `Name` | `Type`, `Version`, `Domain Event`, system-managed ID |
| Presentation adapters | `Name` | `Type` |
| Infrastructure adapters | `Name` | none |
| Ports | `Name` | `Type` |

This table describes the established pattern, not a write schema. Use exact names and values from the
fetched data source. Never set system-managed IDs. Do not create a new select option merely because
capitalization differs.

For an integration-event relation, follow the live template and schema. A published event commonly
relates to the local domain event that triggers it; a consumed event commonly has no local domain
event. If the live model and evidence do not fit that pattern, report the mismatch instead of forcing
the relation.

## Row content contract

Prefer the current database template. Fetch its template ID or current exemplar, apply it when the
active capability supports templates, wait for asynchronous template application, then populate its
placeholders surgically. Do not send custom content in the same create operation when the capability
says a template provides the body.

If template application is unavailable, fetch the current template or a row created from it and
reproduce its meaningful structure in the supported Markdown dialect. Include the body during row
creation when possible so a titled-but-empty page is not left behind.

Preserve useful gray `📌` context callouts and blue `💡` editor guidance from the live template. Use
real page mentions and links; do not leave template prompts in completed content.

### Command and query

Follow the current template, normally covering:

- operation or query signature;
- plain-language description;
- actor;
- returned value;
- preconditions;
- postconditions or guarantees.

Derive conditions from current validation/business rules and the linked story. Do not invent them to
make a row look complete.

### Domain event

Follow the current template, normally covering:

- what the event means;
- the exact trigger;
- the actual versioned schema or code definition;
- the current internal flow and handlers.

Do not paste a universal event envelope from this skill. Derive the envelope and payload from the
current code, schema registry, and version-compatible shared framework. If the schema is unavailable,
mark it unverified or leave an explicit TODO.

### Integration event

Cover the event's meaning, direction, source, transport/topic, versioned schema, producer or consumer,
and observable effect. For consumed events, link the owning service's contract where available. For
published events, name known consumers only when evidence exists.

Do not create a current integration-event row based only on a local domain event, a Scope Guide plan,
or a container-diagram relationship. Require boundary-crossing evidence such as a producer/consumer,
topic or queue, subscription, serializer, schema, or deployed integration configuration. Keep planned
or unverified events in a proposal/TODO unless the live database explicitly supports status.

### Presentation adapter

Name the real HTTP, CLI, or messaging adapter, its responsibility, and the commands or queries it
exposes. Link contract rows when the live template supports those links.

### Infrastructure adapter

Name the real repository, client, broker, cache, or other driven adapter and the operations it
implements. Include transport or storage details only when verified.

### Port

Describe the real driving or driven boundary and include the current signature. Follow the repository
and version-compatible architecture guide: use the actual interface, abstract class, type, or token;
do not impose one representation universally.

## Idempotent row workflow

Before creating rows:

1. Re-fetch the target guide and data source.
2. Query existing rows and normalize the identity fields for comparison: trim surrounding whitespace
   and compare the title plus discriminators such as direction and version where relevant.
3. Classify each requested row as absent, exact existing, conflicting existing, or ambiguous.
4. Create only absent rows. Update an existing row only when that update was approved.
5. Stop and report ambiguous or conflicting matches rather than guessing.

After the operation, query and fetch again. Verify each expected row's unique identity, properties,
relations, template/body content, and destination. Confirm the operation did not introduce duplicates.

## Partial failures and retries

Notion creation, duplication, and template application may be asynchronous or partially successful.

- Record the requested identities before writing.
- Wait for a returned asynchronous task to finish when polling is available.
- If the result is ambiguous or times out, query the target before retrying.
- Reconcile requested versus observed rows.
- Retry only rows proven absent, with a bounded attempt count.
- Never replay the whole batch after some rows succeeded.
- Report unresolved partial state and provide exact page links.

This reconciliation is the rollback strategy for creates: avoid duplicates and leave an auditable list
of what exists. Do not archive or delete a partially created page without explicit authorization.

## Safe page updates

Re-fetch immediately before updating. Use an exact, narrow content or property update. Preserve child
pages, inline databases, custom sections, comments, and unrelated text.

Do not use whole-page replacement when child pages or databases could be removed. Never enable a
“delete omitted content” option for routine guide maintenance. If the capability cannot perform a
surgical update safely, return the proposed content and stop.

After an update, compare the refreshed page structure with the pre-write snapshot. Confirm synced
references still point to the intended sources and every pre-existing child page and inline database
is still present.

### Synced blocks

A synced reference may point to a source used by several services. Before editing a source:

1. identify the source block and known embedding pages;
2. show the user the proposed change and blast radius;
3. obtain separate explicit confirmation for the shared edit;
4. update the source only, then verify representative embeddings.

Without that confirmation, leave the synced content unchanged and propose a guide-local alternative.

### Page verification

Changing a page's verification status is a separate external mutation and may assign the connected
actor as owner. Do it only after evidence-based review and explicit user authorization.

## Creating a new guide

Resolve and duplicate the current blank service or Design Guide template. Duplication can be
asynchronous; wait for completion before inspecting the new tree.

After duplication:

1. verify the new page is under the intended service;
2. rename only the intended pages and replace template placeholders;
3. update project metadata and mentions;
4. re-resolve every new guide-local data source and template;
5. confirm all expected sections, databases, relations, and views exist;
6. populate only approved, evidence-backed content.

Never edit the blank template itself when the request is to create a service guide.
