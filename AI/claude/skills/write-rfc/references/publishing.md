# Publishing the RFC

After the draft is ready, ask the author where it should go. Never publish to an
external destination (Notion/Confluence) without confirming — it's visible to
others. Publish to exactly the destination(s) the author picks.

## Local Markdown file

The simplest option and a good default for repos.

- Default location: `docs/rfcs/` at the repo root. If that folder doesn't exist,
  offer to create it, or ask for a preferred path.
- Filename: `NNNN-kebab-title.md` (zero-padded sequence) if the folder already
  uses numbering; otherwise `kebab-title.md`. Check existing files first to
  match the convention.
- Write the file with the Write tool and report the path.

## Notion page

Uses the connected Notion MCP tools.

1. Ask _where_ in Notion it should live if not already told — a parent page or a
   database (e.g. an "RFCs" or "Engineering Docs" space). Use
   `notion-search` to locate the parent by name and confirm the match with the
   author before creating anything.
2. Create the page under that parent with `notion-create-pages`, passing the RFC
   title as the page title and the Markdown body as content. Notion's API accepts
   Markdown for page content, so the same draft works directly.
3. If the author picked Notion but there's no obvious parent and search finds
   nothing, ask them to paste the parent page URL/ID rather than guessing.
4. Report the created page URL.

## Confluence page

Uses the connected Atlassian (Rovo) MCP tools.

1. Identify the target space. Use `getConfluenceSpaces` to list spaces (or
   `getAccessibleAtlassianResources` first if you need the cloud ID) and confirm
   which space with the author.
2. Optionally find a parent page in that space with
   `searchConfluenceUsingCql` if the RFC should nest under an existing page.
3. Create the page with `createConfluencePage`, passing the title, space, and the
   Markdown body (the tool accepts Markdown/storage format for the body).
4. Report the created page URL.

## Multiple destinations

The author may want more than one (e.g. commit the `.md` to the repo _and_
mirror it to Notion). That's fine — do each in turn from the same draft.
