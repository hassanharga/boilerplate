# API-only services

Read this reference when the repository has no user interface or the requested journey is
entirely API-driven.

## Preserve the existing runner

Look first for the service's integration/E2E conventions: Jest or Vitest configuration,
Supertest, framework test modules, container fixtures, contract tests, and existing
`test:e2e` scripts. Extending that runner is normally cheaper and more trustworthy than
adding a browser-oriented harness.

Playwright's request client, Cypress API mode, or another runner may be reasonable when
already used across the system or explicitly selected. Do not add one merely for its
reporter or worker model when the existing runner can exercise the same behavior.

## Choose workflow-level tests

An API E2E journey should verify behavior across meaningful boundaries, such as:

- authenticate, refresh, authorize, and revoke;
- create a resource, transition its state, and verify terminal state and side effects;
- deliver duplicate or out-of-order events and verify idempotency;
- prove one tenant or role cannot read or mutate another's data;
- verify a consumer-critical response or event contract.

A single pure function or isolated endpoint validation usually belongs in a unit or
integration test. Use the repository's taxonomy rather than renaming tests to satisfy an
arbitrary label.

## Test environment and fixtures

Decide first what the test actually needs to be true. A workflow that depends on
transactions, constraints, migrations, or database-specific behaviour needs a real
instance; one that only needs a stored value may not.

| Fixture | Use when | Cost of getting it wrong |
| --- | --- | --- |
| Container per suite (Testcontainers or the repository's compose file) | Real database, broker, or cache behaviour matters | Slow start; needs a container runtime in CI |
| Shared long-lived test instance | Container startup is prohibitive and the suite can namespace cleanly | Cross-run interference, and a failure in one run poisons the next |
| Transaction rollback per test | The service exposes a test seam for it and the workflow is single-connection | Silently wrong for anything that spans connections, commits, or background work |
| In-memory substitute | The stored value is all that matters | Constraints, isolation levels, and SQL dialect differences never get exercised |

Reuse the repository's existing fixture. Do not introduce a container runtime, a new
database, or a new orchestration layer without authorization — state the proposed change
and its CI cost first.

Run migrations the same way production does, from the same migration files. A schema built
by a test-only script drifts, and the drift is discovered in production.

## Isolation

Namespace identities and records across run, worker, and test — a worker index and a random
suffix in every created identifier. Use dedicated databases, schemas, topics, buckets, or
test tenants when side effects outlive a request. Clean only owned data; never use a broad
delete as teardown.

For a multi-tenant service, an isolation test is not a variation on a happy path. Write it
as a distinct case: create data as tenant A, then attempt every read, list, update, and
delete as tenant B, and assert the *specific* expected response. A `404` and a `403` mean
different things about what the system leaked, and asserting "not 200" hides a regression
from one to the other. Include the paths that skip the usual guard — bulk endpoints,
exports, search, admin routes, and anything that takes an ID directly.

## Idempotency and duplicate delivery

At-least-once delivery means duplicates are normal traffic, not an edge case. For any
consumer or endpoint that claims idempotency, assert on the effect and not just the
response:

- deliver the same message or request twice and verify one resulting record, one charge,
  one outbound notification;
- deliver two messages concurrently with the same idempotency key and verify the same;
- deliver out of order and verify the terminal state is the intended one, not the last
  writer's;
- redeliver after the first attempt has already committed but before its acknowledgement,
  which is the case that actually breaks in production.

An endpoint returning `200` twice proves nothing on its own. Read the resulting state.

## Waiting for eventual consistency

Never sleep for a guessed duration. Poll for the expected condition with a bounded timeout
and a clear failure message naming what was expected and what was observed:

- poll the read model, projection, or outbox until the expected record appears;
- consume from the topic the service publishes to and assert the message that arrived;
- assert on a job's terminal state, not on the job having been enqueued.

Give the helper a single implementation in the suite so timeouts are consistent and one
change adjusts them all. When a poll times out, dump the actual state — the state at
timeout is what diagnoses the failure, and it is gone by the time anyone reruns.

## Broker and event assertions

When the service publishes, the published message is part of its contract. Assert the
topic or queue, the key or routing, the schema version, and the fields consumers depend on
— not the whole payload, which turns every additive change into a failing test.

Use a real broker for ordering, partitioning, redelivery, and dead-letter behaviour; a
substitute in-process bus proves the handler ran, not that the system delivers. If a
substitute is used, say what it no longer proves.

## Contract tests

A contract test answers a different question from an E2E workflow: whether this service's
surface still matches what a specific consumer expects. Keep them separate and do not let
one stand in for the other.

If the repository publishes an OpenAPI, AsyncAPI, protobuf, or GraphQL schema, verify the
implementation against it rather than against a hand-written expectation that can drift.
If it uses a consumer-driven contract tool, the provider verification belongs in the
service's pipeline and the consumer's expectations belong in the consumer's. Do not stand
up a broker or add a contract-testing dependency without authorization.

## Coverage and verification

Keep unit-coverage requirements in the repository's unit-test tooling. Adding an API E2E
workflow neither satisfies nor creates a percentage target. Report the endpoints, roles,
state transitions, and external effects covered.

Run the changed API E2E specs and directly affected checks by default. Run the full service
suite only when the user explicitly requests it, then report infrastructure prerequisites
and actual results.
