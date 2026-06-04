---
name: review-changes
description: Review code changes, staged/unstaged diffs, commits, branches, or GitHub pull requests. Invoke whenever the user asks to review code, check a PR, inspect a commit or branch, look for bugs, assess code quality, verify conventions, or wants merge readiness feedback — phrases like "review my changes", "check this PR", "any issues?", "LGTM?", "what's wrong here?", "review before I push", "look at this commit", "review the diff", or "is this ready to merge?" all warrant this skill. Use this even if the request is casual or brief.
---

# Review Changes

Review as a senior engineer focused on issues that actually matter after merge. A short, high-signal review beats a long speculative one.

## Review Contract

- Lead with findings — do not bury issues under preamble.
- Review changed behavior and the minimum surrounding context needed to understand it.
- Prefer concrete failure scenarios over abstract advice.
- Skip formatting, lint, and style unless they are project-enforced and not auto-fixed.
- Do not invent findings. If the diff is clean, say so plainly.
- Do not edit files during a review unless the user explicitly asks for fixes.

## 1. Discover Scope

Pick the narrowest source that matches the request:

| Request | Command |
|---------|---------|
| PR | `gh pr diff <number>` + `gh pr view <number>` |
| Staged | `git diff --cached` |
| Unstaged | `git diff` |
| Local changes | `git status --short`, then both diffs |
| Branch | `git log main..HEAD --oneline`, then `git diff main...HEAD` |
| Commit | `git show <sha>` |
| Unclear | `git status --short` + both diffs; if empty, `git log -5 --oneline` and ask |

**Always skip and note:** lock files, generated/bundled output (`dist/`, `*.min.*`, `*.generated.*`), binary files, whitespace-only changes, and dependency bumps without code changes (flag if security-sensitive).

## 2. Build Context

For each meaningful changed area:

1. Identify the changed function, class, endpoint, schema, command, or test.
2. Read enough surrounding code to understand inputs, outputs, side effects, and callers.
3. Check how the code handles errors, nulls, empty collections, async behavior, retries, transactions, and external services.
4. Compare tests against changed behavior — look for missing negative paths, boundary conditions, and assertions that don't actually prove the outcome.
5. Read project guidance files (`CLAUDE.md`, `AGENTS.md`, `README.md`, lint config, test config, architecture docs) and apply their conventions only to the diff in scope.

## 3. Detect Project Architecture

Before reviewing, check whether the project follows a structured architecture.

**DDD / Hexagonal indicators** — look for:
- `src/domain/` with aggregates, value objects, or domain events
- `src/application/` with use cases or orchestrators
- `src/infrastructure/` with adapters or repositories
- `src/presentation/` with controllers or handlers
- Result/Either types for error handling (`right()`, `left()`, `Result.ok()`)
- Repository interfaces or driven ports

If any of these are present, apply **Section 3a** in addition to the general checks below.

### 3a. DDD / Hexagonal Architecture Checks

These violations are blocking — they erode the architecture's core guarantees.

**Layer integrity**
- Domain must not import from infrastructure or presentation.
- Application must depend on domain through interfaces only — not directly on infrastructure.
- Infrastructure adapts inward; it must not be imported by domain or application directly.
- Business logic must not live in controllers, DTOs, or persistence adapters.

**Domain purity**
- Aggregates and value objects must be free of framework decorators, ORM annotations, and HTTP concerns.
- Domain events should carry only primitive values or value objects.
- Invariants that belong on the aggregate must not be enforced in services, controllers, or tests only.

**Result / Either pattern**
- Functions returning `Either` or `Result` must be handled exhaustively — no unchecked `.getValue()` without verifying which side first.
- Error branches must not silently return success.
- Errors should extend the project's base error type and use the established `static create()` factory pattern if that convention exists.

**Ports and adapters**
- Driven ports (repository interfaces) must not expose persistence-layer types into the domain.
- Driving adapters (controllers) must not call infrastructure directly.

**Test coverage**
- Domain layer changes require tests — this layer typically demands 100% coverage.
- Application orchestrators should be tested with mocked ports, not real infrastructure.

## 4. Hunt For Real Problems

### Bugs and Regressions
- Inverted or incomplete conditions, off-by-one errors, wrong operators, bad defaults.
- Crashes from `null`, `undefined`, missing fields, empty arrays, or failed parsing.
- Async bugs: missing `await`, unhandled promises, stale closures, race conditions, non-atomic read-modify-write flows.
- Broken public contracts: changed signatures, response shapes, event names, env vars, migration semantics, config keys that callers depend on.
- Error paths that swallow exceptions, drop stack traces, skip cleanup, or return success after failure.
- External calls, DB operations, file I/O, queues, and transactions without correct failure and rollback behavior.
- State mutations that happen before a fallible operation, leaving the system in a partial state on failure.

### Security and Privacy
- Hardcoded secrets, tokens, private keys, or realistic-looking test credentials.
- Injection risks: SQL/NoSQL, command, template, XSS, path traversal, unsafe deserialization.
- Missing authorization, ownership checks, tenant isolation, or input validation at trust boundaries.
- Sensitive data in logs, traces, errors, telemetry, snapshots, fixtures, or API responses.
- Insecure defaults: CORS policies, open redirects, cookie flags, weak crypto, exposed ports, permissive ACLs.
- New endpoints or mutations without rate limiting, authentication, or authorization where needed.

### Architecture and Project Fit
- Layer violations or dependency direction reversals (see Section 3a for DDD projects).
- Business logic in the wrong layer — controllers, DTOs, persistence adapters, or tests.
- Bypassing established abstractions, result/error patterns, repositories, validators, or module wiring.
- Changes that make behavior hard to test, observe, roll back, or reason about.
- New abstractions introduced for a single use case in this diff (premature generalization).

### Tests
- New behavior with no tests where a failure would be plausible and costly.
- Happy-path-only tests when the changed code adds branching or error handling.
- Assertions that only verify a mock was called, a snapshot changed, or an object exists — without checking the actual outcome.
- Tests that pass for the wrong reason: unrealistic setup, expected values that mirror implementation mistakes, or tests tightly coupled to internal implementation.
- Integration tests that should be unit tests (slow, fragile), or unit tests mocking so much they test nothing real.

### Maintainability
Report only when the cost is concrete:
- Duplicated logic introduced by this diff that can diverge independently.
- Functions or methods that do too many things, making the changed behavior hard to understand or test.
- Names that obscure a non-obvious or surprising behavior.
- Dead code, unreachable branches, or unused exports added by the change.
- Magic values, hardcoded limits, or implicit assumptions that belong in named constants or config.

## 5. Filter Findings

Report a finding only when all of these hold:
- You can point to the exact changed or nearby line.
- You understand enough surrounding context to avoid guessing.
- You can describe a realistic failure scenario or concrete cost.
- The issue is not already prevented by a test, type check, linter, framework guarantee, or upstream invariant you verified.

Suppress: theoretical risks with no plausible path, vague "consider X" advice, personal style preferences, issues outside the requested diff, duplicate root causes, and nitpicks unless the user asked for thorough review.

When uncertain, investigate further or flag the finding as `[low confidence]` with the specific uncertainty stated.

## 6. Write The Review

Order findings: issues → questions → suggestions → nitpicks. Within each group, order by impact.

For each finding:

```
### <Short title>

**Type:** issue | question | suggestion | nitpick
**File:** `path/to/file.ts:42`
**Issue:** What the code does wrong and why — cite the specific line or snippet.
**Impact:** The concrete failure, regression, exposure, or cost if left unfixed.
**Fix:** The smallest practical change. Include a snippet only when it clarifies.
```

**Type definitions:**
- **issue** — actual bug, regression, security vulnerability, architectural violation, or missing critical test. Must be resolved before merge.
- **question** — something unclear or ambiguous that needs clarification before a verdict. May turn out to be fine, may reveal a bug.
- **suggestion** — not a bug, but a meaningful improvement worth doing. Non-blocking.
- **nitpick** — minor style, naming, or preference issue. Skip unless the user requested exhaustive review.

## Clean Review Output

When there are no findings:

```
No issues found.

Reviewed: <scope>
Skipped: <files/categories, or "none">
Residual risk: <untested area or assumption, or "none identified">
Verdict: Ready to merge
```

## Review Summary

End every review with:

- `Findings:` count by type (e.g. `2 issues, 1 question, 1 suggestion`), or `none`
- `Verdict:` `Ready to merge` | `Needs changes` | `Needs rework`
- `Next step:` one concise action, or `none`

**Verdict guide:**
- **Ready to merge** — no issues or open questions.
- **Needs changes** — at least one `issue` or unresolved `question` must be addressed first.
- **Needs rework** — structurally unsafe, hard to review reliably, or multiple serious root-cause problems.
