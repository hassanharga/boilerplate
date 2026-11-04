# Live incident response

Use this reference when declaring or coordinating a Yassir P0/P1 incident.

## First five minutes

Everything below this card is for reading cold. This is for reading while a graph is
red. In order:

1. **Confirm impact is real and current.** One affected business flow, failing now.
   Not an alert, not a suspicion.
2. **Declare a provisional severity from impact**, not from suspected cause. Provisional
   is fine and expected; name the facts you are missing.
3. **Name one human IC** — Engineering Manager of the affected scope, else Tech Lead,
   else any senior engineer. If that is you and you are also debugging, say so out loud
   and page for help now, not later.
4. **Open `#incident-<date>-<scope>`** and put every decision there from this point on.
5. **Post the initial declaration** with confirmed impact, current status, and an
   absolute next-update time. Recovery ETA is "unknown" unless evidence supports one.
6. **Start the timeline.** Impact start, detection, declaration — with timezone.

Then work mitigation loops. Do not spend the first five minutes on root cause; a safe
reversible mitigation beats a correct diagnosis that arrives later.

## Scalable roles

| Role | Accountable for |
| --- | --- |
| Human Incident Commander | Severity, priorities, assignments, decisions, escalation, and safe resolution |
| Operations/Resolver Lead | Technical investigation, mitigation proposals, execution coordination, and verification |
| Communications Lead | Factual stakeholder updates, questions, and next-update clock |
| Scribe/Timeline | Append-only events, decisions, actions, owners, evidence links, and corrections |
| Security/Release Lead | Conditional security evidence/containment or hotfix/release workflow |

The IC owns any undelegated role, but should delegate as soon as incident size or workload
requires it. If the only responder is debugging, explicitly page help and name who is
temporarily covering command and communication.

### When you are alone

Paging for help assumes someone answers. At 02:00 that may not happen, and the failure
mode is a single tired person carrying command, comms, timeline and debugging at once.

**The bar for an irreversible action goes up, not down.** There is no second pair of
eyes, and solo plus adrenaline is exactly when an unreviewed production command gets
run. Prefer the slower reversible mitigation even when the risky one looks faster.

Say in the channel that you are solo and command is uncovered. That sentence is what
actually summons help — silence reads as "handled". Set a hard escalation timer rather
than paging once and hoping: if nobody responds within the window and impact is P0,
escalate up the chain and keep escalating.

Drop duties in this order, keeping the last ones longest:

| Drop first | Keep longest |
| --- | --- |
| Role separation and the formal state block | A minimal timestamped timeline |
| Polished stakeholder prose | One honest update cadence, stretched if needed |
| Parallel workstreams | Mitigation of customer impact |
| Side-channel mirroring (there are no side channels) | The escalation timer |

A stretched cadence you meet beats a tight one you miss — say "next update in 45
minutes" and mean it rather than promising 15 and going quiet.

The agent covers Scribe. It cannot execute anything, but it can hold the timeline,
draft the updates, and run read-only evidence passes while you work the problem.

## Shared incident state

Maintain one compact state block and update it without erasing history:

```text
Incident: <short scope>
Status: Investigating | Identified | Mitigating | Monitoring | Recovered | Resolved
Severity: <P0/P1, rationale, last reassessed time>
Times: impact start | detected | declared | mitigated | recovered | resolved (timezone)
Impact: affected flow, cohort/geography, magnitude, duration, data/safety/revenue risk
Workaround: none | description and limits
Human IC: <name/role>
Roles: Operations | Communications | Scribe | Security/Release
Current condition: <what the evidence confirms>
Hypotheses: <supported, rejected, and unknown>
Actions: <owner | action | state | next check | result>
Decisions: <timestamp | decision | evidence | risk/rollback>
Next stakeholder update: <absolute time and timezone>
Recovery criteria: <business and technical signals, window, backlog/downstream checks>
```

Timeline entries use absolute timestamps and a timezone. Record decisions and outcomes,
not a voice-call transcript. Correct an earlier entry with a new correction entry rather
than silently rewriting history.

## Mitigation loop

For each proposed production action:

1. State the condition and evidence.
2. State the proposed action, expected impact, risks, and blast radius.
3. Define rollback/abort triggers and the verification signals.
4. Obtain the required human approval and operational authorization.
5. Have an authorized responder or capability execute it.
6. Observe customer, business, and system signals; record the result and next decision.

Prefer the smallest reversible mitigation that reduces impact. Do not let pressure turn a
hypothesis into permission to change production.

## Communications

Use confirmed facts, explicit unknowns, and an absolute next-update time. Keep sensitive
security details, credentials, personal data, and exploit paths out of broad channels.

Treat the templates below as prompts, not text to copy mechanically. Adapt each update
into natural, direct prose for its audience. Remove every placeholder and internal
template label before sharing it, and do not repeat unchanged wording just to fill every
field. Product, Operations, and Business updates should be short and understandable
without engineering context; keep detailed technical evidence in the incident channel.

### Initial declaration

```text
🚨 <P0/P1> — <affected flow/region>
Impact: <confirmed users/business effect and start time>
Status: Investigating. <root cause unknown or confirmed fact>
Actions: <current containment/diagnosis>
Incident channel: #incident-<date>-<scope>
Next update: <absolute time + timezone>. Recovery ETA: <unknown or evidence-backed ETA>.
```

### Progress update

```text
<P0/P1> update — <time + timezone>
Condition: <current impact and telemetry>
Changes since last update: <new evidence/action/result>
Actions: <active mitigation and owners>
Needs/unknowns: <specific blockers>
Next update: <time>. Recovery ETA: <unknown or evidence-backed ETA>.
```

### Handoff

```text
Command handoff — <time + timezone>
Outgoing IC: <role/name>. Incoming IC: <role/name>.
Current condition/severity: <state>
Active actions and owners: <list>
Open risks/decisions/timers: <list>
Next stakeholder update: <time>
```

### Monitoring or resolution

```text
Status: <Monitoring/Resolved> — <time + timezone>
Impact: <stopped at time / no current impact>
Change: <mitigation or fix>
Evidence: <business-flow checks, telemetry, backlog/downstream state, observation window>
Residual risk/follow-ups: <owner and link, or none>
```

Publishing any message still requires explicit authorization.

## Recovery evidence

Choose a representative stability window based on the signal volume, failure mode,
deployment method, rollback time, and business cycle. Verify:

- the affected user/business flow succeeds, not only an internal health check;
- error rate, latency, saturation, and availability are normal;
- queues/backlogs drain and downstream systems remain healthy;
- no data-integrity, duplicate-processing, or delayed side effects remain;
- the mitigation or fix is fully deployed to the intended scope;
- rollback remains available during monitoring;
- residual risk and longer-term work have named owners.

## Red flags

- The main debugger is also silently carrying command, comms, and timeline duties.
- “Next update in 20 minutes” is presented as “recovery ETA 20 minutes.”
- A brief green graph is treated as recovery without business-flow validation.
- Severity stays fixed after scope or impact changes.
- Responders act in side channels without mirroring decisions to the incident record.
- A deployment, rollback, query, flag, credential, or external post is executed from
  broad instructions such as “do whatever is needed.”
- Root-cause analysis delays a safe reversible mitigation.
- A fast mitigation discards evidence needed for security, data, or recurrence analysis.
