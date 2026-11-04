# From raw requirements to a Scope Guide

Use this when the input is unstructured material for a new or barely documented service: kickoff
notes, a PRD, a Slack thread, Jira epics, a bullet list, or a mix. The goal is a draft Scope Guide
the team can approve, not a polished document that hides open questions.

## Contents

- [1. Inventory the material](#1-inventory-the-material)
- [2. Classify every statement](#2-classify-every-statement)
- [3. Shape functional requirements](#3-shape-functional-requirements)
- [4. Pull out quality targets and constraints](#4-pull-out-quality-targets-and-constraints)
- [5. Write the introduction last](#5-write-the-introduction-last)
- [6. Present the draft](#6-present-the-draft)

---

## 1. Inventory the material

Read everything the user supplied before writing anything. Note who said what and when, if the
material shows it. Later statements usually replace earlier ones. When two statements conflict and
the order is unclear, keep both and raise the conflict.

Then check whether the service already exists in the Mobility Microservices database and whether
neighboring services' Scope Guides already cover part of this scope. A new service that duplicates
an existing capability is the first thing a reviewer will ask about.

## 2. Classify every statement

Put each statement into exactly one bucket. A single bullet often holds several statements; split
it first.

| Bucket | Test | Goes to |
| --- | --- | --- |
| Current state | Describes how things work today | 1.1 Context |
| Pain | Describes what is wrong, slow, costly, or impossible today | 1.2 Problem |
| Direction | Describes what the new service will be or enable | 1.3 Solution |
| Capability | Someone can do or observe something new | a Functional Requirement row |
| Quality target | How fast, how many, how available, how secure | 2.2 NFR category |
| Fixed condition | Must be respected and is not up for debate | 3.1 or 3.2 Constraints |
| Term | A domain word people need to agree on | Glossary |
| Design idea | A how: a library, a database, a queue, an algorithm | Not the Scope Guide; list it for the Design Guide |
| Open question | Undecided, phrased as a question or "TBD", or two options | Open questions list |
| Out of scope | Explicitly excluded | the related row's Out of Scope, or a scope note |

Watch for these common hidden cases:

- **A quality target inside a feature.** "The rider gets a confirmation within 2 seconds" is a
  capability (confirmation) plus a Performance target (2 seconds). Put the observable outcome in the
  scenario and the number in 2.2.1, then cross-reference them.
- **A design idea posing as a requirement.** "Use BullMQ delayed jobs to trigger dispatch" is a how.
  The requirement underneath is when dispatch must start. Keep the "when", and move the tool to the
  design list, unless the notes say the tool is mandated. In that case it is a technical constraint;
  record who mandated it.
- **An open question posing as a constraint.** "Postgres or Mongo?" is not a constraint.
- **A deadline** is a business constraint, even when it appears in a feature bullet.

## 3. Shape functional requirements

- **One row per capability.** Split a bullet that bundles several capabilities, such as "riders
  can schedule, edit and cancel". Merge two bullets that describe the same capability from
  different angles, and say that you merged them.
- **Name each row** as a short verb phrase: `Schedule a Ride`, `Cancel a Scheduled Ride`.
- **Write the story** from the notes. When the notes don't say who needs a capability, or why, write
  the story with the gap marked, for example `So that <benefit — to confirm>`, and add a question.
  Do not invent the benefit.
- **Write at least a success and a failure scenario** per row. Derive failures from the notes when
  possible, such as validation rules, limits, and time windows. When the notes give no failure
  behavior, draft the obvious failure (invalid input, not found, too late) and mark its outcome as
  proposed.
- **Order rows** so the core capability comes first and supporting rows follow.
- **Prefixes and areas.** Use plain titles by default, as in the blank template. Suggest Dispatch-style
  prefixes and Area values only when there are many rows (roughly more than 12) that fall into clear
  groups, and ask before adding columns to the database.
- **Leave properties honest.** Status stays at the initial value. Priority, milestone and Jira link
  are filled in only from the notes.

## 4. Pull out quality targets and constraints

For each of the eight NFR categories, fill it from the notes, or write `N/A` when the notes show it
does not apply. Otherwise write `TBD — <who decides>`. Never fill a category with a plausible
number the notes don't contain. A reviewer can't tell your guess from a commitment.

When a number is stated without a condition ("fast", "2 seconds"), keep the number and add the
missing condition as a question: for which percentile, at what load, and measured where.

Record constraints only when the notes treat them as fixed, and name the source.

## 5. Write the introduction last

Context, Problem and Solution summarize everything else, so draft them once the buckets are sorted.
Keep to 3 to 4 points each, and no more than 2 lines per point. Each problem point should have a
matching solution point. If the notes give no problem statement, for example when they are only a
feature list, say so; don't manufacture a business case.

## 6. Present the draft

Show the draft as the guide will read, section by section, with:

- numbered items: `S1` for a section, `R1…Rn` for requirement rows, and `G1` for glossary rows;
- a "Moved out" list of design ideas for the Design Guide, each with its source line;
- a "Merged or split" note for any statement that did not map one to one;
- open questions, grouped by who can answer them (product, tech lead, ops);
- a coverage check: every statement from the input is used, moved out, or listed as a question,
  and none is silently dropped.

Then follow the create workflow in `notion-mechanics.md`, but only after approval: duplicate the
template, then write the approved sections and rows.
