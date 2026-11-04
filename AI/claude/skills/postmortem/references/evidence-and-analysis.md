# Evidence and causal analysis

Use this reference before drafting any postmortem.

## Build an evidence map

Organize incident material into five states:

| State | Meaning | Writing rule |
| --- | --- | --- |
| Confirmed | Directly supported by a reliable source | State as fact and retain a useful link or identifier |
| Estimated | Derived from bounded data or calculation | Label the estimate, method, and time window |
| Inferred | Best explanation supported by several facts | Label the inference and what would confirm it |
| Unknown | Material fact is not available | State the gap and the evidence or owner needed |
| Conflicting | Sources disagree | Preserve both accounts until an authoritative correction is established |

Useful sources include incident records, append-only timelines, alerts, dashboards, logs,
traces, deployment and configuration history, feature-flag changes, code and tests, pull
requests, tickets, customer reports, and responder interviews. Source availability does
not make every statement in it correct. Prefer direct system evidence for timestamps and
measured impact, while retaining human context for decisions and observed symptoms.

When a source is corrected, keep the final document internally consistent and mention the
correction when it changes duration, severity, impact, or causal conclusions.

Missing or unavailable evidence is a limitation, not automatically a cause. Call it a
technical, process, detection, or response gap only when evidence shows that the limitation
changed the incident or its handling.

## Reconstruct time and impact

Use one explicit timezone. Track impact start, detection, declaration, mitigation,
recovery, and resolution separately because they answer different questions. Calculate
customer-impact duration from impact start to verified recovery, not detection to closure.

Quantify only what the evidence supports. Record query windows, cohorts, regions, traffic
coverage, and exclusions that affect an estimate. Distinguish "no impact found in the
checked scope" from "no impact occurred."

## Build the causal model

Start with the observable failure, then trace backward through the relevant system and
decision conditions. A useful model normally distinguishes:

1. the initiating event or trigger;
2. technical mechanisms that produced customer impact;
3. process or design conditions that allowed the mechanism;
4. controls that failed, were absent, or behaved as designed but were insufficient;
5. detection, mitigation, coordination, and recovery factors.

Try to disprove each causal claim against alternate explanations, safeguards, tests,
versioned behavior, and deployment evidence. Correlation with a deployment is not proof
that the deployment caused the incident. Do not force a single root cause when independent
conditions combined.

Five Whys can help uncover a deeper condition, but it is not a required ceremony and it
does not prove causality. Stop when the evidence ends, not when the document has a neat
story.

## Turn evidence into actions

Map each proposed action to a cause, contributing condition, or response gap. Reject vague
items such as "improve monitoring" or "be more careful." An action should state:

- the concrete deliverable;
- the reliability, security, or response property it establishes;
- an observable acceptance check, including a negative case when applicable;
- accountability fields required by current policy;
- whether it prevents, detects, or mitigates recurrence.

Do not generate one action per paragraph merely to make the document look complete.
Prioritize the smallest set that materially changes recurrence probability, detection
time, blast radius, or recovery time. Do not force representation of every
prevent/detect/mitigate category. When an idea depends on an unconfirmed control gap, keep
it as a candidate for validation rather than presenting it as an agreed action.

Prefer outcome requirements over speculative implementation. A symptom involving retries,
timeouts, identity, access, or another protocol does not by itself prove the correct key,
scope, threshold, algorithm, or mechanism.

## Security and sensitive incidents

Separate the broadly shareable learning document from details that could enable abuse or
expose secrets, personal data, customer data, or confidential topology. Preserve enough
information to explain the failed boundary and corrective action. Place restricted details
in an authorized location and link them only when audience and access are appropriate.

Never reproduce credentials, tokens, private keys, full sensitive payloads, or unnecessarily
weaponized exploit steps in the postmortem.

Do not verify rotation or revocation by attempting to use an exposed credential. Use
authorized provider, secret-manager, configuration, or audit evidence instead.
