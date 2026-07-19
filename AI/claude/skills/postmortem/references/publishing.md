# Publishing a postmortem to Confluence or Notion

Only do this when the user explicitly asks. Default output is a local Markdown file.

Always write (or keep) the local Markdown file first, then publish from it — that way there's a source of truth even if the publish step fails.

## Confluence (Atlassian Rovo MCP)

1. If you don't already know the target, ask which **space** it should go in (or confirm a space they named). Use `getConfluenceSpaces` / `getVisibleJiraProjects` to resolve names to IDs if needed.
2. Confluence pages use storage-format HTML, not Markdown. Convert the doc: headings → `<h1>/<h2>`, tables → `<table>`, task list items (`- [ ]`) → Confluence task lists or a simple bulleted list, code spans → `<code>`. Keep it simple and valid — a clean bulleted list beats a broken macro.
3. Create the page with `createConfluencePage` (title = the postmortem title, body = converted HTML, space = resolved space). If updating an existing page, use `updateConfluencePage`.
4. Return the page URL to the user.

## Notion (Notion MCP)

1. Ask for (or confirm) the parent page/database the postmortem should live under. Use `notion-search` to locate it if the user names it.
2. Create the page with `notion-create-pages`. Notion accepts Markdown-ish content blocks, so the conversion is lighter than Confluence — pass the sections as blocks. Tables and to-do items map naturally to Notion table and to-do blocks.
3. Return the page URL to the user.

## After publishing

Tell the user where it went (URL) and confirm the local Markdown copy still exists as the source of truth.
