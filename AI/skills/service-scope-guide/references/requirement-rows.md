# Functional requirement rows

Last verified: 2026-09-30, against the blank template's database template, the Dispatch database
and template, and Dispatch rows such as `EN-12 … (v2)`. Fetch the target database's live template
before writing; it wins over this file.

## Contents

- [What one row is](#what-one-row-is)
- [Properties](#properties)
- [Naming and IDs](#naming-and-ids)
- [Body structure](#body-structure)
- [Writing the story](#writing-the-story)
- [Writing scenarios](#writing-scenarios)
- [Versioning an existing requirement](#versioning-an-existing-requirement)
- [Reviewing rows](#reviewing-rows)

---

## What one row is

One row is one capability with an observable outcome, something a stakeholder could accept or
reject by watching the service's behavior. Split a row that bundles unrelated behaviors. Merge
rows that describe one behavior from two angles. A row is not a task, a ticket, or a component;
those live in Jira and the Design Guide.

## Properties

Always read the live schema. Typical properties:

| Property | Type | Notes |
| --- | --- | --- |
| `Name` | title | The requirement title; see naming below. |
| `Status` | status | Blank template: `Not Ready`, `Ready`, `In progress`, `Released`. Dispatch adds `Closed`; Location adds `Out of scope`. |
| `Version` | text | `v1.0`, `v2.0`. Live rows also use `v1` and `v2`; match the guide's existing style. |
| `JIRA Ticket` | url | The ticket or epic this requirement is delivered through. Leave empty rather than guessing. |
| `ID` | auto-increment | System-managed. Never set it. It is not the `EN-12`-style ID in the title. |
| `Area`, `Sub-Area` | select | Dispatch only. Use existing options; do not create a new option for a spelling variant. |
| `Priority` | select | Dispatch only: `High`, `Medium`, `Low`. A team decision. |
| `Planned Milestone` | text | Dispatch only, for example `M1` or `Future`. A team decision. |
| `Summary` | text | Dispatch only. Two or three sentences on what the requirement delivers, optionally with "Example: …". |

Status meaning as used in the live guides: `Not Ready` means still being shaped; `Ready` means agreed
and ready to build; `In progress` means being built; `Released` means live; `Closed` means done or
retired in Dispatch; `Out of scope` means explicitly excluded (Location). Only the team moves a
row forward. The agent may **report** that a status looks wrong, with evidence. For example, a
`Not Ready` row whose behavior is already in production code, or a `Released` row with no
implementation found.

## Naming and IDs

Follow the guide's existing convention. Dispatch uses `<PREFIX>-<n> — <Title>` with an em dash, and
the prefix tracks `Area`:

| Prefix | Area |
| --- | --- |
| `EN-` | 01 Engine |
| `EDB-` | 02 EDB Platform |
| `GOV-` | 03 Governance |
| `EDBC-` | 04 EDBs Catalog (zero-padded: `EDBC-07`) |
| `DA-` | 05 Data (zero-padded: `DA-01`) |

A **requirement's identity is its ID plus its version**: `EN-12` v1 and `EN-12 (v2)` are two
versions of one requirement, not a duplicate. Versions share the ID and may have different titles.
Dispatch has `EN-5 — Resolve Variant` and `EN-5 — Select Experiment Variant (v2)`. A new
*capability* takes the next number after the highest ID already used in its prefix; count each ID
once, whatever its versions. Query all rows first, because gaps and older unprefixed rows exist.
Never reuse a number for a different capability. Match the prefix's zero-padding. A few live titles use a hyphen instead of the em dash (`EDBC-27 - …`); use
the em dash for new rows and report the inconsistency rather than renaming.

Guides without a prefix convention (Location, blank template) use a plain title such as
`Place New Order`. Do not introduce prefixes there unless the user asks.

Titles are short verb phrases describing the capability: `Resolve Strategy`,
`Filter Candidates by ETA`. Not `Strategy stuff` or `Implement StrategyResolver`.

## Body structure

The database template (Dispatch `2edf03bdfe1b8111a8dbe1f8c765450f`, locked) has:

1. Gray `📌` callout: "This is part of the functional requirements described in <Scope Guide
   mention> of <service mention>."
2. Blue `💡` callout reminding the editor to update the title and properties.
3. `# 1. Story`: a blue `💡` explainer with the story syntax and an example, then a gray `📝`
   callout holding the story itself.
4. `# 2. Scenarios`: a blue `💡` explainer with a collapsed example, then one
   `## 2.n. <Scenario Title> {toggle="true"}` per scenario, each holding a Given/When/Then table.
5. `# 3. Appendices`: `3.1 Related Links` and `3.2 Out of Scope`, each with a blue `💡` prompt.

Mature rows adapt this. `EN-12 (v2)` drops the blue editor callouts once filled. It adds
`# 2. Behavior in scope` as a bullet list of the rules before the scenarios, which become
`# 3. Scenarios`. It ends with `# 4. Related sources`. Adding "Behavior in scope" is good practice
when a requirement has several rules the scenarios exercise. Otherwise follow the template.

Some areas use their own body layout. In Dispatch, `04 EDBs Catalog` rows (`EDBC-`) have a plain
Story sentence, then a `Scope Schema` toggle (sources, dependencies, validation and diagnostics
bullets) and a JSON interface block (`metadata`, `inputs`, `parameters`, `outputs`); several have
no scenarios. For a new or versioned row, **follow the layout of neighboring rows in the same Area**.
Suggest adding scenarios where they are missing, without imposing the full template.

Create rows from the database template whenever the connector supports templates, then fill its
placeholders. Do not leave template prompts such as `<Role>` or `<Scenario Title>` in completed
content.

## Writing the story

```
As a    <real actor>
I want  <capability>
So that <benefit to that actor or the business>
```

The template uses "I would like to"; live rows also use "I want to". Match the guide.

- The actor is a real role for this service: a client system submitting Dispatch Requests, Ops, the
  Core team, a driver, a rider. Avoid "As a system" or "As a developer" unless that really is the
  consumer.
- The benefit is the reason the requirement exists. If no source states it, ask; do not invent one.

## Writing scenarios

Each scenario table has a header column and colored rows:

| Row | Color | Content |
| --- | --- | --- |
| `GIVEN` / `AND` | `red_bg` | Initial state or context. |
| `WHEN` | `orange_bg` | The single action or event. |
| `THEN` / `AND` | `green_bg` | The observable outcomes. |

The template also has blank spacer rows between blocks; mature rows drop them. Either is fine; match
the guide.

Rules that make scenarios useful:

- **At least a success path and a failure path.** Add edge cases that change the outcome, such as
  duplicates, timeouts, missing data, or concurrency. Do not pad with near-copies.
- **One `WHEN` per scenario.** Two actions mean two scenarios.
- **Observable outcomes only.** Name what a caller, consumer, or operator can see: a response, a
  published message, a state visible through the API, or a field in the Decision Envelope. "The
  service calls `StrategyRepository.find`" is implementation, not an outcome.
- **Exact contract names are allowed** when they are part of the agreed external contract. For
  example, `metadata.execution.triggering.strategyMode` in an envelope is observable. Format them
  as code.
- **Use glossary terms** in the glossary's capitalization (Dispatch Request, Pool Key, Strategy).
- **Titles describe the situation:** "AUTO failure falls back safely", not "Scenario 7".
- Keep numbers the team agreed on. Where a threshold is undecided, say so in the row rather than
  choosing one.

## Versioning an existing requirement

When the behavior of an agreed requirement (`Ready`, `In progress`, `Released`, or `Closed`)
changes, **do not rewrite it in place.** People built against it, and the old row is the record of
what was agreed. Instead:

1. Find the latest existing version of the requirement: the highest `(vN)` suffix or `Version`
   among rows with that ID. Build on that version, not on v1.
2. Create a new row titled `<same ID> — <Title> (vN+1)` (the title may be updated), `Version`
   `vN+1.0` in the guide's version style, with the same `Area`/`Sub-Area`.
3. Replace the first gray callout with: "This is version N+1 of <mention of the version it
   replaces>, part of the functional requirements in <Scope Guide mention>." Then say in one
   sentence what stays valid and what this version adds or changes.
4. Carry over the scenarios that remain true, and add or change the rest.
5. Leave earlier versions untouched unless the user asks for a pointer or status change on them.

Wording fixes, typos, broken links, or a clarification that does not change behavior may be edited
in place. If you cannot tell whether a change alters behavior, ask.

`Not Ready` rows are still being shaped. Edit them in place after approval.

## Reviewing rows

Check each row against:

- the story has a real actor and a stated benefit;
- at least one success and one failure scenario, each with one `WHEN` and observable `THEN`s;
- no leftover template prompts;
- no implementation detail posing as a requirement;
- terms match the glossary; new terms are defined there;
- the title follows the guide's naming convention; each ID plus version pair is unique, and two
  different capabilities never share an ID;
- the status is plausible given Jira and code evidence;
- each versioned row (v2, v3, …) links the version it replaces, and that version was not silently
  rewritten;
- `JIRA Ticket` links resolve to the matching ticket when present.

Report findings per row with the row title and link. Do not fix them without approval.
