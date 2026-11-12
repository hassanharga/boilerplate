# Cypress and WebdriverIO patterns

Read this reference when the repository uses Cypress or WebdriverIO. Match guidance to the
installed version and its current official documentation — both runners have changed their
config format, isolation defaults, and command APIs across major versions, so verify before
quoting an option name.

The principles in the skill are unchanged. What differs is where isolation comes from, how
sessions are reused, and how each runner waits.

## Cypress

### Configuration

Prefer the existing `cypress.config.*` and folder layout. `e2e` and `component` are
separate testing types with separate configuration blocks; do not move specs between them
to satisfy a naming preference.

Decide each option from repository facts: `baseUrl` from the application's own start
scripts, `specPattern` from the existing layout, `video` and `screenshotOnRunFailure` from
what CI actually needs to diagnose a failure. Retries are configured separately for `runMode`
and `openMode` — a retry that passes is still a flaky result, and the first-failure artifact
is the evidence to keep.

Cypress runs specs in a browser process it controls. Node-side work — database seeding,
file system access, container control — lives in `setupNodeEvents` tasks, not in the spec.
Reach for `cy.task` rather than trying to make a Node API work inside the browser.

### Test isolation

`testIsolation` is on by default in current versions: cookies, local storage, and session
storage are cleared between tests, and the page returns to `about:blank`. That is browser
state only. The server-side account, database rows, queue messages, rate limits, and feature
flags survive, exactly as with any other runner.

Some suites disable `testIsolation` for a chain of tests that build on one another. That
trades independence for speed and makes any single test unrunnable on its own. Do not turn
it off to make an order-dependent suite pass; fix the dependency.

### Authentication and session reuse

`cy.session` caches and restores a login across tests, keyed by an identifier. Two rules make
it trustworthy:

- Key the session on the actual identity, not a constant. A shared key across tests that
  mutate the account reintroduces exactly the coupling `cy.session` looks like it removed.
- Give it a `validate` callback that makes a real check — an authenticated request, or a
  visit to a protected route. Without validation, an expired session restores silently and
  the failure surfaces somewhere unrelated.

Keep one journey that exercises the real sign-in UI. Others may log in through a controlled
API inside the session setup. Use distinct identities for authorization-boundary tests.

### Waiting and selectors

Cypress commands retry the query and the assertion until timeout, so the correct pattern is
to assert the observable outcome, not to wait for a duration. Two traps:

- `cy.wait('@alias')` on an intercepted route proves a request happened, not that the UI
  finished rendering its result. Assert the rendered state as well.
- Only the last command in a chain retries. A chain that ends in an action rather than an
  assertion can act on a stale element; re-query instead of storing an element in a variable.

Never use `cy.wait(<number>)` as a readiness mechanism. Prefer `cy.findByRole`-style
accessible queries if Testing Library is installed, then `data-cy`/`data-testid` attributes,
and scope with `.within()` on a dialog or row rather than chaining CSS structure.

### Flake diagnosis

Reproduce with `cypress run` — not the interactive runner — at the same spec, browser, and
`--env` that failed, since open mode has different retry and isolation behaviour. Read the
first failure's screenshot, video, and command log together with the server log.

Common Cypress-specific causes: a `cy.session` restored past its expiry, a disabled
`testIsolation` block whose earlier test changed, an `cy.intercept` registered after the
request it meant to catch, an element detached from the DOM between query and action, and
cross-origin navigation that needs `cy.origin`.

## WebdriverIO

### Configuration

Prefer the existing `wdio.conf.*`. The `capabilities` array drives which browsers and
devices run and how many run at once; `maxInstances` interacts with the machine, the
database, and any shared environment, so treat it as a capacity decision, not a speed dial.

Note which automation protocol the suite uses — WebDriver Bidi or classic WebDriver — because
it determines whether network interception, console capture, and other Bidi-only features are
available at all. Services (`services: [...]`) start browsers, drivers, containers, or the
application itself; reuse the repository's existing orchestration rather than starting
infrastructure inside a spec.

### Isolation

WebdriverIO gives each worker a browser session. Sessions are reused across specs within a
worker by default in some configurations — check `specFileRetries`, session-per-spec settings,
and any `beforeSession`/`afterTest` hooks before assuming a clean slate. If the suite relies
on state carried between specs, that is order dependence, and it will surface as a flake as
soon as sharding changes.

Give parallel state-mutating specs separate identities and namespaced data. Worker index is
available through the config and is the natural seed for per-worker test accounts.

### Authentication and session reuse

There is no built-in session-cache primitive. The usual approaches, in decreasing order of
trustworthiness:

- log in through a controlled API in a hook and inject the resulting cookies or storage into
  the session before the first navigation;
- restore a saved storage state written by a setup spec, validated with a real authenticated
  check before use;
- drive the login UI in every spec, which is slow and makes the sign-in page a single point
  of failure for the whole suite.

Whichever is used, saved state can impersonate the test user. Keep it in a gitignored
directory and regenerate it when it expires.

### Waiting and selectors

WebdriverIO auto-waits for an element to exist before interacting, but that is not the same
as waiting for it to be ready. Use the explicit `waitUntil`/`waitForDisplayed`/`waitForEnabled`
commands with a condition describing the observable outcome, and prefer the `expect-webdriverio`
matchers, which retry.

Prefer accessibility-oriented selectors — `aria/Name`, role-based queries — then stable
`data-testid` attributes via `[data-testid="…"]`. Avoid XPath chains and generated class
names. `$$` returns a live query; re-query rather than holding a reference across a navigation.

### Flake diagnosis

Reproduce with the same capability, `maxInstances`, and spec order that failed — running a
single spec alone hides every concurrency and session-reuse cause. Check the driver log
alongside the test log; a session that died mid-spec produces confusing downstream errors that
look like assertion failures.

Common WebdriverIO-specific causes: session reuse carrying state between specs, a stale
element reference after a re-render, a driver/browser version mismatch, `specFileRetries`
masking a real failure, and a service that reports ready before the application is.

## Either runner

After a fix, use the skill's bundled `scripts/repeat-spec.sh` (resolved against the skill
directory, as the skill explains) to turn "it passed once" into a ratio, and report
the repeat count with the result. Reproduce under the concurrency that exposed the failure,
not in isolation.
