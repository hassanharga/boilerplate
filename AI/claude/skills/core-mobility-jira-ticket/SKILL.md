---
name: core-mobility-jira-ticket
description: Use when creating or drafting Jira tickets for Yassir Core Mobility, especially CMB tickets for Core squad work, Dispatch Service, LTS, Maps and Routes, Backend, bugs, defects, or work that must align with Core squad monthly metrics.
metadata:
  short-description: Create CMB tickets with Core squad conventions
---

# Core Mobility Jira Ticket

Use this skill when the user asks to create, prepare, draft, split, or polish a Jira ticket for Core Mobility work.

## Source Context

- Jira site: `https://yassir.atlassian.net`
- Cloud ID: `78a96af4-a80c-47e6-ab86-975e9a422169` (pass as `cloudId` to every Atlassian MCP tool). If a call rejects it, refresh with `getAccessibleAtlassianResources`.
- Project: `CMB` / Core Mobility
- Metric guidance source: `Core squad monthly metrics guide` in Notion, page `31ff03bdfe1b80a18ae6d2953fcca865`
- Observed ticket examples: `CMB-38544`, `CMB-38547`, `CMB-38548`, `CMB-38549`, `CMB-38552`, `CMB-38553`, `CMB-38560`

## MCP Tooling

Create and edit tickets through the Atlassian Rovo MCP (no `curl`, no web UI):

- `mcp__claude_ai_Atlassian_Rovo__createJiraIssue` — create. Takes `cloudId`, `projectKey: "CMB"`, `issueTypeName`, `summary`, `description` (`contentFormat: "markdown"`). All other fields go in `additional_fields`.
- `mcp__claude_ai_Atlassian_Rovo__editJiraIssue` — update an existing ticket; custom/standard fields go in `fields`.
- `mcp__claude_ai_Atlassian_Rovo__getJiraIssue` — read current state before editing (preserve artifacts, see Description Style).
- `mcp__claude_ai_Atlassian_Rovo__getJiraProjectIssueTypesMetadata` / `getJiraIssueTypeMetaWithFields` — re-confirm an id only if a create/edit call is rejected on a field. Don't fetch metadata pre-emptively; the ids below are verified.
- `mcp__claude_ai_Atlassian_Rovo__searchJiraIssuesUsingJql` — find related/duplicate tickets or active sprints.
- `mcp__claude_ai_Atlassian_Rovo__getTransitionsForJiraIssue` — only if asked to move status.

Field payload shape for `additional_fields` (create) / `fields` (edit):

```json
{
  "customfield_10513": { "id": "11193" },
  "components": [{ "id": "10035" }],
  "customfield_10026": 3
}
```

Select fields (`Squad`) take `{ "id": "..." }`; `components` take an array; `Story Points` is a bare number.

## Required Jira Fields

- `project`: `CMB` / Core Mobility.
- `summary`: use `[Core][<service-or-area>]: <title>`.
- `issuetype`: default to `Technical Task` for implementation work.
- `Squad` / `customfield_10513`: **required**. Set to `Core` unless the user explicitly says otherwise.
- `components`: **required**. Set the owning service/platform component. Use exactly the component category needed for metrics classification.
- `Story Points` / `customfield_10026`: use for estimates. Do not use `Story point estimate` / `customfield_10016` (not available on these issue types).
- `Sprint` / `customfield_10020`: do not set unless the user asks. See Creation Workflow step 7.

Verified option/component ids (CMB, confirmed against live metadata):

| Field      | Value              | Id      |
| ---------- | ------------------ | ------- |
| Squad      | `Core`             | `11193` |
| Component  | `Backend`          | `10035` |
| Component  | `Core`             | `10346` |
| Component  | `Dispatch Service` | `14688` |
| Component  | `LTS`              | `12434` |
| Component  | `Maps and Routes`  | `15933` |
| Issue type | `Technical Task`   | `10030` |
| Issue type | `Bug`              | `10004` |
| Issue type | `Defect`           | `10032` |

The component is literally `Maps and Routes` (spelled out, no ampersand). If an id is missing here, fetch it with `getJiraIssueTypeMetaWithFields` before creating.

## Summary Style

Format:

```text
[Core][<service-or-area>]: <imperative title>
```

Examples:

```text
[Core][DES]: Implement candidate attribute update persistence
[Core][LTS]: implementation for secondary datasource
```

Use a concise service/area tag that matches the work context, such as `DES`, `LTS`, `Maps and Routes`, or `Backend`.

## Metrics Classification

Before creating the ticket, classify the work for Core squad monthly metrics:

- `Tech`: technical roadmap work. Use component `Backend`. Do not combine `Backend` with other service components.
- `Prod`: product or microservice feature work. Use a non-Backend component such as `Dispatch Service`, `LTS`, or `Maps and Routes`.
- `Main`: production maintenance. Use issue type `Bug` or `Defect` and priority `P0` or `P1`.

Rules from the metrics guide:

- Each team member's work should have a unique Jira ticket created and updated promptly.
- Each ticket should have either `Backend` or another component, but not both.
- Renovate review tickets count as `Prod`, not `Tech`, unless the user explicitly ties them to the technical roadmap.

If the category is ambiguous, infer from the work description when low risk. Ask a short clarification only when the component choice would materially affect metrics.

## Description Style

Prefer this structure for implementation-ready tickets:

```markdown
## Description

<One concise paragraph describing the work and target behavior.>

## Acceptance criteria

- <Observable criterion>
- <Observable criterion>
- <Contract, persistence, integration, or rollout constraint when relevant>
```

Keep acceptance criteria field-oriented and testable. Mention unchanged contracts explicitly when relevant.
When a requirement needs only a subset of available records, encourage fetching the already filtered and sorted result from the datastore instead of loading a broad result set and filtering it in application memory.

When enhancing or rewriting an existing ticket, preserve existing artifacts unless the user explicitly asks to remove them. Before updating a description, inspect the current description and carry forward:

- links to Notion pages, docs, diagrams, spikes, PRs, or external references
- inline schemas, payload examples, code blocks, tables, and sample data
- implementation notes, open questions, datasource considerations, and migration/rollout notes
- user-authored constraints that are not superseded by the requested change

If the cleaned structure needs to move these items, keep them under explicit sections such as `## Source artifact`, `## Storage sketch`, `## Implementation note`, or `## Open questions`. Do not replace the whole description with only `Description` and `Acceptance criteria` when doing so would discard useful source context.

## Creation Workflow

1. Identify category: `Tech`, `Prod`, or `Main`.
2. Select issue type:
   - `Technical Task` for normal implementation work.
   - `Bug` or `Defect` for `Main` work.
3. Select exactly one component category:
   - `Backend` for `Tech`.
   - Service/platform component for `Prod`.
   - Relevant production area component for `Main`.
4. Build the summary with `[Core][<service-or-area>]: ...`.
5. Set `Squad` to `Core` (`customfield_10513: { "id": "11193" }`).
6. Set `Story Points` via `customfield_10026` if the user gives an estimate.
7. Do not hard-code sprint values. If the user asks to add the ticket to a sprint, find the active sprint via `searchJiraIssuesUsingJql` / sprint metadata first, then set `customfield_10020`.
8. Create with `createJiraIssue` (`projectKey: "CMB"`, `cloudId`, `issueTypeName`, `summary`, `description` as markdown, everything else in `additional_fields`). To enhance an existing ticket, `getJiraIssue` first, then `editJiraIssue`.
9. Report the created/updated issue key and URL back to the user.
