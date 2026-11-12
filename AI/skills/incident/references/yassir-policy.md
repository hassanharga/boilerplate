# Yassir Mobility incident policy

Last verified: 2026-08-23 (read-only, against the internal Notion sources).

Re-verify when this date is more than 30 days old, and say in the output that policy
was not revalidated. Severity definitions, channels, and postmortem deadlines change;
quoting a stale rule during an incident is worse than saying you are unsure.

## Source precedence and known caveats

Primary source: [Incident Response & Post-Mortem Process](https://app.notion.com/p/2fcf03bdfe1b809b9cd0d58c45a29df7).

- Use the definitions on the incident-process page for live incidents. Its linked
  “detailed examples” destination currently opens the Mobility Repositories page and
  must not be treated as severity policy.
- Jira defect priority and live incident severity use the same P0–P3 labels but are not
  interchangeable. Defect priority can describe scheduled work; live incident severity
  describes current impact and response.
- The linked [Post-Mortem hub](https://app.notion.com/p/14bf03bdfe1b800ca97dfd0f21bf4785)
  currently contains databases rather than a seven-section document template. Use the
  seven required sections below.
- The incident page requires a postmortem the same day, maximum 48 hours. The hotfix page
  says P0 and repeated P1 hotfix postmortems may take three business days. For a declared
  incident, apply the stricter same-day/max-48-hour rule until policy owners reconcile it.
  This contradiction is unresolved policy, not a judgement call to re-make each time —
  raise it as a standing follow-up action on the postmortem so the owners reconcile the
  two pages once, rather than every responder rediscovering it under time pressure.
- Team-specific alert descriptions and the fire-drill rollout are still evolving on the
  source page. Do not present unfinished local details as universal policy.

Re-fetch the primary page before posting or creating external artifacts when possible.
If it cannot be accessed, use this cache and state that live policy was not revalidated.

## Observability and response records

- Datadog is the policy-defined primary observability source for metrics, logs, traces,
  alerts, and dashboards; GCP is used in some cases.
- Teams own monitoring and alerts for their services, APIs, and critical flows.
- Ops, Support, Product, Business, user reports, dependency status, and business KPIs can
  reveal impact even when an alert did not fire.
- The incident Slack channel is the response record and decision source of truth. Keep
  key conditions, actions, needs, decisions, owners, and outcomes there. If a workstream
  investigates elsewhere, mirror substantive updates back to the incident channel.

## Live incident severity

| Level | Current impact | Response |
| --- | --- | --- |
| P0 Critical | Complete or near-complete outage of a core business function, or similarly severe live data/operational impact | Immediate declaration, dedicated focus, organization-wide visibility |
| P1 Major | Significant degradation with high user or revenue impact, but not total outage | Immediate declaration, priority over other work, active communication |
| P2/P3 | Limited impact, effective workaround, and no immediate business risk | Normal sprint/team process, not the major-incident lifecycle |

P0 examples from the primary page include drivers unable to go online, trip creation or
acceptance broken, payments failing at scale, mass OTP/login failure, and severe live data
corruption. P1 examples include severe regional failure/latency, partial payment failure,
or a broken feature without an immediate workaround.

Use examples as anchors, not automatic classification. Quantify actual scope, duration,
workaround, and business effect. Reassess during the incident.

## Human command and channels

Exactly one human Incident Commander is required. Default selection order:

1. Engineering Manager of the affected scope.
2. Team Tech Lead.
3. Any senior engineer when neither is available.

The IC coordinates the response and is not the main debugger.

- Incident channel: `#incident-<date>-<scope>`.
- Status/announcement channel cache:
  [Yassir status channel](https://yassir-team.slack.com/archives/C0BKCKFMCRW).
- Notify relevant Ops, Product, and Business stakeholders early with severity, confirmed
  impact, current status, and an ETA only when evidence supports one.

Channel creation, invitations, calls, announcements, and updates are external writes.
Draft them by default; perform them only after explicit authorization.

## Resolution policy

The primary page considers an incident resolved when the fix is deployed, systems are
confirmed healthy, impact is absent, monitoring confirms recovery, stakeholders are
notified, and externally reported issues are closed or updated. Apply the stronger
evidence and stability contract in `live-response.md` so a transient metric improvement
is not mistaken for recovery.

## Postmortem contract

Create the document the same day, no later than 48 hours after the incident. It is
blameless and must retain all seven sections:

1. Incident summary.
2. Severity and quantified impact.
3. Timeline from detection through resolution, with timezone.
4. What went well.
5. What did not go well.
6. Technical and process root causes.
7. Clear, owned, trackable action items.

Share with involved engineering teams and relevant Product/Ops/Business stakeholders.
A standalone meeting is optional and chosen by the IC; otherwise review at the domain-wide
postmortem meeting.

Every action item must have a named owner and a Jira ticket whose component is
`Postmortem`. Prefer system guardrails over “be more careful.” The postmortem is closed
only after every action is completed.

