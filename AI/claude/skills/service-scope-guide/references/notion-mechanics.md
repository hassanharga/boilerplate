# Notion mechanics

Use this reference only for Yassir Mobility Scope Guides. Treat every identifier, schema, template,
and Markdown shape as live data that must be fetched again before a write.

## Operations

With the connected Notion MCP, these are the operations this skill needs. Names differ across
agents, so each row also names the capability to look for when these exact tools are absent:

| Operation | Tool | Capability if unavailable |
| --- | --- | --- |
| Find a guide | `notion-search` | Search or resolve a page by title |
| Read a page or database | `notion-fetch` | Fetch page, database, data source, and Markdown spec |
| Read rows | `notion-query-data-sources` | Query rows in a data source |
| Instantiate a template | `notion-duplicate-page` | Duplicate a page or instantiate a template |
| Add rows | `notion-create-pages` | Create pages under a data source with a database template |
| Edit content or properties | `notion-update-page` | Update exact page content or properties |
| Wait on async work | `notion-get-async-task` | Poll asynchronous work |

Inspect the active tool contract before calling: payload shapes differ even where names match, so
do not copy a JSON shape from this skill. If the connector exposes the enhanced Markdown resource
(commonly `notion://docs/enhanced-markdown-spec`), read it before creating or changing content.

If a required safe capability is unavailable, stop at a draft or write plan. Do not approximate an
external write with an unsafe whole-page replacement.

## Resolve the exact guide and its database

Every Scope Guide owns its own Functional Requirements database, and they all share the display
name "Functional Requirements". A global name search is not enough.

1. Fetch the exact Scope Guide and verify its title, ancestor service, and sibling Design Guide.
2. Read the inline database reference in the Functional Requirements section.
3. Fetch that data source to get current property names, types, status and select options, and
   the default page template.
4. Query rows with the data source's SQL or rows mode. Text returned by SQL loses mentions and
   links, so fetch the row page before rewriting any rich-text property.

Never reuse the Dispatch data source ID for another service.

## Creating requirement rows

Before creating:

1. Re-fetch the guide and data source.
2. Query existing rows. A row's identity is its requirement ID plus its version (the `(vN)` title
   suffix and the `Version` property; no suffix means v1). Classify each proposed row:
   - **absent:** no row has this ID and version, so it can be created. That includes a new
     version of an existing ID, provided it is one higher than the latest existing version;
   - **already existing:** the same ID and version with the same title, trimmed and case-folded;
   - **conflicting:** the same ID and version with a different title; a version number that
     skips or goes back (for example v4 when the latest is v2); or a proposed new capability
     reusing an existing ID;
   - **ambiguous:** anything you cannot place, such as an unprefixed row whose title nearly
     matches.
   For guides without ID prefixes, compare trimmed, case-folded titles instead.
3. Create only absent rows. Stop and report conflicts or ambiguity.

To create: prefer the database's default template. Apply it when the capability supports templates,
wait for template application to finish, then fill placeholders with narrow updates. Do not send
custom content in the same create call when the capability says the template provides the body.
When templates are unavailable, fetch the template page and reproduce its structure in the
supported Markdown, including the body in the create call so no titled-but-empty row is left.

Set only properties the user approved. Never set the auto-increment `ID`. Use exact existing select
and status option names; do not create new options.

After creating: query and fetch again, then verify each row's title, properties, body, and parent
data source, and that there are no duplicates.

## Partial failures and retries

Creation, duplication, and template application may be asynchronous or partially successful.

- Record the requested row identities before writing.
- Wait for a returned async task to finish when polling is available.
- On an ambiguous result or timeout, query the database before retrying.
- Retry only rows proven absent, with a bounded attempt count; never replay a whole batch.
- Report unresolved partial state with exact page links.

Do not archive or delete a partially created page without explicit authorization.

## Safe page updates

Re-fetch immediately before updating. Use an exact, narrow content or property update. Preserve
child pages, the inline database, synced blocks, custom sections, comments and discussion anchors,
and unrelated text.

Never use whole-page replacement where it could remove the inline database or child pages, and
never enable a "delete omitted content" option for routine maintenance. If the capability cannot
update surgically, return the proposed content and stop.

After an update, compare the refreshed page with the pre-write snapshot. Confirm the inline database
and every synced reference are still present and pointing to the same sources.

### Synced blocks

Dispatch's glossary table and recordings callout are synced blocks; the Design Guide may embed the
glossary. Before editing a synced source:

1. identify the source block and the known embedding pages (at least the sibling Design Guide);
2. show the proposed change and which pages will change with it;
3. obtain separate explicit confirmation for the shared edit;
4. edit the source only, then verify one embedding page.

Without that confirmation, leave the synced content unchanged and deliver the proposed glossary rows
as a draft.

### Page verification

Changing a page's verification status is a separate mutation and may assign the connected actor as
owner. Do it only on explicit request after an evidence-based review.

## Creating a new Scope Guide

A new service normally gets its whole guide set by duplicating the blank service template
(`<MICROSERVICE>` in the Mobility Microservices database), which includes a blank Scope Guide. If
the service page already exists without a Scope Guide, duplicate the blank Scope Guide under it.
Duplication can be asynchronous; wait before inspecting the new tree.

After duplication:

1. verify the new page is under the intended service page;
2. rename only the intended pages (`<Service> - Scope Guide`);
3. update the `Project` mention and the footer previous/next mentions to the real pages;
4. re-resolve the new guide-local Functional Requirements data source and its template;
5. populate only approved, evidence-backed content; leave unknown authors as placeholders.

Never edit the blank template itself.
