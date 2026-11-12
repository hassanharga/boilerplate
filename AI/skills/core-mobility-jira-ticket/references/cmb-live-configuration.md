# CMB Live Configuration

Last verified: 2026-08-23 (read-only, against Jira and the metrics source).

Re-verify when this date is more than 30 days old, and say in the output that the
configuration was working from a stale cache. Field IDs, components, and required
create metadata change without notice; a stale ID produces a confusing API rejection
rather than an obvious failure.

Use these values as a cache. Confirm current create metadata before every external write. Refresh the accessible site when the cloud ID is rejected, and resolve any requested value that is absent from this table rather than guessing.

## Sources

- Jira site: `https://yassir.atlassian.net`
- Cached cloud ID: `78a96af4-a80c-47e6-ab86-975e9a422169`
- Project: `CMB` / Core Mobility
- Metrics policy: Notion page `31ff03bdfe1b80a18ae6d2953fcca865`, titled `Core squad monthly metrics guide`

## Cached IDs

| Kind       | Value            | ID      |
| ---------- | ---------------- | ------- |
| Issue type | Technical Task   | `10030` |
| Issue type | Bug              | `10004` |
| Issue type | Defect           | `10032` |
| Squad      | Core             | `11193` |
| Component  | Backend          | `10035` |
| Component  | Core             | `10346` |
| Component  | Dispatch Service | `14688` |
| Component  | LTS              | `12434` |
| Component  | Maps and Routes  | `15933` |

Current create metadata requires `components` and Squad (`customfield_10513`) for Technical Task, Bug, and Defect.

## Optional fields

- Story Points: `customfield_10026` is populated on existing CMB tickets but was not exposed in current create metadata. If requested, determine whether the connector supports it during create or requires a follow-up edit; never silently omit it.
- Story point estimate: do not substitute `customfield_10016`; current representative CMB tickets return it as null.
- Sprint: `customfield_10020`; set only when requested and after resolving the intended active sprint.
- Priority: standard `priority`; discover current allowed values. Metrics policy requires P0 or P1 for `Main` work.

Atlassian Rovo MCP is the preferred capability for live Jira reads and writes.
Tool schemas and exposed function names differ across agents, so discover the
Rovo operations by their descriptions and use the current schema for payload
shape rather than copying historical MCP names or parameters. Use an equivalent
authenticated Atlassian or Jira connector only when Rovo is unavailable.
