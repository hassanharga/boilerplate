# Reliability and State-Machine Review

Use this reference when a change touches orchestration, retries, locks, queues,
state transitions, read-modify-write persistence, or multiple side effects.

## Model the operation before judging order

List legal states, transitions, exit paths, authoritative records, external
effects, retry owner, and recovery mechanism. There is no universal rule that
“publish first” or “persist last” is correct. Judge the sequence against the
system’s recovery protocol.

Prefer designs that make the intended outcome durable before acknowledging work:
an atomic state transition, transactional outbox, idempotency record, or another
recoverable handoff. When direct publication is unavoidable, identify what a
crash between persistence and publication—or publication and persistence—does,
and require an explicit retry or compensation path.

## Exit-path matrix

Enumerate success, validation failure, conflict, not found, timeout, retry
exhaustion, partial failure, cancellation, and unexpected exception. For each,
record:

- returned or thrown outcome;
- persistence transition;
- lock/lease/job cleanup;
- event or envelope publication;
- metrics/logging;
- retry, dead-letter, or compensation behavior.

Compare paths serving the same logical outcome. A missing effect is a defect
only when the protocol requires it; symmetric-looking branches can legitimately
differ. Logging does not turn failure into success. A failed required operation
must remain visible to its retry or caller contract.

## Atomic write predicates

For conditional updates, ensure the predicate admits only legal state tuples.
Independent `$in` conditions can accidentally create a Cartesian product of
illegal pairs. Prefer explicit correlated alternatives or an equivalent typed
state transition. Check version, owner, lease, and run identifiers at the atomic
write, not only in an earlier read.

Treat a read followed by a separate write as a race surface. A stale replica or
cache read must not be the sole authority for skipping or approving a state
transition. The write result—matched/version count or compare-and-swap
outcome—usually supplies stronger evidence.

Distinguish omitted fields from intentional clearing. Spreading payloads or
coalescing stale caller values into `$set` can overwrite authoritative state.

## Idempotency and retry ownership

Identify which layer retries: client, queue, transport, framework, or handler.
Every effect repeated by that owner needs an idempotency key, a guarded state
transition, natural idempotence, or compensation. Confirm that retry exhaustion
is observable and that a manual retry cannot duplicate money movement,
notifications, jobs, or events.

Timeouts need a clear budget and cancellation contract. A timeout that returns
while work continues can duplicate side effects on retry. When multiple attempts
exist, distinguish the overall operation budget from per-attempt deadlines and
verify that cancellation reaches the underlying transport.

## Parallel and partial failure

For `Promise.all` or equivalent fan-out, first-failure rejection does not cancel
the other work. Determine whether partial success is allowed, recorded, and
recoverable. Use an all-settled shape only when every rejected item is inspected;
turning rejected results into an overall success is data loss.

Unbounded parallelism can exhaust pools or rate limits; purely sequential I/O
can violate latency budgets. Require evidence about independence, ordering,
backpressure, and expected cardinality rather than prescribing one construct.

## Representation and semantic consistency

Trace identifiers and transition codes at runtime, not only by static type. A
primary-key lookup may normalize an input while a downstream string field uses
exact matching. After loading an entity, prefer its canonical identifier for
downstream queries and events when that is the domain contract.

Copied branches must emit the event, error code, metric tags, and target state
for their own transition. Compare with the state model and consumers, not only
with a visually similar sibling.

## Required evidence

High-risk findings should identify the competing execution or crash point and
the resulting invalid state. Ask for focused tests that exercise illegal state
pairs, duplicate delivery, partial failure, persistence failure, publication
failure, timeout/cancellation, and retry. Do not demand a specific mechanism
when another mechanism proves the same invariant.
