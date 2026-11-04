# Publishing the RFC

Read this reference only after the draft is ready and the author has chosen a
destination. Publishing to Notion or Confluence creates shared state and notifications;
drafting an RFC does not authorize publishing it.

## Resolve the destination before the first write

Before writing anything, resolve:

- the final or explicitly accepted draft content;
- platform and workspace or site;
- the exact parent page, database, space, or folder;
- create a new page versus update an existing one;
- title and intended audience.

If these are already unambiguous in the request and available context, do not ask again.
Otherwise stop and ask one focused question. Never infer permission to update from
permission to create, and never overwrite an existing page merely because the title
matches.

The author may want more than one destination — for example the `.md` committed to the
repository and a mirror in Notion. That is fine; do each in turn from the same draft, and
name one as the source of truth.

## Local Markdown file

The simplest option and a good default for repositories.

- Default location: `docs/rfcs/` at the repository root. If it does not exist, offer to
  create it or ask for a preferred path.
- Filename: `NNNN-kebab-title.md` with a zero-padded sequence if the folder already uses
  numbering; otherwise `kebab-title.md`. Check the existing files first and match the
  convention rather than imposing one.
- Write the file, then read it back and report the path.

Writing a file into a working tree is not the same as committing it. Commit, push, and
pull-request creation each need their own authorization.

## Notion

Use the connected Notion capability in the current runtime. In Claude Code that is the
Notion MCP — `notion-search` to locate a parent, `notion-create-pages` to create, and
`notion-fetch` to read back. Tool names differ across agents, so if those are not present,
use whatever search, create, and fetch capability the runtime exposes.

1. Resolve the parent page or database if the author has not already named one. Search by
   name and confirm the match with the author before creating anything.
2. Search that parent for an existing RFC with the same title or subject before creating
   a new one, so a retry or a forgotten earlier draft does not become a duplicate.
3. Create the page under that parent with the RFC title and the Markdown body. Notion
   accepts Markdown for page content, so the draft transfers directly.
4. If no obvious parent exists and search finds nothing, ask the author to paste the
   parent page URL or ID rather than guessing.

## Confluence

Use the connected Atlassian capability. In Claude Code that is the Atlassian MCP —
`getConfluenceSpaces` to list spaces, `getAccessibleAtlassianResources` first if the cloud
ID is needed, `searchConfluenceUsingCql` to find a parent page, and `createConfluencePage`
to create. Fall back to whatever authenticated Confluence capability exists.

1. Identify the target space and confirm it with the author.
2. Find the parent page if the RFC should nest under one.
3. Search for an existing page with the same title in that space before creating.
4. Create the page with the title, space, and Markdown body.

## Write once, and recover from ambiguity

A timeout, connection failure, or interrupted response after a write request is
ambiguous — the platform may have accepted it. Before retrying any write, search or fetch
the target by parent, title, author, and recent creation time. Retry only after
confirming the expected page does not exist. Never blindly resend a create request.

## Verify after writing

Read the result back and verify:

- platform, workspace or site, and parent;
- page identity, title, and URL;
- the expected sections survived the conversion, including tables and code blocks;
- no raw placeholders or `_TODO(author)_` markers intended for removal remain;
- no duplicate page was created and nothing was unintentionally overwritten.

Return the verified URL or page identifier, and state whether a local copy also exists.
If the read-back cannot be completed, say publication is unverified rather than claiming
success.

If no authenticated publishing capability is available, return the ready-to-publish
content and state plainly that nothing was published.
