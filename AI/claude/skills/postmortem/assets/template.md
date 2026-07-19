# Postmortem: [Short incident title]

|                      |                                       |
| -------------------- | ------------------------------------- |
| **Date of incident** | YYYY-MM-DD                            |
| **Authors**          | [names]                               |
| **Status**           | Draft / In review / Final             |
| **Severity**         | [e.g. SEV1 / SEV2 / SEV3]             |
| **Duration**         | [impact start → resolved, total time] |

## Summary

Two to four sentences a busy reader can absorb in fifteen seconds: what broke, who it affected, how long it lasted, and what the underlying cause was. Someone should be able to read only this section and understand the incident.

## Impact

What was affected and by how much. Quantify wherever the data exists — users affected, requests failed, error rate, revenue, data loss, SLA/SLO breach. Include what was _not_ affected if that helps bound the blast radius.

- **User impact:** …
- **Scope / duration:** …
- **Data impact:** … (or "none")

## Timeline

All times in [timezone]. Note the gap between impact-start and detection — it's often a finding in itself.

| Time  | Event                                             |
| ----- | ------------------------------------------------- |
| HH:MM | [Impact begins — often before anyone noticed]     |
| HH:MM | [Detection — alert fired / customer reported / …] |
| HH:MM | [Investigation milestones]                        |
| HH:MM | [Mitigation applied]                              |
| HH:MM | [Full resolution]                                 |

## Root cause

Explain _why_ this happened, not just _what_ broke. Walk the causal chain down to something systemic. If there were multiple contributing causes, describe each rather than forcing a single line. Keep it blameless — focus on the systems and decisions, not individuals.

## Contributing factors

Things that made the incident more likely, worse, or slower to resolve (missing alerts, stale runbook, unclear ownership, gaps in monitoring). Optional if there were none, but there usually are.

## Resolution

What actually stopped the bleeding, and whether it's a durable fix or a temporary mitigation. Note if luck played a role or if the same fix would work next time.

## What went well / what went poorly

A short honest reflection. What in the response worked (good alerting, fast rollback) and what didn't (took too long to detect, unclear who owned it). This is where the team learns, not just about the bug but about the response.

## Action items

Concrete, owned follow-ups. Prefer changes to the system over "be more careful." Tag each with whether it helps **prevent**, **detect**, or **mitigate** where useful.

- [ ] [Action] — Owner: [name] — [prevent/detect/mitigate]
- [ ] …

## Lessons learned

The one or two takeaways worth remembering even after the action items are closed — the generalizable insight a future engineer would benefit from.
