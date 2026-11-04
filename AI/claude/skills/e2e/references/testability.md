# Failure states and testability

Use this reference when a journey depends on failures that are hard to produce or systems the team does not control.

## Select evidence, not a universal checklist

Choose failure cases from acceptance criteria, incident history, domain risk, validation rules, permission boundaries, and recovery behavior. Not every journey needs bad input, session loss, network failure, and empty data. A checkout may need decline and idempotency cases; a read-only dashboard may need authorization and empty data; a webhook workflow may need duplicates and reordering.

For each selected case, state:

- the risk or user-visible loss;
- how the state or failure will be produced;
- whether the real backend or a controlled double is involved;
- the visible, persisted, and side-effect outcomes to assert;
- what the test cannot prove.

## Real system versus controlled double

Use the real controlled application path for critical happy paths, authorization, persistence, and contracts whenever the environment supports deterministic data. Use network routing, dependency doubles, sandbox APIs, or test-mode seams for rare failures such as timeouts, declined payments, downstream 500s, dropped connections, and empty responses.

A mocked browser response proves the client handles that response shape. It does not prove the server emits the shape, that authentication reaches the server, or that downstream side effects occur. Pair important mocked failure handling with lower-level contract or integration tests where appropriate and label the boundary in the report.

Do not weaken production security to make a test convenient. Any test-only route, fixed credential, OTP bypass, or fault-injection flag must be restricted to a controlled test environment, unavailable by default, and separately reviewed when it changes application code.

## Common external boundaries

- **OTP, email, and magic links:** prefer a controlled mail/SMS catcher, test tenant, or existing test-only retrieval path. Otherwise cover request/verification behavior separately and report that delivery is unverified.
- **Third-party OAuth:** use a provider sandbox or mock identity provider when available. Otherwise verify the authorization request and controlled callback/session behavior without automating a production identity page.
- **Payments and 3DS:** use the gateway's official sandbox and test instruments. Cover webhook-driven state transitions independently. Do not automate real card or bank challenges.
- **Captcha and bot protection:** use official test keys or a controlled non-production bypass. Never attempt to defeat production protection.
- **Cron and background work:** invoke an existing job interface, controlled trigger, or lower-level handler. Do not wait for real elapsed time.
- **Maps, geolocation, push, camera, and OS dialogs:** use supported browser-context controls and assert application behavior, not third-party pixels or native UI outside the browser's control.
- **WebSockets and multi-client flows:** use separate contexts and assert eventual business outcomes, avoiding fragile intermediate ordering.
- **Generated files and documents:** verify that the user can trigger and receive the artifact; validate detailed contents or rendering with the appropriate lower-level document tests.

## Failure patterns

- **Invalid input:** assert the visible validation result and that invalid state was not persisted.
- **Authorization or session loss:** exercise the relevant boundary and assert safe recovery, redirect, or denial without data leakage.
- **Dependency failure:** inject a controlled timeout, connection failure, or error response and assert a usable recovery path rather than a blank or permanently loading state.
- **Empty data:** prefer a genuinely fresh identity or namespace; otherwise mock the repository's real response contract and label it.
- **Concurrency and idempotency:** submit or deliver duplicates concurrently and verify exactly-once business outcomes where the domain requires them.

If a journey cannot be made deterministic without a product or infrastructure change, do not create a permanently skipped or misleading green test. Report the blocker, the partial coverage, and the smallest safe change that would make it testable.
