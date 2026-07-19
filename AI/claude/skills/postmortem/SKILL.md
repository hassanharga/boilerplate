---
name: postmortem
description: Write a blameless incident postmortem (a.k.a. post-incident review, incident retro, RCA writeup, "we had an outage — write it up") for an engineering/ops incident. Use this whenever someone needs to document an incident after the fact — outages, degradations, data issues, failed deploys, security events — by synthesizing raw material (logs, Slack threads, alert timelines, Jira tickets, deploy history) and/or interviewing the people involved, then producing a structured Markdown doc covering summary, impact, timeline, root cause, resolution, and action items. Trigger even when the user doesn't say the word "postmortem" — phrases like "write up what happened with the outage", "document the incident from last night", "we need an RCA for the payment failure", "do a retro on the S3 incident", or "turn this incident channel into a report" all mean this skill. Markdown-first; can optionally publish to Confluence or Notion when asked. Do NOT use for project retrospectives unrelated to an incident, for live incident response while the fire is still burning, or for generic meeting notes.
---

# Incident Postmortem

Turn the messy aftermath of an incident into a clear, blameless document that helps the team understand what happened and prevents it from happening again.

## What a good postmortem is for

A postmortem is not a status report and it is not a punishment. Its real audience is a future engineer — maybe someone on the team, maybe a stranger a year from now — trying to understand a failure so they can avoid repeating it. Everything you write should serve that reader: enough context to follow the story cold, an honest timeline, a root cause that actually explains _why_ (not just _what_ broke), and action items concrete enough to file as tickets.

The single most important cultural rule is **blamelessness**. People make reasonable decisions given the information they had at the time. When someone "made a mistake," that almost always points at a system that made the mistake easy to make and hard to catch — a missing guardrail, a confusing runbook, an alert that didn't fire. Write about systems and decisions, not about who to blame. This is what makes people comfortable being honest, which is the only way you get an accurate postmortem.

## Workflow

### 1. Gather what happened

Most incidents leave a trail. Before asking the user anything, use whatever raw material they've given you or pointed you at — pasted logs, an incident Slack channel, alert/PagerDuty timelines, deploy history, Jira/Linear tickets, dashboards, git blame on the offending commit. Read it and build a mental model of the sequence of events.

Then **interview to fill the gaps.** You almost never have everything from raw material alone. Ask targeted questions rather than generic ones — the point is to close specific holes in the timeline and the causal chain. Good things to pin down if unknown:

- **Detection**: How was it noticed? Alert, customer report, someone stumbling on it? (A gap between impact-start and detection is itself a finding.)
- **Timeline anchors**: When did impact actually start (often earlier than detection)? When was it mitigated? When fully resolved? Use timestamps with a timezone.
- **Impact**: Who/what was affected and how much? Users, requests, revenue, data, SLAs. Quantify if at all possible — "checkout was down" is weaker than "~8% of checkout attempts failed for 43 minutes."
- **Root cause**: Keep asking "why" past the first answer. The first answer is usually the surface trigger ("a bad deploy"). The useful cause is a layer or two down ("the deploy passed CI because the failing case had no test, and the canary window was too short to catch it").
- **Contributing factors**: What made it worse or slower to resolve? Missing alerts, a stale runbook, unclear ownership, a noisy dashboard.
- **Recovery**: What actually fixed it? Was there luck involved? Would the same fix work next time?

Don't interrogate. Ask the few questions that matter, incorporate the answers, and ask follow-ups only where the story still doesn't hold together. If the user genuinely doesn't know something, mark it as unknown in the doc rather than inventing it — a postmortem with honest gaps is far more useful than one with confident fiction.

### 2. Find the real root cause

Resist stopping at the trigger. A useful technique is the "5 whys" — chain causes until you reach something systemic that, if fixed, would prevent a whole class of similar incidents. But treat it as a tool, not a ritual: sometimes there are multiple independent contributing causes, and forcing a single linear chain hides that. Capture the branch points honestly.

The test for a good root cause: _would fixing this have prevented the incident, and would it prevent similar ones?_ If the fix is "tell people to be more careful," you haven't found the root cause yet — you've found a symptom.

### 3. Write action items that will actually get done

Weak postmortems die in a pile of vague follow-ups. Each action item should be specific, owned, and small enough to actually complete. Prefer items that change the system (add a test, add an alert, add a guardrail, fix the runbook) over items that ask humans to try harder. Where useful, note whether each item helps **prevent** the cause, **detect** the problem faster, or **mitigate** impact — that framing surfaces gaps (e.g., you fixed the cause but detection would still take 40 minutes next time).

Keep the list lightweight — a checklist the team can scan — but make each item concrete enough to hand to someone.

### 4. Produce the document

Write to a Markdown file by default. Read `assets/template.md` for the exact structure and use it. Name the file descriptively, e.g. `postmortem-2026-07-19-checkout-outage.md`, in the current directory unless the user says otherwise.

Fill every section. If a section is genuinely unknown, keep the heading and write what's known plus an explicit "Unknown / needs follow-up" note — don't silently drop sections, because the gaps are often the most instructive part.

### 5. Publish (only if asked)

If the user wants it in Confluence or Notion, read `references/publishing.md` for how to convert and push it via the connected MCP. Default to leaving it as a local Markdown file — don't publish anywhere without being asked.

## Tone and style

- **Blameless throughout.** Name roles and systems, not individuals-at-fault. "The on-call engineer rolled back" is fine; "X broke prod" is not.
- **Concrete over vague.** Timestamps, numbers, percentages, specific service names. Quantify impact wherever the data exists.
- **Honest about the unknown.** Mark gaps as gaps. Speculation, if included, must be labeled as speculation.
- **Readable cold.** Assume the reader wasn't there and doesn't know the systems. Expand acronyms on first use; give one line of context for internal service names.
- **Tight.** This is a working document, not a novel. Every sentence should help the future reader understand or prevent the incident.
