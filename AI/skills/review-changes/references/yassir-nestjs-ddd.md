# Yassir Mobility NestJS and DDD Review Profile

Apply this profile only when repository instructions, package names, or source
layout identify a Yassir Mobility service using NestJS and the Mobility
microservices chassis. Project instructions, current code, configuration, and
the repository’s pinned dependency versions control every conclusion.
Technology notes in this file are investigation prompts, not authoritative
contracts.

Chassis conventions snapshot: 2026-08-23. Nothing here is asserted as fact — each
section says what to check and against what — so the date matters only for the
Mobility-specific contracts below (the terminal recovery invariant in particular).
If the chassis has moved, the current code wins and the prompt is what is stale.

## Architecture boundaries

For the common hexagonal layout:

- domain code must remain free of NestJS, persistence, transport, and DTO types;
- application code uses declared ports rather than concrete infrastructure;
- infrastructure translates between persistence/transport and domain shapes;
- controllers and consumers delegate use-case logic to application handlers;
- aggregate invariants live at the aggregate boundary, including negative and
  cross-field cases that individual DTO validation cannot enforce.

Raise a finding only when the current repository actually follows this layout
and the change violates an established boundary. Do not require filenames,
interface prefixes, factories, error catalogs, or HTTP-conversion methods merely
because another Mobility repository uses them; compare local siblings and
instructions first.

## Either and Result

Trace both sides before accessing a value. A failure branch that logs and then
continues to a success-shaped result is a correctness defect. Preserve the local
error/factory conventions only when project code or instructions establish
them. A new error must reach the transport mapping used by this repository, but
the exact method name is not universal.

Tests should cover meaningful `left`/error branches and prove the resulting side
effects, not merely that a mock was called.

## Domain and persistence fidelity

- Value objects and aggregates must not expose or retain mutable references when
  immutability is part of their contract.
- Correlated fields and non-empty collections need joint negative tests at the
  domain factory or mutator that owns the invariant.
- Mapper/schema/response changes need round-trip coverage across every affected
  direction.
- Driven ports speak in domain/primitives unless the repository explicitly
  defines another boundary.

When identifiers can be normalized or cast, compare the raw input, persisted
canonical identifier, and downstream query semantics. Verify behavior against
the pinned database driver/ODM and repository tests before claiming that one
query accepts an identifier representation that another rejects.

## Terminal recovery invariant

For Mobility recovery and decision-envelope flows, required terminal or
idempotency persistence must succeed before decision/failure envelope
publication. If terminal persistence fails, return or propagate failure and stop
publication. A failed stale-record touch is a failure with record identity,
state, and error context—not a successful skip.

Apply this invariant only to flows using that recovery contract. For other
orchestrators, derive ordering from their documented outbox, transaction, retry,
or compensation protocol using the reliability reference.

## Production rollout evidence

Seeder-only changes do not prove production activation when the seeder skips
production. Require a migration, operator runbook, external rollout reference,
or another verified provisioning path.

New topics, event patterns, publishers, consumers, or cloud resources require
evidence for broker provisioning, IAM, deployment values, monitoring, and
rollback when those live outside the application repository. Treat absence from
the repository as a Question until the external source is checked.

## Chassis version gate

Read the declared and resolved `mob-microservices-chassis` version before using
resilience or logging rules. Do not transfer a contract from another version or
repository. For the pinned version, check the repository’s installed types,
tests, configuration, and authoritative source for:

- the resilience wrapper order and which failures count toward each policy;
- overall retry-budget timeout versus a fresh per-attempt timeout/cancellation
  signal;
- propagation of the supplied `AbortSignal` to the transport;
- numeric direct gRPC status codes versus wrapper error-name matching;
- redaction of request, response, header, query, URL, and nested-error fields
  retained by error normalization.

If a claim cannot be verified for the pinned version, ask for evidence rather
than filing a finding from memory or this reference.

## NestJS execution model

For the pinned NestJS and transport versions, verify:

- provider scope and whether mutable instance state can cross request or message
  boundaries;
- how the actual static, dynamic, or global module graph registers and exports
  a new injection;
- which bootstrap path awaits lifecycle work and what ordering it guarantees;
- the guard return/throw contract before claiming an unusual return value
  permits or denies access;
- retry, acknowledgment, and redelivery semantics for the configured event
  library and handler options.

A caught event-handler failure is a defect when evidence shows unintended
acknowledgment or data loss, not merely because a catch exists.

## Verification and coverage

Read active Jest/Vitest/Sonar configuration and repository instructions. Enforce
100% unit coverage where configured, another threshold where configured, and no
invented target where none exists. New domain invariants need positive and
negative tests; application handlers need focused success and failure-path tests
with appropriate port doubles. Real infrastructure tests may add confidence but
do not replace a focused test of handler decisions when that decision is the
changed behavior.
