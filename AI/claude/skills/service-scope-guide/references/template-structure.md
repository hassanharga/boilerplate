# Scope Guide page structure

Last verified: 2026-09-30, against the live blank Scope Guide and the Dispatch and Location guides.
When this date is more than 30 days old, compare the snapshot with the live blank template before
relying on it. Report what you found: still matching, changed (and how), or not checked.

This is the section skeleton, what belongs in each section, and where evidence usually comes from.
Re-fetch the target and blank template before writing: the live pages win if this snapshot drifts.

## Contents

- [Page header](#page-header)
- [1. Introduction](#1-introduction)
- [Optional: Key Concepts](#optional-key-concepts)
- [2. Requirements](#2-requirements)
- [3. Constraints](#3-constraints)
- [4. Appendices](#4-appendices)
- [Page footer](#page-footer)
- [Section numbering](#section-numbering)
- [Filling order](#filling-order)

---

## Page header

Two columns: a gray table of contents on the left; on the right a metadata table and a green quote
listing the five questions the guide answers (current state and problem, solution, functional
requirements with scenarios, non-functional requirements, constraints).

Metadata rows: `Domain` (Mobility), `Project` (a mention of the parent service page), `Author(s)`,
`Approver(s)`. Authors and approvers are Notion person mentions. When unknown, keep the italic
placeholder (`*Mention author(s)*`); never guess people.

The blank template also carries a blue `💡` callout explaining that blue lamp callouts are
instructions and can be removed once a section is done. Mature guides have removed it.

## 1. Introduction

The blank template's instruction: each sub-section has **3 to 4 points max**, each point **no more
than 2 lines**, written as `→` lines inside one colored quote block (Shift+Enter between points).
Hold to that. It keeps the introduction readable in a minute.

- **1.1 Context** (gray quote): the current state someone must know to understand the problem —
  where the capability lives today, who uses it, how it works now.
- **1.2 Problem** (red quote, left column): what is wrong or limiting today, and its cost.
- **1.3 Solution** (green quote, right column): the proposed direction at scope level — what the
  service will be and what that enables. Not the architecture.

Problem and Solution sit side by side in a 50/50 column block. Each problem point should have a
matching solution point, or the gap should be deliberate.

**Where to look:** PRDs, RFCs, epic descriptions, kickoff notes, recorded walkthroughs, incident
history. Code can confirm the "current state" facts but not the problem framing.

## Optional: Key Concepts

Dispatch inserts `# 2. Key Concepts` after the introduction, holding a synced purple `📽️` callout
listing recorded design walkthrough sessions (title, date, link) with a nested yellow `⚠️` note:
recordings are supplementary, and the written guide wins any conflict. Add such a section only when
the user supplies recordings or key-concept material. Keep that note whenever recordings are
listed. The callout is a synced block; see `notion-mechanics.md` before editing it.

## 2. Requirements

### 2.1 Functional Requirements

A blue `💡` callout defines functional requirements (what the product must do) and tells editors to
click **New** so the database template guides them. Then the inline **Functional Requirements**
database — one row per requirement. Row content, naming, versioning, and properties are in
`requirement-rows.md`.

### 2.2 Non-functional Requirements

A blue `💡` callout explains NFRs and the section rules, which remain the contract:

- the eight standard categories are listed; add more categories only if needed;
- under each, list requirements following the example given;
- if a category has none, write **N/A** and remove the extra `→` points;
- keep the height of each pair of adjacent columns equal by adding empty lines.

Categories, in 50/50 column pairs, each with a gray `📌` question callout, a blue `💡` example
callout, and a colored quote holding the `→` points:

| # | Category | Question | Quote color |
| --- | --- | --- | --- |
| 2.2.1 | Performance | How fast does the system return results or process information? | red |
| 2.2.2 | Scalability | How much will performance change with higher workloads? | green |
| 2.2.3 | Reliability | How often does the system experience critical failures? | brown |
| 2.2.4 | Maintainability | How long to fix the issue when it arises? | orange |
| 2.2.5 | Availability | How long is the average system downtime? | yellow |
| 2.2.6 | Security | How well are the system and its data protected? | purple |
| 2.2.7 | Portability | Which hardware, OS, and browsers does it run on? | green |
| 2.2.8 | Compatibility | Does the system conflict with other applications and processes? | red |

A good NFR point names the measure, the target, and the condition:
"95th-percentile Dispatch Run latency ≤ 800 ms at 200 requests/second". Weak examples found in live
guides — "as fast as possible", "never fail", "99% reliable" with no window — should be flagged in a
review, not copied. If the team has not set a number, write the point with `TBD` and name who
decides; do not invent one.

Location keeps the gray `📌` question callouts and removes the blue examples once filled. Dispatch
still carries empty placeholders here. An empty NFR section in a mature guide is a finding worth
reporting.

**Where to look:** SLOs and SLAs, capacity plans, incident postmortems, product commitments, platform
standards, and dashboards. Observed metrics (for example from Datadog) describe current behavior;
present them as evidence for a target, not as the target itself.

## 3. Constraints

A toggle heading containing two columns:

- **3.1 Technical Constraints** (red quote): fixed technical conditions the design must respect —
  a mandated platform, a third-party provider, a shared database that cannot be split yet, a
  compatibility contract with legacy clients.
- **3.2 Business Constraints** (green quote): deadlines, markets, regulations, budget, contractual
  obligations.

Use `N/A` when there are none. An open question ("Redis or MongoDB? Needs assessment.") is not a
constraint. Flag it in a review and suggest moving it to the requirement or decision where it
belongs.

## 4. Appendices

### 4.1 Glossary `{toggle="true"}`

Gray `📌` callout: this is the ubiquitous/shared language for everyone working on the scope. Then a
three-column table: `ID`, `Term`, `Description`, with a header row. IDs are zero-padded sequential
(`001`, `002`, …).

- New terms take the next number after the current highest. Never renumber existing rows, even with
  gaps (Dispatch skips `074`), because requirement rows and conversations cite them.
- Define a term in one natural sentence, as this team uses it. Do not define it by repeating it.
- In Dispatch the glossary table is a **synced block**, and the Design Guide's ubiquitous-language
  section may embed it. A change can therefore appear on several pages. Follow the synced-block
  workflow in `notion-mechanics.md`.
- Mature glossaries sometimes include implementation details (Dispatch names Redis, MongoDB, and
  BullMQ). Preserve them; for new terms, keep implementation details out.

### Optional: Requirements Map `{toggle="true"}`

Dispatch has `5.2 Requirements Map`, with one toggle per area (for example `→ Engine Area`). Each
toggle holds a PlantUML **activity diagram** of the end-to-end flow. Every step carries a
`note right` naming the requirement IDs that govern it (for example `[EN-9] Idempotency & Safe
Retries`). It shows which requirement owns each step and exposes steps no requirement covers.

To update a map: decode the existing URL, add or rename the affected steps and notes, encode it
again, and verify. Commands:

```bash
python3 <skill-dir>/scripts/plantuml_url.py decode '<existing plant-uml.yplatform.dev URL>'
python3 <skill-dir>/scripts/plantuml_url.py encode map.puml
```

`<skill-dir>` is the directory containing this skill's `SKILL.md`. Encoding and decoding are local.
Fetching the URL sends the source to the internal renderer: do that only when the user has
authorized the update. An HTTP 200 is not proof, because PlantUML can return an error image. Check
that the response has no syntax-error banner and that the notes list the intended IDs.

### Optional: Related Links `{toggle="true"}`

Links to companion pages (Dispatch links "A Policy-Driven Engine"), boards, and presentations.

## Page footer

Two columns: `< Previous Page` (red) mentioning the parent service page, and `Next Page >` (green)
mentioning the sibling Design Guide. When creating a guide, update both mentions from the template
placeholders to the real pages.

---

## Section numbering

The blank template numbers sections 1 Introduction, 2 Requirements, 3 Constraints, 4 Appendices.
Adding Key Concepts shifts them in Dispatch to 3, 4, and 5. Dispatch's `# 4. Constraints` still
contains `3.1`/`3.2` sub-headings, and its NFR sub-headings are `3.2.x`. When you add a section,
renumber only the headings you were authorized to touch. Report other inconsistent numbering as a
finding.

## Filling order

1. **Context, Problem, Solution**: everything else is judged against them.
2. **Glossary seed**: the handful of terms the requirements will use, so rows share one vocabulary.
3. **Functional requirements**: the core capability rows first, then supporting rows.
4. **Non-functional requirements**: once the capabilities they qualify are known.
5. **Constraints**: often surface while writing 3 and 4.
6. **Glossary completion**: every capitalized domain term used in the rows is defined.
7. **Requirements map**, if the guide uses one: after the requirement IDs are stable.
