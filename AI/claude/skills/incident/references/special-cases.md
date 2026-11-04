# Incident special cases

Read only when the response includes a production hotfix or a security/supply-chain event.
The sources below were verified read-only on 2026-08-23.

## Production hotfix

Source: [Hotfix Management](https://app.notion.com/p/349f03bdfe1b8035a88cf7513fbb92fb).

Hotfixes apply to urgent P0/P1 production code, mobile, frontend, backend, configuration,
or security changes. P2/P3 use the normal release path unless the authorized engineering
leader approves an escalation.

Before proposing deployment, require:

- a tracking item with severity, impact, minimal fix approach, risk/test plan, and rollback;
- an IC/engineering lead and QA decision that hotfix—not normal release—is appropriate;
- a minimal change set without unrelated refactoring;
- targeted tests where feasible, or a documented exception plus follow-up;
- at least one code-owner/senior review, QA sign-off or documented extreme-emergency
  exception, and EM/Staff sign-off for P0;
- staging verification by default, or documented gaps and compensating controls such as
  canary, feature flag, and additional monitoring;
- a deployment owner, release communication, dashboards, and rollback triggers.

After deployment, validate for 30–60 minutes using the affected flow and primary KPIs,
then close or downgrade only when evidence supports it. Forward-merge/backport the fix to
all active branches within 24 hours, maximum 48, and track that completion so the defect
is not reintroduced.

The hotfix page says P0/repeated-P1 postmortems may take three business days. A declared
incident follows the stricter same-day/max-48-hour incident policy until Yassir resolves
the inconsistency.

Branching, deployment, merge/backport, Slack release announcements, and Jira mutations are
shared-state actions. Draft the plan by default and execute only with explicit approval.

## Security and supply-chain incident

Source: [Security Incidents](https://app.notion.com/p/348f03bdfe1b81049611c60f5f53a60f).

This branch applies when an advisory, compromised dependency/build path, credential
exposure, artifact tampering, or related security event affects Mobility engineering.
Do not publish sensitive indicators, credential details, exploit paths, or unverified
claims to broad status channels.

Current Yassir lifecycle:

1. **Declared:** triage the advisory/event, name the IC, and create a dedicated child page.
2. **In flight:** name Champions/workstream owners; maintain the Exposure Inventory
   database daily; archive the Slack kickoff and key decisions.
3. **Closeout:** confirm every production repository/artifact is on the fixed or trusted
   version, complete the postmortem, and track Jira actions.
4. **Archived:** retain the page for institutional memory and update the runbook with
   reusable lessons.

The incident record should include:

- governance: IC, Security lead, Champions, review policy, and communication mode;
- advisory/event identity and verified affected ranges or indicators;
- exposure inventory: repository/service, owner, resolved version/artifact, environment,
  build/runtime reachability, credential/data access, containment, fix, production status,
  evidence, and last update;
- workstreams for containment, credentials/IAM, build provenance, affected services,
  monitoring/forensics, communications, and recovery;
- an append-only decision and evidence register with access restrictions;
- unknown or unassessed entries labeled as such—never “safe.”

Contain first when credible: pause suspect build/release paths where authorized, isolate
artifacts/runners, restrict credentials, and preserve logs/evidence. Credential validation,
rotation/revocation, pipeline changes, quarantines, and production rebuild/redeploy actions
require explicit authorization and approved security/operations handling.

Close only when affected production artifacts are trusted/fixed, exposed credentials are
rotated/revoked or proven unaffected, monitoring shows no ongoing unauthorized activity,
core flows are healthy, residual risk is explicitly owned, and required legal/privacy or
external-notification decisions have been made by authorized people.

