---
name: turn-into-skill
description: Use when the user asks to turn a completed or well-described workflow into a reusable Agent Skill, including “turn this into a skill,” “make this reusable,” or “remember how we did this.” Also use to refresh a skill's cached references against their current sources when they are stale or a review reported drift. Do not use for inventing an unperformed capability, auditing or benchmarking an existing skill, writing ordinary documentation, or saving a one-off fact.
metadata:
  short-description: Capture completed workflows as reusable skills
---

# Turn Into Skill

Convert proven work into a portable Agent Skill without losing the corrections, ordering, and
constraints that made it succeed. Harvest evidence from the actual work; do not turn one transcript
into a universal process by guesswork.

## Boundaries

Use this skill when the workflow was completed or is described with enough concrete detail to recover
its inputs, decisions, actions, and accepted output.

Also use it to refresh a skill's cached references — see [Mode 2](#mode-2-refresh-cached-references)
below. That is deliberately carved out of the "editing an existing skill" exclusion, because
a cached reference is captured knowledge going stale, which is this skill's own concern.

Route elsewhere when:

- the capability has never been performed and needs design or experimentation;
- the request is to audit, benchmark, or repair an existing skill's design;
- the user wants an RFC, PRD, runbook, README, or knowledge-base page;
- the user wants to remember a fact rather than a repeatable workflow.

If the source material is too thin to distinguish a reusable method from a one-off result, say what
is missing and ask for that evidence. Do not manufacture steps.

### Skill, learning, or fact

Three destinations, easy to confuse. Pick by whether it changes *how* the agent works, and
in how many situations:

| The thing | Where it goes | Test |
| --- | --- | --- |
| A repeatable method with inputs, ordering, and an accepted output | A skill | Would a future agent, given only this, produce the same result on a new instance of the same task? |
| A correction to how the agent should behave in this repository | `learnings.md` at the project root | Is it a rule that applies across tasks here, not a procedure for one task? |
| Something true right now — a URL, an ID, a version, a decision made | Memory or the relevant document | Is it a fact rather than a behaviour? |

A single correction is a learning; a correction that only makes sense inside a sequence of
steps is a signal that the sequence should be a skill. When the same learning has been
written three times for variations of one task, that is the skill trying to surface — say
so rather than appending a fourth.

## Mode 1: Capture a workflow

### 1. Resolve the source

Use the strongest available sources in this order:

1. the completed conversation and the user's corrections;
2. accepted artifacts, scripts, commits, reviews, or command output from that work;
3. a detailed workflow description supplied by the user;
4. current project instructions and environment evidence needed to interpret the workflow.

Re-read the source rather than relying on a summary. Record conflicts instead of silently choosing a
version. The user's later correction normally supersedes an earlier attempt, but preserve both the
final rule and the failure it prevents.

Read [references/harvest-and-safety.md](references/harvest-and-safety.md) before extracting content.

### 2. Discover instructions, roots, and collisions

Discover the current runtime's configured skill roots and applicable instruction files. Check the
repository root and relevant ancestors, not only the current directory. Depending on the runtime,
instructions may include `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, or configured
global guidance.

This user's personal skills live in `~/.agents/skills/`, one directory per skill. Check
`~/.claude/skills/` too — it is the Claude Code default and may hold plugin-installed or
older copies. Prefer the root the active runtime advertises or has already populated; when
both are populated with the same skill, resolve whether one is a symlink before treating
them as independent.

Check global and project-local skills for semantic overlap. Resolve symlinks or aliases before
treating paths as independent copies. Compare purpose, triggers, output, and constraints—not names
alone.

- If an existing skill already covers the workflow, recommend extending it and show the overlap.
- If the outcomes differ, give the new skill a discriminating name and description.
- Never overwrite or merge an existing skill without explicit approval of that exact change.

When overlap is material and the correct boundary is not already explicit, stop and ask the user to
choose extension versus a separate skill before drafting either change.

Use the runtime's canonical shared Agent Skills directory when the user requests an all-agent skill
and that directory is supported. Prefer one canonical copy with configured aliases over divergent
copies. If discovery differs across clients, explain the limitation and ask before creating aliases
or additional installations.

### 3. Harvest the reusable method

Extract only information that changes future behavior:

- the goal, inputs, and accepted output;
- non-obvious ordering and stopping conditions;
- successful commands or capabilities and why they were needed;
- user corrections, rejected approaches, and demonstrated failure modes;
- decisions that must be asked versus decisions the agent can infer;
- safety, authorization, privacy, and environment constraints;
- verification that proved the result worked.

Separate workflow invariants from instance-specific values. Parameterize repository paths, branches,
ticket IDs, service names, accounts, internal endpoints, dates, and other values that should vary.
Keep a concrete example only when it materially clarifies the method.

Do not copy every project rule into the skill. Keep portable invariants that belong to the workflow;
tell future agents to read live project instructions for rules that may change by repository.

### 4. Ask only material questions

Infer answers already present in the request or source. Ask one batched round only for gaps that would
materially change the result, such as:

- whether a demonstrated variation belongs in scope;
- whether an ambiguous decision should be automated or surfaced;
- the destination when global, project-local, and draft-only outcomes are genuinely unresolved;
- authorization for a risky step or for modifying an overlapping installed skill.

Use the user's own phrasing as trigger evidence. Do not ask them to repeat it. If they already said
“global,” “project-local,” “all agents,” or “draft only,” do not ask for the destination again.

### 5. Design the smallest useful package

Start from [assets/skill-template.md](assets/skill-template.md), adapting it to the workflow rather
than filling every optional section.

The entrypoint should contain the purpose, triggers, essential decisions, constraints, and routing to
resources. Add resources only when they pay for themselves:

- `scripts/` for deterministic logic that would otherwise be regenerated;
- `references/` for substantial conditional guidance or schemas;
- `assets/` for templates or files copied into output.

Write capability-based instructions when tool names differ across agents. Preserve an exact command
only when its interface is itself an invariant; replace environment-specific values with placeholders
and state prerequisites.

Do not require a worked example, output template, failure-mode section, or fixed number of steps when
the workflow does not need them. Assume the future agent is capable; include only non-obvious guidance.

### 6. Preserve safety and authorization

Before writing any artifact, scan the harvested material for secrets and sensitive values. Never
persist credentials, tokens, cookies, private keys, personal data, or live secret-bearing commands.
Sanitize or parameterize internal URLs, identifying local paths, account IDs, and production targets
unless the user explicitly requires them and the destination is appropriate.

Authorization from the original task is not standing authorization for future runs. If the captured
workflow contains external, destructive, production, publishing, or shared-state actions, place a
confirmation gate immediately before that action.

The request to “turn this into a skill” authorizes creating a draft. It also authorizes installation
when the destination is explicit and no existing skill will be overwritten. Otherwise stage the
package, show the destination or diff, and obtain confirmation before installation or replacement.
Never publish, push, or distribute the skill externally without separate authorization.

### 7. Draft, validate, and evaluate

Create the package in a safe writable staging location when installation could overwrite existing
state or the destination is not writable. Validate before installation.

Read [references/evaluation.md](references/evaluation.md) and apply the checks proportionate to the
skill. At minimum:

- validate against the current Agent Skills specification or the active runtime's current validator;
- check realistic positive and near-miss triggers;
- perform a zero-context read-through;
- test bundled scripts according to the target repository's policy;
- run compact fresh-agent behavioral evaluations for a substantial or risky skill, or when the user
  asks for testing.

Do not impose 100% unit-test coverage on every repository. Preserve an explicit repository or
acceptance-criteria coverage requirement when one exists; otherwise use focused behavior tests for
changed scripts and fresh-agent evaluations for instructions.

When the runtime supports subagents and the work splits into independent read-only passes,
delegate. Give each subagent a disjoint scope and the same evidence standard, and require it to
return findings with sources — never decisions, conclusions, or writes. Reconciliation, conflict
resolution, the final package, and every external write stay in the main agent. If subagents are
unavailable or a pass fails, run the same passes sequentially without reducing coverage.

Here that means a fresh evaluator per behavioral scenario. Give it the staged skill, a realistic
scenario, and only the raw artifacts it needs — never the intended answer, and never permission to
write externally. Package design, interpretation of the evaluation, corrections, installation, and
reporting stay with the main agent. When no fresh evaluator is available, run the strongest
isolated checks instead — positive and near-miss triggers, a zero-context read-through, scenario
walkthroughs, validators, focused script tests — and state plainly that independent fresh-agent
behavior was not verified. Do not block a safe installation over it.

### 8. Install and report

After validation, install only at the approved destination. Re-read or revalidate the installed copy
so the report is based on what agents will actually load.

Report in plain language:

- skill name and installed or draft path;
- what was harvested and what was deliberately parameterized or omitted;
- collisions or portability limitations;
- structural, script, trigger, and behavioral evaluation results;
- how the active runtimes discover or reload it.

Do not promise that every runtime sees the skill immediately unless that was verified.

## Mode 2: Refresh cached references

A skill that caches anything external — a policy summary, a page ID, a schema, a config
snapshot, a framework convention — starts drifting the moment it is written. Refreshing it
is a separate job from capturing a workflow, and it is deliberately kept out of every other
skill: a review or an incident reports drift and keeps going, it never stops to fix the
skill.

### Triggers

- **On request.** The user asks to refresh a skill, or a review, incident, or audit left a
  `Guidance:` line reporting that cached guidance conflicted with current evidence.
- **On schedule.** Monthly, matching the 30-day rule the dated references themselves carry.
  A skill with a `Last verified` header older than 30 days is due; one whose sources change
  rarely can be marked with a longer interval in the reference itself.

Scheduling belongs to the runtime, not to this skill. In Claude Code that is a cron entry
invoking this skill against the named skill directory; elsewhere use whatever the runtime
offers, or run it by hand. Do not create a schedule without asking — a recurring job that
edits skill files is a standing authorization the user should grant deliberately.

### 1. Find what is actually cached

For the named skill, list every claim that came from somewhere else and could have moved:

```bash
rg -n 'Last verified|last verified' ~/.agents/skills/<skill>/
```

Then read the references themselves. Cached content is not always dated — page and database
IDs, cloud IDs, custom field IDs, endpoint hostnames, severity tables, required-section
lists, deadlines, schema property names, and version-pinned framework claims are all cached
whether or not anything says so. Build the list before fetching anything, so the fetch pass
is one round rather than a trickle.

### 2. Re-fetch from the source of record

Each cached claim names, or should name, where it came from. Fetch that source — not a
search result that looks similar. If a reference does not name its source, that is itself a
finding: record it and propose adding the source line, because an unattributable claim can
never be refreshed, only re-guessed.

When a source is unreachable, say so and leave the cached value alone with its old date.
Never quietly re-date content that was not actually verified — a fresh date on unverified
content is worse than a stale date on verified content, because it disarms the next check.

Delegate here when the skill caches from several independent sources. One subagent per
source, each returning what the source currently says with a link and a fetch time — never
a decision about what the skill should say. Reconciliation and every write stay with the
main agent.

### 3. Apply mechanical, propose substantive

| Kind of drift | Action |
| --- | --- |
| The source still says what the cache says | Update the `Last verified` date. No other change. |
| An identifier moved, a name changed, a link redirects, a value was reformatted | Apply it, then list what changed in the report. |
| A rule changed, a deadline moved, a section was added or removed, a convention was replaced | Propose the edit with both texts side by side and wait. |
| The source contradicts itself, or two sources disagree | Do not resolve it. Record the conflict as a standing follow-up, the way the incident policy handles its own unresolved contradiction. |
| The cached content no longer exists at the source | Propose removal, and say what the skill will no longer be able to do. |

The dividing line is whether the change alters what a future agent would *do*. A moved page
ID does not; a changed deadline does. When unsure, treat it as substantive — an unrequested
behaviour change buried in a maintenance pass is exactly the failure this split prevents.

### 4. Report

Name the skill, each reference touched, what was confirmed unchanged, what was applied
mechanically, what is proposed and awaiting a decision, what could not be reached, and the
new verification dates. A refresh that found nothing is a useful result: say the dates moved
and nothing else did.

## Failure handling

- **Insufficient source:** stop and request the missing transcript, artifact, or decisions.
- **Conflicting corrections:** show the conflict and ask which behavior should govern.
- **Sensitive source:** sanitize first; if safe generalization would remove essential meaning, stop.
- **Overlapping skill:** propose an extension or a clearly separated trigger; do not create a quiet
  duplicate.
- **Unavailable validator or evaluator:** perform the strongest available checks and state exactly
  what was not verified.
