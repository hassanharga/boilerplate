# Playwright patterns

Read this reference only when the repository uses Playwright or the user has selected it. Match guidance to the repository's installed Playwright version and current official documentation.

## Configuration

Prefer an existing `playwright.config.*` and project layout. Preserve established scripts, reporters, browser projects, timeouts, and CI integration unless evidence shows a problem.

For a new configuration, decide each option from repository facts:

- start commands and readiness URLs come from existing application scripts;
- browser projects come from supported-user and CI requirements, not an automatic cross-browser matrix;
- workers fit machine, database, and external-service capacity;
- retries expose intermittent failures but do not fix them; retain and report the first-failure evidence;
- traces are normally most useful on the initial failure or first retry in CI; videos and screenshots are optional when traces already provide adequate evidence;
- a setup project is useful only when its authentication strategy fits the suite.

Do not force `fullyParallel`, fixed ports, fixed retry counts, or generic script names into an existing repository. Avoid installing system browser dependencies automatically; browser downloads and host packages require the user's authorization.

## Authentication and server-side isolation

Playwright creates an isolated browser context for each test. That isolates cookies and browser storage, not the server-side account, database rows, queue messages, rate limits, or feature settings.

A shared saved authentication state is suitable only when all concurrent tests can safely use the same account without changing state that affects another test. When tests mutate profile, permissions, balances, settings, carts, or other shared account data, provision one identity per worker or per test as the risk requires. If provisioning is temporarily impossible, serialize only the conflicting tests and report the limitation rather than pretending they are isolated.

Keep one journey that exercises the real sign-in UI. Other tests may authenticate through a controlled API or reuse saved state when that does not weaken the behavior being tested. Use distinct identities for authorization-boundary tests; changing a mocked role on one session does not prove server authorization.

Saved state may contain credentials, session cookies, and headers capable of impersonating the test user. Store it in a gitignored test-output or authentication directory, never commit it, and regenerate it when expired. Confirm whether the application relies on cookies, local storage, or session storage before assuming saved state captures the required mechanism.

## Data setup and cleanup

Prefer setup through the application's public or test-supported API because it respects real validation. Direct database setup is acceptable when no API can produce the needed state and the repository already has safe test tooling. Network mocks are useful for controlled error and empty states but do not prove the frontend matches the live contract.

Make identifiers unique across CI run, shard, worker, and test. Clean only records created by that scope. Teardown should still run after an assertion failure, but the suite must tolerate leftovers from a killed process without colliding with a later run. Never point destructive seed or cleanup logic at production.

For state-mutating tests, verify the important persisted state through an independent surface when useful, such as an API read or a later UI page. A successful click alone does not prove the operation completed.

## Locators and waiting

Prefer, in order:

1. user-facing roles and accessible names;
2. labels, stable text, placeholders, and alt text;
3. stable test IDs for repeated, dynamic, or otherwise ambiguous elements.

Scope locators to a dialog, row, list item, or other stable region. Avoid CSS structure, generated framework attributes/classes, XPath chains, `.first()` used to silence ambiguity, and assertions that only prove a request was sent.

Use Playwright's actionability checks and web-first assertions. Wait for the observable result: rendered content, navigation outcome, response-backed state, or enabled control. A fixed timeout is not evidence that the application is ready.

## Requests, rendering, and services

Browser routing intercepts requests made by the browser. It cannot directly replace server-side fetches performed by a server-rendered framework, background worker, or downstream service. Establish where a request originates before designing fault injection. For server-side work, use controlled backend data, a dependency double, a test-mode seam, or the repository's integration tooling.

When several services must start, wait on genuine readiness endpoints rather than ports that merely accept a connection. Record prerequisites such as databases, queues, containers, and environment variables. Reuse existing orchestration instead of embedding a new infrastructure lifecycle into Playwright unless separately approved.

## Flake diagnosis

Reproduce the smallest failing spec with the same browser, worker count, environment, and retry state that exposed it. Inspect the first failure, trace, console, network, and server logs. Common causes include shared server data, stale saved sessions, readiness races, ambiguous locators, unobserved asynchronous work, environmental resource limits, and tests that depend on order.

After the fix, run the spec independently and repeat it under the relevant concurrency. A retry that passes remains a flaky result until the cause is understood.
