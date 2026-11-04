---
name: incident
description: Use when triaging, declaring, coordinating, communicating, or resolving a live Yassir Mobility production incident; classifying live P0/P1 impact; supporting a human Incident Commander; applying Yassir postmortem/Jira follow-up rules; or handling incident-related hotfix and supply-chain/security workflows. Do not use for ordinary P2/P3 backlog work or non-incident retrospectives.
---

# Yassir Mobility Incident Response

Reduce customer and business impact quickly while keeping command, communication,
evidence, and recovery decisions clear. The agent supports a human Incident Commander
(IC); it does not become the accountable IC.

## Authority and safety

- Start with read-only triage, drafts, and coordination. Incident urgency does not
  authorize Slack/Notion/Jira writes, deployments, rollbacks, production queries,
  feature-flag changes, credential rotation, or any other shared-state action.
- Perform an external or production action only when the user explicitly authorizes
  that exact scope and the repository or operational policy permits it. State the
  intended action, risk, rollback/stop condition, and verification before execution.
- Never invent impact, root cause, an ETA, recovery, or an owner. Mark unknowns and
  state the evidence needed to resolve them.
- Mitigate impact before deep causal analysis, while preserving useful evidence and
  maintaining an append-only decision/timeline record.
- Treat credentials, personal data, security indicators, and customer details as
  sensitive. Minimize and redact them in incident communications.

## Start or classify

Read [yassir-policy.md](references/yassir-policy.md) for current Yassir severity,
channels, ownership, and postmortem requirements. Re-fetch the canonical Notion policy
before any external write when a connector is available; the reference is a verified
cache, not permanent authority.

Establish these facts before asserting severity when possible:

- affected core flow and whether it is unavailable or degraded;
- affected countries/cities, user cohorts, requests, and duration;
- failure rate, latency, backlog, data-integrity, safety, privacy, and revenue impact;
- workaround quality and whether impact is continuing;
- first impact, detection, and declaration timestamps with timezone.

Use impact, not suspected root cause. A provisional severity is acceptable when time is
critical; name the missing facts and reassess whenever impact changes.

- **P0:** declare immediately for complete or near-complete loss of a core business
  function or similarly severe live impact.
- **P1:** declare immediately for significant degradation with high user or revenue
  impact but not total loss.
- **P2/P3:** do not start the major-incident process; route through normal team work.

Incident severity is not the same as Jira defect priority. A ticket labeled P1 does not
by itself prove a live P1 incident.

## Run a P0/P1 response

1. **Name one human IC.** If nobody is assigned, ask for one and identify the temporary
   human coordinator. Do not allow the sole resolver to remain overloaded without
   explicitly seeking help.
2. **Scale roles to the incident.** Assign Operations/Resolver, Communications, and
   Scribe/Timeline ownership when people are available. One person may hold multiple
   roles for a small incident, but every responsibility must have a named owner.
3. **Create the shared state.** Use the contract in
   [live-response.md](references/live-response.md): impact, severity, roles, evidence,
   hypotheses, actions, decisions, next update, and recovery criteria.
4. **Work in short mitigation loops.** Observe, propose the safest reversible action,
   name risk and rollback, obtain required authorization, execute through an authorized
   human or capability, then verify customer and system signals. Record the result.
5. **Communicate on a clock.** Draft factual updates using `live-response.md`. Give a
   next-update time even when there is no conclusion. ETA means expected recovery time;
   never substitute the update cadence for an ETA.
6. **Reassess severity and scope.** Upgrade, downgrade, split workstreams, or bring in
   additional service owners as evidence changes. Keep decisions in the incident channel
   even when responders investigate elsewhere.

For a production code/config change or security/supply-chain event, also read
[special-cases.md](references/special-cases.md) before proposing the action plan.

## Collect evidence

Datadog is the policy-defined primary observability source. Use the Datadog skills and
tools available in the current runtime — `datadog/logs`, `datadog/traces`,
`datadog/metrics`, and `datadog/visualizations` — as the default evidence path, and load
the relevant one before querying rather than guessing at query syntax mid-incident. GCP
is the documented secondary source. Fall back to whatever observability capability the
runtime exposes, and say which source a number came from.

Reading telemetry is read-only and needs no additional authorization. Running a query
against a production database is not telemetry; it is a production action.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final incident record, and every
external write stay in the main agent. If subagents are unavailable or a pass fails, run
the same passes sequentially without reducing coverage.

Here that means parallel evidence streams while you keep working the mitigation: error
rates and logs, deployment and configuration history, customer and business signals, and
downstream or dependency health. Each returns timestamped findings with links. This is
where delegation pays for itself — serial evidence gathering is the slow part of a P0.

## Recover and resolve

Do not close because one graph briefly improves. Distinguish:

- **Mitigated:** customer impact is reduced or stopped, but the system may remain fragile.
- **Monitoring:** the mitigation/fix is deployed and representative signals are under
  observation for an appropriate window.
- **Recovered:** business flows, telemetry, backlogs, and downstream systems are healthy;
  no active impact is observed.
- **Resolved:** recovery is confirmed, residual risk has an explicit owner, stakeholders
  are informed, and externally reported issues are updated as applicable.

Draft the resolution announcement only after the evidence contract in
`live-response.md` is satisfied. A hotfix may impose an additional 30–60 minute
post-deployment validation window.

## Learn and follow through

**REQUIRED SUB-SKILL:** Use `postmortem` for the document-writing craft when available,
then apply the Yassir contract in `yassir-policy.md`. If its template asset is unavailable,
use the seven-section Yassir fallback directly.

Create Jira action items only when explicitly asked. Every Yassir postmortem action has
a named owner and a Jira ticket with component `Postmortem`. The postmortem is not closed
until every action is complete.

## Reference routing

- [yassir-policy.md](references/yassir-policy.md) — read for every Yassir incident.
- [live-response.md](references/live-response.md) — read when declaring or running P0/P1.
- [special-cases.md](references/special-cases.md) — read for hotfix or security/supply-chain paths.
