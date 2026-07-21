# Yassir Mobility — concrete incident facts

Source of truth: [Incident Response & Post-Mortem Process](https://app.notion.com/p/2fcf03bdfe1b809b9cd0d58c45a29df7) (Notion). This file mirrors the concrete, actionable pieces; when in doubt, re-read the source page.

## Observability

- **Datadog** is the single source of truth: metrics, logs, traces, alerts, dashboards. (GCP in some cases.)
- Each team owns monitoring for its own services, APIs, and critical flows, and owns its alerts. Ownership rule: _if you own the service/scope, you own its alerts._

## Severity levels

Only **P0** and **P1** trigger the incident process. **P2/P3** are handled in normal sprint planning.

### 🔴 P0 — Critical

Complete or near-complete outage of a core business function. Examples (Mobility/Delivery):

- Drivers cannot go online
- Trip creation or acceptance is broken
- Payments failing at scale
- Mass login failures (OTP problems)
- Severe data corruption impacting live operations

Expectations: immediate response, dedicated focus until resolved, organization-wide visibility.

### 🟠 P1 — Major

Significant service degradation with high user/revenue impact, but not a total outage. Examples:

- High failure rate in a specific country or city
- Severe latency affecting matching or pricing
- Partial payment failures
- Feature broken with no immediate workaround

Expectations: immediate response, prioritized over all other work, active communication.

### 🟡 P2 / 🟢 P3 — Non-incident

Limited impact, workarounds exist, no immediate business risk → normal sprint planning.

## Incident Commander (IC)

There must always be **exactly one IC**. Default selection order:

1. Engineering Manager of the affected scope
2. Tech Lead of the team
3. Any senior engineer if no TL is present

The IC **runs** the incident and is **not** the main debugger. Responsibilities: declare the incident (P0/P1); create the temporary Slack channel; invite required participants; post the announcement to the status channel; start a live call if needed; assign clear tasks; keep comms flowing; track decisions + timeline; ensure focus on recovery.

## Communication

- **Incident channel:** `#incident-<date>-<scope>` — the single source of truth during the incident. Short, factual updates. No side discussions outside the channel.
- **Status / announcement channel:** https://yassir-team.slack.com/archives/C0BKCKFMCRW — notify Ops/Product/Business early with severity, impact, current status, and ETA (if available).

### Announcement template (initial)

> 🚨 Hey team, we are facing an issue in **XXX** and the team is looking into it. For more details you can join the incident channel `#incident-<date>-<scope>`.

Share early even without full detail. Silence creates anxiety — "We're investigating" is better than no update.

## Resolution criteria

An incident is resolved when: the fix is deployed, systems are confirmed healthy (monitoring confirms recovery), and impact is no longer present. Then: announce resolution in the incident channel, notify stakeholders, close/update any externally reported issues.

## Post-mortem

- **Template:** [Yassir Post-Mortem template](https://app.notion.com/p/14bf03bdfe1b800ca97dfd0f21bf4785) (Notion). Lightweight & standardized.
- **Timing:** create the document the same day, max within 48 hours.
- **Required sections:** 1) Incident summary; 2) Severity & impact; 3) Timeline (detection → resolution); 4) What went well; 5) What didn't go well; 6) Root causes (technical & process); 7) Action items (clear, owned, trackable).
- **Sharing:** share with involved engineering teams and, when relevant, Product/Ops/Business. Transparency is mandatory.
- **Meeting:** optional standalone meeting, IC decides; otherwise covered in the domain-wide post-mortem meeting at the end of each sprint.

### Action-item tracking

- Each action item must have an **owner** and be linked to a **Jira ticket with component = `Postmortem`**.
- Postmortem board (reviewed every domain-wide incident meeting): https://yassir.atlassian.net/jira/software/c/projects/CMB/boards/2021
- The post-mortem is **closed/done only when all action items are completed.**

## Appendix (related processes)

- [Hotfix Management](https://app.notion.com/p/349f03bdfe1b8035a88cf7513fbb92fb)
- [Security Incidents](https://app.notion.com/p/348f03bdfe1b81049611c60f5f53a60f)
- [Runbooks](https://app.notion.com/p/348f03bdfe1b81b4ac17f94d6cea1407)
- [Critical Dependency Change Strategy](https://app.notion.com/p/356f03bdfe1b81bd82f2ec83fd61c0ff)
- [Fire Drill](https://app.notion.com/p/3a3f03bdfe1b807485d4c6faafa20498)
