---
name: e2e
description: Use when creating, extending, or stabilizing end-to-end, browser, smoke, or multi-step workflow tests, including Playwright, Cypress, WebdriverIO, authentication fixtures, test-data isolation, and flaky E2E specs. Do not use for unit, component, load, performance, or code-review tasks.
---

# End-to-End Testing

Build the smallest trustworthy E2E coverage for the user's actual system. Preserve the repository's runner and conventions, isolate state, and report what the tests do and do not prove.

## Choose the operating mode

| Request                                  | Default response                                                                                                                                              |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Add one explicit journey or failure case | Treat the requested scope as approved; extend the existing suite without remapping unrelated journeys.                                                        |
| Stabilize a flaky spec                   | Reproduce and identify the cause before changing retries, timeouts, assertions, or product code.                                                              |
| Create a new or broadly expand a suite   | Inspect the product and environment, propose a journey/testability matrix, and obtain approval before dependencies or test code.                              |
| Test a backend with no UI                | Extend its existing API E2E or integration runner unless the user specifically chooses another runner. Read [references/api-only.md](references/api-only.md). |

Use the runner already established by the repository. Do not replace Cypress, WebdriverIO, Selenium, Jest/Supertest, or another working harness with Playwright merely because this skill is loaded. If no runner exists and the user did not select one, compare choices against the application, languages, browser/mobile needs, CI, and team conventions before recommending one.

For Playwright work, read [references/playwright.md](references/playwright.md). For Cypress or WebdriverIO, read [references/other-runners.md](references/other-runners.md). For hard-to-produce failures or external-system journeys, read [references/testability.md](references/testability.md).

## Inspect before changing

Read repository instructions and identify:

- the package manager, workspace, E2E runner/version, config, scripts, fixtures, and naming conventions;
- the application start/readiness process and required services, containers, environment variables, and CI resources;
- authentication, roles, test identities, server-side state, and existing seed/cleanup paths;
- the user's acceptance criteria and the smallest affected journey, using tickets/specs, routes, forms, existing tests, and product documentation as evidence.

Never run a dependency installer, browser download, infrastructure setup, or CI mutation without authorization. State the exact proposed change and its cost first. Do not test against production or destructively clean shared data unless the user explicitly authorizes the exact environment and operation.

## Scope and coverage

For broad work, present candidate journeys with entry point, business risk, intended assertions, failure cases, and testability. Wait for approval before implementing that broad scope. Do not add a second approval gate when the user already named the exact journey or spec.

Code-coverage policy and E2E scope are separate:

- If the repository or acceptance criteria require 100% unit-test coverage, preserve and verify that requirement with its unit-test coverage tooling. E2E tests do not substitute for missing unit coverage.
- If the repository has no coverage target, do not invent one.
- Describe E2E completeness as covered journeys and risks, including gaps and mocked boundaries, rather than claiming a code-coverage percentage.

Select failure cases from actual risk. Bad input, authorization/session loss, dependency failure, empty data, concurrency, idempotency, and recovery are candidates, not a mandatory checklist for every journey.

## Delegate independent passes

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard, and
require it to return findings with sources — never decisions, conclusions, or writes.
Reconciliation, conflict resolution, the final test code, and every external write stay in
the main agent. If subagents are unavailable or a pass fails, run the same passes
sequentially without reducing coverage.

Here that means mapping candidate journeys across separate areas of the product in
parallel when proposing a suite, or reproducing a suspected flake across several specs at
once. Writing the specs themselves stays in the main agent so conventions and fixtures
stay consistent.

## Implement trustworthy tests

- Assert user- or consumer-visible outcomes, persisted state, and important side effects rather than implementation details.
- Prefer accessible or contract-level selectors, then stable test IDs when necessary. Avoid DOM-position, generated-class, and XPath chains.
- Keep every test independently runnable. Browser contexts isolate browser state, not shared accounts, databases, queues, or external side effects.
- Give parallel state-mutating tests separate identities and namespaced data. Scope cleanup to records created by that test or run; never use a broad delete as teardown.
- Use the real controlled backend for critical happy paths and contract-sensitive behavior. Use mocks or fault injection for rare failures, and label what that boundary no longer proves.
- Protect credentials and saved sessions from source control and logs.
- Replace fixed sleeps with observable readiness or web-first assertions.

For a bug or flaky test, first reproduce the failure under the smallest relevant command. Fix the root cause. Do not manufacture green results with skips, weaker assertions, extra retries, arbitrary sleeps, or unrelated serialization.

### Evidence a flake is fixed

A single passing rerun is not evidence — it is the same reasoning as accepting a passing retry. Use the bundled `scripts/repeat-spec.sh` to turn it into a number:

```bash
<skill-dir>/scripts/repeat-spec.sh -n 20 -- <the exact spec command>
<skill-dir>/scripts/repeat-spec.sh -n 50 --until-fail -- <command>   # while hunting the cause
```

`<skill-dir>` is the directory containing this `SKILL.md`, not your working directory. Resolve it once and use the absolute path; a bare `scripts/…` will not exist relative to the repository under test.

It runs the command N times, reports the pass ratio and which runs failed, and exits non-zero if any failed. Report the actual ratio and the repeat count. State plainly which claim you are making: that the cause was identified and fixed, or that N runs observed no failure — those are different, and only the first is a fix.

## Verify and report

Run the changed E2E specs and directly affected tests by default. Run the complete E2E suite only when the user explicitly requests it; choose workers conservatively for the available machine and shared environment. Also run the repository-required typecheck, lint, build, and relevant test commands, reporting each result accurately.

For a changed spec, verify it independently and repeat it when order dependence or flakiness is plausible. Do not claim cross-browser, real-backend, production, or full-suite confidence unless those exact conditions were verified.

Report:

1. runner/configuration and files changed;
2. journeys, roles, and failure cases covered;
3. real versus mocked boundaries and environment prerequisites;
4. commands actually run with pass/fail results;
5. untested, unreliable, or blocked journeys with a concrete reason and next step.

## Common mistakes

- Installing a preferred runner alongside a healthy existing one.
- Sharing one mutable account across parallel workers.
- Treating retries as a flake fix or a passing retry as clean.
- Running a large full suite after a one-spec change without authorization.
- Claiming E2E tests satisfy a unit-coverage threshold.
- Automating third-party production pages instead of using a sandbox, controlled double, or documented gap.
