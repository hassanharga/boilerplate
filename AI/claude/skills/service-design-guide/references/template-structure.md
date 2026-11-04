# Design Guide page structure

Last verified: 2026-08-23, against the live blank template and the exemplar guides. Re-verify
when this date is more than 30 days old, and say in the output that the snapshot was not
revalidated.

The established section skeleton, what belongs in each section, and where to find evidence. This is
a verified snapshot derived from the live blank template and the Dispatch, Location, Lead, and Maps
& Routes guides. Re-fetch the target and blank template before writing: the live pages win if this
snapshot drifts.

When updating, preserve the target guide's custom sections, layout, callouts, synced blocks, and
human-written rationale. Dispatch is the mature exemplar for depth, not a requirement that every
service copy its engine-specific content or volume.

## Contents

- [Page header](#page-header)
- [1. High-Level Architecture](#1-high-level-architecture)
- [2. Detailed Design](#2-detailed-design)
  - [2.1 Domain Layer](#21-domain-layer)
  - [2.2 Microservice Contract](#22-microservice-contract-service-api)
  - [2.3 Presentation Layer](#23-presentation-layer)
  - [2.4 Infrastructure Layer](#24-infrastructure-layer)
  - [2.5 Application Layer](#25-application-layer)
- [3. Appendices](#3-appendices)
- [Filling order](#filling-order)

---

## Page header

Two-column block: a table of contents on the left, and on the right a metadata table plus a green
callout listing the seven questions the guide answers.

Metadata table rows — `Domain` (Mobility), `Project` (mention of the parent service page),
`Author(s)`, `Approver(s)`. Author and approver are Notion person mentions; if you don't know them,
leave the italic placeholder rather than inventing names.

Some guides also carry a purple callout linking recorded design walkthrough sessions. Preserve it if
present; only add one if the user gives you recordings. It should state that recordings are
supplementary and that the written doc wins any conflict.

## 1. High-Level Architecture

Opening line explains that this section covers how the service interacts with other systems and its
internal components at a high level.

### 1.1 Container Diagram

Gray `📌` callout explaining this is the [C4](https://c4model.com/) container view: the relationship
between this microservice and other microservices/systems inside and outside Mobility, and how they
communicate. Note that the container named in the diagram title is _this_ service.

Then the diagram image. These come from Structurizr at `structurizr.yplatform.dev` — see
`diagrams.md`.

**Where to look in the repo:** outbound HTTP clients and their base URLs, message broker topic
producers/consumers, database connection config, third-party SDK usage, and the service's own
inbound routes. Also check the Scope Guide for systems that are planned but not yet wired up — mark
those as planned rather than existing.

### 1.2 Component Diagram

Gray `📌` callout: all Mobility microservices use Hexagonal Architecture
(`b218065f57fe4531be9e44f211d3ef9f`); this C4 component view zooms inside the service to show the
internal components structured per that guide.

Then the diagram image.

**Where to look:** modules, entry points, dependency wiring, ports, handlers, and runtime flows.
Components represent meaningful responsibilities with clear interfaces and dependencies. Do not
mirror top-level folders mechanically.

## 2. Detailed Design

Opens with a red `⛔` **ALERT!** callout stating that the layers and components rest on two
cornerstones, mentioning both pages:

- Hexagonal Architecture: `b218065f57fe4531be9e44f211d3ef9f`
- Domain-Driven Design: `0843af60da3b4097b146b9c12eb59674`

Keep this callout. It's the pointer that stops a reader misinterpreting everything below it.

### 2.1 Domain Layer

Two-column intro: gray quote block on the left describing the domain layer (the yellow hexagon) as
the home of core business logic and rules, where the DDD focus lies, and listing the three
subsections; hexagon image on the right.

Three toggle subsections:

#### 2.1.1 Ubiquitous/Shared Language `{toggle="true"}`

A three-column table — `ID`, `Term`, `Description` — with header row and header column. IDs are
zero-padded sequential (`001`, `002`, …). It may be wrapped in a synced block so the glossary can be
reused on other pages. Follow the shared-edit confirmation workflow in `notion-mechanics.md`; do not
edit the source merely because a reference is present.

Include domain-specific terms needed for engineers, product partners, and operators to share the
same meaning. Use one natural sentence defining the term as this team uses it; do not define a term
by repeating itself. Avoid generic engineering words that add no service-specific understanding.

**Where to look:** domain entity/value-object/enum class names, event names, and any acronym in the
codebase or Scope Guide. Also mine the Scope Guide prose; it usually introduces the vocabulary first.

Judge completeness against the service's actual domain and Scope Guide, not another guide's entry
count. Preserve a mature existing glossary unless a specific, evidence-backed correction is approved.

#### 2.1.2 Domain Model `{toggle="true"}`

One or more PlantUML class diagrams showing aggregates, entities, value objects, enums, and their
relationships. The Dispatch convention uses stereotype-based styling:

```
skinparam class {
  BackgroundColor<<Aggregate Root>> #Lavender
  BackgroundColor<<Domain Event>>   #cfe8e5
  BackgroundColor<<Value Object>>   #eeeeee
  BackgroundColor<<enum>>           #yellow
  BackgroundColor<<interface>>      #lightblue
  StereotypeFontColor Brown
}
```

wrapped in a `package "<Name> Bounded Context" { ... }`. Split into several diagrams when one becomes
unreadable rather than shrinking everything.

**Where to look:** the domain module — entity classes, their fields and methods, value objects, and
the aggregate boundaries implied by which objects are loaded and saved together.

#### 2.1.3 Domain Events `{toggle="true"}`

PlantUML diagram(s) of the event hierarchy, followed by an inline **Domain Events** database. The
established schema typically has `Name`, `Version`, and a system-managed ID; fetch the live schema
and row template before writing. See `notion-mechanics.md`.

**Where to look:** classes named `*DomainEvent` / `*Event` raised inside the domain layer, and the
code paths that raise them.

### 2.2 Microservice Contract (Service API)

Two-column intro explaining that the contract comprises commands (writes), queries (reads), and
integration events (published or consumed).

#### 2.2.1 Commands `{toggle="true"}`

Gray `📌` callout defining commands as write operations that modify system state, each an explicit
instruction with business rules and validations enforced.

Inline **Microservice - Commands** database. The established schema typically has `Command`, `Story`,
and a system-managed ID; fetch the live schema and template before writing.

**Where to look:** command handlers / write-side use cases, and the routes or consumers that invoke
them.

#### 2.2.2 Queries `{toggle="true"}`

Gray `📌` callout defining queries as read operations that retrieve data without modifying state.

Inline **Microservice - Queries** database. The established schema typically has `Query`, `Story`,
and a system-managed ID; fetch the live schema and template before writing.

#### 2.2.3 Integration Events `{toggle="true"}`

Gray `📌` callout defining integration events as messages published to notify other systems, enabling
loose coupling — and stressing the distinction from domain events: **domain events are scoped inside
the service boundary; integration events cross it.**

Preserve the blue `💡` callout as part of the live pattern, but treat its questions as discovery
prompts rather than proof. A local domain event may suggest a published contract; a container
relationship may suggest an integration to investigate. Neither establishes a current event by
itself.

Require concrete boundary-crossing evidence: broker publish/consume code, a topic or queue,
subscription, serializer, versioned schema, deployed configuration, or an owning service contract.
Classify Scope Guide or diagram-only events as planned or unverified and keep them out of the current
events database unless its live schema explicitly supports status.

Inline **Microservice - Integration Events** database. The established schema typically has `Name`,
`Type`, `Version`, `Domain Event`, and a system-managed ID. Fetch the live schema, select values,
relation target, and row template before writing.

### 2.3 Presentation Layer

Two-column intro: the presentation layer (left half of the hexagon) holds driving adapters — HTTP
adapters for web, CLI adapters for command-line, messaging adapters for broker interactions.

Blue `💡` callout: for each command and query in the contract, identify which adapter exposes it.

Inline **Microservice - Presentation Layer - Adapters** database. The established schema typically
has `Name` and `Type`; fetch the live schema and exact select values before writing.

**Where to look:** controllers, route definitions, message consumers, CLI entry points.

### 2.4 Infrastructure Layer

Two-column intro: the infrastructure layer (right half of the hexagon) bridges core logic and
external technical systems via driven adapters — databases, external APIs, messaging systems, other
services.

Blue `💡` callout: use the container diagram to identify databases, APIs, messaging systems, and
services that need investigation. Add driven adapters only when current code/configuration verifies
their implementation; mark Scope-only relationships as planned.

Inline **Microservice - Infrastructure - Adapters** database. It typically has `Name`; fetch the live
schema and row template before writing.

**Where to look:** repository implementations, external service clients, cache/broker/storage
gateways.

### 2.5 Application Layer

Two-column intro: the application layer (green hexagon) mediates between domain logic and the outside
world — orchestrating use cases and managing data flow, without holding business logic itself.

Then a **Ports** section with the inline **Microservice - Application Layer - Ports** database. It
typically has `Name` and `Type`; fetch the live schema and select values before writing.

Services with heavier orchestration add their own subsections here — Dispatch has a _Service to
Service Orchestration Flow_ sequence diagram plus `Engine` and `EDBs` databases. Add such subsections
only when the service genuinely has that concept; don't import Dispatch's engine vocabulary into a
service that has no engine.

**Where to look:** the actual boundaries and dependency tokens the application layer uses. A port may
be represented by an interface, abstract class, type, or framework-specific token. Driving ports are
invoked by presentation adapters; driven ports are implemented by infrastructure adapters.

## 3. Appendices

Blue `💡` callout noting this holds related information not belonging to the sections above — related
links, references, glossary. Keep the section even when empty; it's cheap and gets used later.

## Page footer

Two-column previous/next page navigation mentioning the sibling guides (Scope Guide before,
Implementation Guide after).

---

## Filling order

The sections have real dependencies, and filling them out of order causes rework:

1. **Ubiquitous language** first — it fixes the vocabulary every later section uses.
2. **Domain model** and **domain events** — the nouns and the things that happen to them.
3. **Container diagram** — establishes which external systems exist.
4. **Commands and queries** — the write and read surface.
5. **Integration events** — verify boundary-crossing producers, consumers, transport, and schemas;
   use domain events and the container diagram only as investigation clues.
6. **Presentation adapters** — mapped from commands and queries.
7. **Infrastructure adapters** — mapped from the container diagram's external systems.
8. **Ports** — driving ports pair with presentation adapters, driven ports with infrastructure ones.
9. **Component diagram** — draw it last, once meaningful responsibilities and dependencies are known.
