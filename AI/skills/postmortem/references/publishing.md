# Publishing a postmortem

Read this reference only after the user explicitly asks to publish. Publication creates
shared state and notifications. Drafting a postmortem does not authorize publication,
ticket creation, announcements, or changes to the incident record.

## Authorization and destination

Before the first write, resolve:

- the final or explicitly accepted draft content;
- platform and workspace/site;
- exact parent page, database, or space;
- create a new page versus update an existing one;
- title, audience, and confidentiality level.

If these are already unambiguous in the request and available context, do not ask again.
Otherwise stop before writing and ask one focused question. Never infer update permission
from permission to create, or overwrite an existing page merely because the title matches.

A local Markdown copy is optional. Create one only when the user requests it or has already
approved a durable local artifact. Honor an explicit request to publish without creating a
local file.

## Prepare the content

Remove placeholders and internal template instructions. Preserve headings, timelines,
tables, task states, links, and code where the destination supports them; use a simpler
valid representation when it does not. Do not change facts merely to fit the platform.

Check the destination's permissions and intended audience before publishing a security,
privacy, data, or supply-chain postmortem. Keep secrets, credentials, personal data,
actionable exploit details, and unnecessary internal topology out of broadly visible pages.
Use a restricted technical appendix only when authorized and needed.

Use the semantic Notion or Confluence capability available in the current runtime. Tool
names vary across agents. If no authenticated publishing capability exists, return the
ready-to-publish content and state that nothing was published.

## Create or update safely

For a new page, search the resolved parent for an existing incident record or equivalent
postmortem before creating a duplicate. For an update, fetch the current page and preserve
material links, comments, decisions, and fields outside the authorized replacement scope.

Write once. If a timeout, connection failure, or interrupted response makes the result
ambiguous, search or fetch the target by parent, title, author, and recent creation/update
time before retrying. Retry only after confirming that the expected write did not land.

## Verify after writing

Read the result back and verify:

- platform, workspace/site, and parent;
- page identity, title, and URL;
- expected status, severity, incident date, and required sections;
- timeline and action-item content;
- no raw placeholders or unapproved sensitive detail;
- no duplicate page or unintended overwrite.

Return the verified URL or page identifier and state whether a local copy exists. If the
read-back cannot be completed, say publication is unverified rather than claiming success.
