# Design Principles Lens

Read for every review that changes production code. Run this pass after the
behavior trace in step 3, on the units the change adds or materially rewrites.
The behavior trace finds what breaks; this pass asks whether the shape of the
change makes it likely to break, hard to change, or harder than it needs to be.

A principle is the reason to look, never the finding by itself. "Violates SRP" is
an opinion. "This module wires providers, runs startup initialization, and parses
legacy env keys, so the env cleanup next sprint must edit the bootstrap path" is
a finding. Every design finding names the concrete cost in this change.

## Lenses

| Principle | Look for | Cost that makes it a finding |
| --- | --- | --- |
| DRY | The same rule, constant, mapping, or config value defined in two places | The copies can already disagree, or one change in the PR had to be made twice |
| KISS | A mechanism more general or indirect than the requirement needs: dynamic proxies, reflection, generic dispatch, meta-configuration | The generality creates behavior nobody asked for, or a simpler shape meets the same requirement with fewer failure modes |
| YAGNI | Options, branches, extension points, or parameters with no caller or requirement | Dead or unreachable paths that still need tests, docs, or reasoning |
| SRP | One unit changing for unrelated reasons, or mixing policy with plumbing | The unit cannot be tested or changed for one reason without touching the other |
| OCP | Adding the next variant means editing a switch, list, or wiring in several places | A missed edit fails silently instead of at compile time or in a test |
| LSP | A substitute, wrapper, decorator, or mock that does not honor the contract of what it replaces | Callers or the framework observe different semantics: sync becomes async, extra members appear, errors change shape |
| ISP | Consumers forced to depend on members they do not use | A narrow consumer breaks or needs a double for unrelated methods |
| DIP | Core or application code depending on infrastructure details | A use case imports an adapter, driver type, or transport DTO |
| Cohesion and coupling | Logic placed far from the data or rule it belongs to; hidden temporal coupling | Correctness depends on call order or initialization the type system does not express |
| Irreversibility | New names and contracts that are expensive to change once shipped: feature-flag keys, env vars, topic and event names, API fields, schemas, persisted keys | The name or shape misdescribes behavior, or a cheaper-to-change alternative exists before first deploy |
| Operability | How the design behaves during incidents and at volume | Per-request error logs, silent fallbacks, no signal when a switch or fallback engages |

Project architecture rules — hexagonal layers, DDD boundaries, local naming and
module conventions — come from repository instructions and, for Yassir Mobility
services, the [Yassir NestJS/DDD profile](yassir-nestjs-ddd.md). This lens does
not restate them.

## Tensions between principles

Principles pull against each other. Resolve the tension in the finding instead of
citing one principle in isolation:

- DRY versus coupling: two similar blocks that change for different reasons are
  not duplication. Prefer the rule of three before asking for an abstraction.
- KISS and YAGNI versus SOLID: do not ask for an interface, factory, or strategy
  that has one implementation and no stated second use.
- Simplicity is measured against the requirement, not against the reviewer's
  preferred style.

When the project's established convention conflicts with a textbook principle,
the convention wins unless the change creates a concrete cost under it.

## Classification

- `Issue - Blocking` or `Issue - Non-blocking`: the design choice causes or newly
  exposes a concrete failure or cost in this change. Pass the normal finding gate.
  Example: a generic wrapper whose catch-all behavior makes the framework call
  methods that do not exist on the real object.
- `Suggestion - Non-blocking`: a clear improvement with a stated, specific benefit
  and no demonstrated defect. Design Suggestions are on by default, capped at
  three per review, highest value first. Report more only when the user asks.
- Out of scope: pre-existing design debt the change does not touch or worsen,
  preferences with no stated cost, and renames or restructures outside the diff.

An irreversibility concern is usually an Issue when the name or contract is about
to ship for the first time, because later correction costs a migration.

## Writing a design finding

Use the normal finding shape. Lead `Issue:` with the concrete problem in this
change and name the principle in plain words once, for example "the same default
is defined in two config keys (duplication)". `Impact:` names who pays and when.
`Fix:` gives the smallest change that removes the cost, not a redesign, unless
the redesign is smaller.
