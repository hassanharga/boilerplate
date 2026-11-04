# Delivering and publishing a PRD

Read this reference only when the user requested a file or a shared destination. Drafting
a PRD does not authorize publishing it.

## Resolve the destination before the first write

Use the destination the user named. If none was named, leave the result in chat or ask
whether they want a local file. Do not offer or create multiple copies by default.

Before writing, resolve:

- the authoritative destination;
- whether an existing document must be updated instead of created;
- the repository or workspace naming convention;
- the parent page, folder, space, or database when relevant;
- who can see the destination;
- whether the write creates, replaces, or appends.

Show the resolved destination before a shared write when it could be confused with
another similarly named location. Never infer permission to update from permission to
create, and never overwrite an existing page merely because the title matches.

## Local file

Match the repository's existing documentation convention. Locations such as `docs/prds`,
`docs/product`, or `specs` are examples to detect, not defaults to impose.

- Preserve an existing filename and structure during refresh work.
- For a new file, follow the repository's naming and numbering pattern.
- Do not overwrite an existing PRD without explicit authorization.
- Read the file back and report the final path.

Writing a file into a working tree is not the same as committing it. Commit, push, and
pull-request creation each need their own authorization.

## Shared knowledge system

Use the connected capability available in the current runtime. In Claude Code that is the
Notion MCP (`notion-search`, `notion-create-pages`, `notion-fetch`) or the Atlassian MCP
(`getConfluenceSpaces`, `searchConfluenceUsingCql`, `createConfluencePage`). Tool names
differ across agents, so fall back to whatever search, create, and fetch capability the
runtime exposes.

1. Resolve the exact workspace and parent location.
2. Search that parent for an existing PRD on the same subject before creating a new one.
3. Confirm create versus update.
4. Preserve the destination's template and metadata.
5. Publish only the approved content.
6. Read the result back.
7. Report the resulting link.

If the destination cannot be resolved safely, ask for the exact page or parent link
rather than guessing.

## Write once, and recover from ambiguity

A timeout, connection failure, or interrupted response after a write request is
ambiguous — the platform may have accepted it. Before retrying, search or fetch the target
by parent, title, author, and recent creation time. Retry only after confirming the
expected document does not exist. Never blindly resend a create request.

## Verify after writing

Read the result back and verify:

- platform, workspace or site, and parent;
- document identity, title, and URL or path;
- expected status, requirement IDs, and required sections;
- tables, acceptance criteria, and open-decision content survived the conversion;
- no raw placeholders remain;
- no duplicate document and no unintended overwrite.

Return the verified URL or path. If the read-back cannot be completed, say publication is
unverified rather than claiming success. If no authenticated publishing capability
exists, return the ready-to-publish content and state that nothing was published.

## Multiple copies

Create more than one copy only when the user requests it. Name one source of truth, link
secondary copies back to it, and record how updates stay synchronized — or state plainly
that the secondary copy is a snapshot.

## Handoff

Report the artifact path or URL, readiness status, source of truth, the decisions most
worth reviewing, and the open items that block design, RFC, planning, or implementation.
Do not repeat the entire PRD in the handoff.

Ticket breakdown is a separate, explicitly requested action — never a side effect of
publishing. See the work-item breakdown section in `SKILL.md` when the user asks for it.
