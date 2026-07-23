---
name: code-review
description: >-
  Review code changes — working-tree diffs, staged/unstaged changes, a commit, a
  branch vs its base, or a GitHub PR — and judge whether they are correct, safe,
  and ready to merge. Also runs as a guard pass on code an agent just wrote,
  edited, refactored, or fixed before it is presented or committed. Combines a
  senior-engineer bug/security/test hunt, a Clean Code/SOLID/DRY/KISS/YAGNI
  quality rulebook, and an LLM-specific failure-mode layer (hallucinated imports,
  swallowed errors, hardcoded success, dead code). Use whenever the user says
  "review my changes", "review this PR", "check the diff", "any issues before I
  push?", "is this ready to merge?", "LGTM?", "audit this code", or after a
  coding agent produces implementation code. DO NOT USE for test-only diffs (use
  test-guard), docs-only changes (use docs-guard), CI/tooling config, pure
  architecture discussion, debugging a failing test or runtime error (use
  systematic-debugging), pure git workflow, or conceptual/factual questions —
  answer those directly.
---

# Code Review Pro

Review a change the way a strong senior engineer would: spend human attention on
correctness, intent, risk, design, and clarity — and let automation own the
mechanical stuff. A short, high-signal review beats a long speculative one. Find
the bugs **and** communicate so the author actually improves; a review that finds
every defect but demoralizes the author has half-failed, and a kind review that
rubber-stamps a broken change has fully failed.

This skill merges three lenses:

- **The review pass** — discover scope, anchor on intent, hunt for real problems, filter noise, write findings.
- **The quality rulebook** — Clean Code / SOLID / DRY / KISS / YAGNI, applied only where the cost is concrete.
- **The AI failure-mode layer** — the systematic ways LLM-generated code breaks, which generic "follow clean code" advice misses. **If you are an AI agent, [references/ai-failure-modes.md](references/ai-failure-modes.md) is the highest-leverage file here.**

It does **not** run linters, formatters, or type checkers — those are the project's job. Use them for mechanical verification; use this skill for the judgement layer.

## Pick your mode

**Review mode** (default — the user hands you a diff/PR/commit/branch to assess):
walk the [Review workflow](#review-workflow) and produce a findings report. **Do not
edit files** unless the user explicitly asks for fixes.

**Guard mode** (a coding agent just wrote/edited/refactored/fixed code, before it
ships): run the [Guard self-check](#guard-mode-self-check) against the diff and fix
violations before presenting or committing. Use the same hunt lenses and rulebook,
just applied to your own fresh output.

## Pick your output style

Two conventions, chosen by audience — the substance is identical, only the framing changes.

- **Terse findings** (default): dense, personal, `issue / question / suggestion / nitpick`, each with `file:line` + Impact + Fix. Best for "review my changes before I push."
- **Conventional Comments** (for a team PR, a shared branch, or when the user asks for review _comments_): `praise / issue / suggestion / question / nitpick` labels with `(blocking)` / `(non-blocking)` decorations, OIR phrasing, acceptance-criteria table, merge verdict. Talk about _the code_ / _we_, never _you_. Details and label tables in [references/conventional-comments.md](references/conventional-comments.md).

If unsure which to use, default to terse and offer to reformat as PR comments.

## Reference map

Read these on demand — don't front-load them:

| File                                                                           | Read when                                                                               |
| ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| [references/ai-failure-modes.md](references/ai-failure-modes.md)               | **First, if you're an AI agent.** The 14 systematic LLM code defects.                   |
| [references/nodejs-nestjs-failure-modes.md](references/nodejs-nestjs-failure-modes.md) | The diff touches NestJS DI/lifecycle/guards/event handlers, or has tricky Node async shapes. |
| [references/frontend-failure-modes.md](references/frontend-failure-modes.md)   | The diff touches React, Angular, Next.js, or browser JS — hooks, reactivity, races, SSR boundary. |
| [references/naming-and-functions.md](references/naming-and-functions.md)       | A finding touches names, function size, params, or command/query separation.            |
| [references/comments-and-formatting.md](references/comments-and-formatting.md) | Judging comments or whether style matches neighbors.                                    |
| [references/solid.md](references/solid.md)                                     | Subclassing, interfaces, "where does this abstraction live", god-classes.               |
| [references/dry-kiss-yagni.md](references/dry-kiss-yagni.md)                   | Deduplication, the wrong-abstraction trap, complexity ceilings, speculative generality. |
| [references/conventional-comments.md](references/conventional-comments.md)     | Writing in Conventional-Comments style / wording the tone.                              |

## Review workflow

Work these in order. For a non-trivial review, create a todo per step so the user can follow along.

### 1. Discover scope

Pick the narrowest source that matches the request — don't review from memory, read the actual diff:

| Request       | Command                                                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------------------------- |
| GitHub PR     | `gh pr diff <n>` + `gh pr view <n> --json title,body,labels,commits,additions,deletions,files` + `gh pr checks <n>` |
| Staged        | `git diff --staged`                                                                                                 |
| Unstaged      | `git diff`                                                                                                          |
| Local changes | `git status --short`, then both diffs                                                                               |
| Branch        | `git log <base>..HEAD --oneline`, then `git diff <base>...HEAD`                                                     |
| Commit        | `git show <sha>` (and `git show --stat <sha>` for shape)                                                            |
| Unclear       | `git status --short` + both diffs; if empty, `git log -5 --oneline` and ask                                         |

If the target is ambiguous (both staged and unstaged present), default to everything not yet on the base branch and say what you included. Base branch is usually `main`/`master` unless told otherwise.

**Get size and shape first** (files touched, lines changed) before reading line by line — it tells you where risk concentrates.

**Don't stop at the diff.** For orchestrator / command / repository / state-machine changes, open each changed branch's **sibling path** (the success/conflict/other-case variant it lives beside) and any **command or repository methods it calls**, and read PRs referenced in the body. Concentrate risk-reading where a new error/conflict branch diverges from an existing one — that asymmetry is where omission bugs hide.

**Always skip and note:** lock files, generated/bundled output (`dist/`, `*.min.*`, `*.generated.*`), binaries, whitespace-only changes, and dependency bumps without code changes (flag only if security-sensitive).

### 2. Anchor on intent

Before judging the code, establish what it's _supposed_ to do — without this anchor a review degenerates into stylistic nitpicking. Gather intent in order of authority:

1. Acceptance criteria / description the user pasted.
2. PR body and linked ticket (`gh pr view`; follow issue refs).
3. Commit messages and branch name.
4. The diff itself (last resort — infer, and say you're inferring).

State your understanding of the goal at the top of the report so the author can correct you. When acceptance criteria exist, treat each as a checkable line item and end with a coverage table. If you genuinely can't tell what the change is for and it changes the verdict, ask. **An absent description is not a finding** — when none is provided, review only against what the code and project conventions imply; don't invent requirements.

### 3. Learn the project's conventions, then skip what automation owns

Skim what the repo already declares before forming opinions: `CLAUDE.md` / `AGENTS.md`, `CONTRIBUTING`, `README`, any `learnings.md`, and lint/format/TS config (`eslint.config.*`, `.prettierrc`, `tsconfig.json`). Review against _this team's_ agreed conventions, not personal taste.

This tells you what's **already automated**. ESLint, Prettier, commitlint, type checkers, and SonarQube already catch formatting, import order, and many smells — re-flagging those by hand is noise that buries the comments that matter. Mention a style issue only if it isn't lint-enforced _and_ it actively obscures meaning.

**Load the domain contracts the diff leans on.** Generic pattern-matchers (and bot reviewers) miss the highest-value findings because they don't read the invariants a change relies on. Before reviewing, pull: the event/error-code catalog the change emits into, the repository predicates a changed path depends on (e.g. a delete/update filter that intentionally excludes some state), and any sibling PRs named in the description. A branch that looks locally correct is often wrong only against a contract stated elsewhere.

### 4. Hunt for real problems

Spend effort where humans are uniquely good. Walk the happy path **and** the edges for each changed area — read enough surrounding code to know inputs, outputs, side effects, and callers. Use these lenses (full rulebook depth in the reference files):

**Trace, don't skim — this is where the critical bugs live.** The defects a teammate catches and a fast pass misses are almost never visible reading the diff top-to-bottom; they surface only when you run the code in your head against concrete values. Reading code left-to-right makes wrong code look right, because plausible syntax reads as correct intent. So for every changed function that has a branch, a loop, an `await`, a state write, or a non-trivial expression, do this **before** forming an opinion:

1. **Name the cases.** Write the input/state partition the code must handle — `empty / one / many`, `null / present / undefined`, `even / odd`, `first attempt / retry / exhausted`, `success / conflict / timeout`, `already-in-state-X / not`. The bug almost always lives in a case the author didn't picture, so enumerate before you trust.
2. **Run each case by hand.** Follow the actual values through the branch and state what the function returns and which side effects fire (writes, events, job terminations, logs). Compare that to what the intent you anchored on in step 2 says *should* happen. A divergence is a finding — cite the case that breaks it.
3. **Diff the new branch against its sibling.** When the change adds or edits one branch (a new error / conflict / timeout / early-return path), open the branch it lives beside and compare their side effects line by line. If the sibling terminates a job, publishes an envelope, releases a lock, or clears state and the new branch doesn't, that asymmetry is an omission bug — the single highest-yield finding on state-machine and orchestrator code, and the one bots reliably miss.
4. **Follow the calls out one hop.** Read the repository predicate, command handler, event handler, or hook the change depends on. Logic that is locally correct is often wrong against a filter, an invariant, or a contract defined one call away — and that call is where the domain rule your team knows by heart actually lives.

Only after tracing, apply the lenses below.

**Correctness & bugs** — inverted/incomplete conditions, off-by-one, wrong operators, bad defaults; crashes from null/undefined/missing fields/empty collections/failed parsing; async bugs (missing `await`, unhandled promises, stale closures, races, non-atomic read-modify-write); broken public contracts (signatures, response shapes, event names, env vars, migration semantics, config keys callers depend on); error paths that swallow exceptions, drop stack traces, skip cleanup, or return success after failure; state mutated before a fallible operation, leaving partial state on failure.

**Security & privacy** — hardcoded secrets/tokens/keys or realistic test creds; injection (SQL/NoSQL, command, template, XSS, path traversal, unsafe deserialization); missing authz, ownership checks, tenant isolation, or input validation at trust boundaries; sensitive data in logs/traces/errors/telemetry/fixtures/responses; insecure defaults (CORS, open redirects, cookie flags, weak crypto, exposed ports, permissive ACLs); new endpoints/mutations without rate limiting or auth where needed.

**Architecture & project fit** — business logic in the wrong layer (controllers, DTOs, persistence adapters, tests); bypassed abstractions/result-patterns/repositories/validators; new abstractions for a single use case in this diff (premature generalization); changes that make behavior hard to test, observe, or roll back. **If the project is DDD / Hexagonal** (`src/domain/`, `src/application/`, `src/infrastructure/`, Result/Either types, repository ports) apply [the DDD checks](#ddd--hexagonal-checks).

**Tests** — new behavior with no test where failure is plausible and costly; happy-path-only tests when the code added branching/error handling; assertions that only prove a mock was called or an object exists without checking the outcome; tests that pass for the wrong reason (unrealistic setup, expected values mirroring an implementation mistake, over-mocking that tests nothing real). For a test-heavy diff, defer to **test-guard**.

**Maintainability & clean code** — report only when the cost is concrete: duplicated _knowledge_ (not merely similar text) that can diverge; functions doing too many things; names that obscure surprising behavior; dead code, unreachable branches, unused exports added by the change; magic values that belong in named constants. The condensed rulebook is [below](#the-quality-rulebook); depth in [references/naming-and-functions.md](references/naming-and-functions.md), [references/solid.md](references/solid.md), [references/dry-kiss-yagni.md](references/dry-kiss-yagni.md).

**AI failure modes** — the highest-yield lens on generated code: hallucinated/unverified imports and API calls, broad catch-all handlers swallowing errors, hardcoded `{"status":"ok"}` or fixture returns from functions that should do real work, copy-from-similar off-by-one/null-semantic bugs, defensive guards for impossible cases, dead "just in case" code, and tests weakened to pass. Full list and detection cues in [references/ai-failure-modes.md](references/ai-failure-modes.md).

**Framework failure modes** — the bugs that are invisible unless you know the framework's execution model, which is exactly why generic passes miss them and experienced teammates don't. If the diff touches **NestJS** (providers, event/message handlers, guards, interceptors, DI wiring, lifecycle hooks) or has tricky **Node async** shapes, open [references/nodejs-nestjs-failure-modes.md](references/nodejs-nestjs-failure-modes.md) — request state leaking through singleton providers, async lifecycle hooks that aren't awaited, `@OnEvent` handlers that swallow failures past the retry mechanism, guards/interceptors that don't block, plus the async shapes (floating promises, `forEach(async)`, `.catch(()=>{})`) that hide the generic async bugs listed above. If it touches **frontend** (React, Angular, Next.js, or plain browser JS), open [references/frontend-failure-modes.md](references/frontend-failure-modes.md) — stale closures and missing effect deps, unabortable fetch races that render the wrong response, un-torn-down subscriptions/timers, `use client`/server boundary and caching mistakes. Read the file that matches the diff; skip the other.

### 5. Filter findings

Report a finding only when **all** hold:

- You can point to the exact changed or nearby line.
- You understand enough context to avoid guessing.
- You can describe a realistic failure scenario or concrete cost.
- It isn't already prevented by a test, type check, linter, framework guarantee, or invariant you verified.

Suppress: theoretical risks with no plausible path, vague "consider X", style preferences, issues outside the diff, duplicate root causes, and nitpicks unless the user asked for a thorough review. When uncertain, investigate further or mark the finding `[low confidence]` with the specific uncertainty stated. **Don't invent findings — if the diff is clean, say so plainly.**

### 6. Write the review

Pick the [output style](#pick-your-output-style) and use the matching template below. Order findings issues → questions → suggestions → nitpicks, and within each group by impact. Lead with what blocks merge; review all at once (one complete pass, not a dribble). In Conventional-Comments style, leave at least one **genuine** praise — find something real, don't fake it.

## The quality rulebook

Condensed imperatives — the _why_ and citations live in the reference files. Apply where the cost is concrete; flag in review mode, fix in guard mode.

**Functions & names** — Names reveal intent; reject `data2`/`result_final`/`temp`/`helper`/`process_*` without a qualifier. Functions stay small (~≤20 lines, one level of abstraction, one thing). Four arguments is the ceiling — beyond that pass a config/DTO object; no boolean flag args (split the function). A function is a query _or_ a command, not both; no output arguments. → [references/naming-and-functions.md](references/naming-and-functions.md)

**Comments & structure** — Comments explain _why_, never _what_; delete paraphrase comments, step-number scaffolding, and commented-out code. Match the file's existing style — read the file and a neighbor before judging or writing. → [references/comments-and-formatting.md](references/comments-and-formatting.md)

**SOLID** — One actor per module (SRP). Extend via new code, not another type-tag branch (OCP). No subclass that refuses its parent's contract or strengthens preconditions (LSP). Abstractions live with the client that consumes them, not the implementation (DIP). → [references/solid.md](references/solid.md)

**DRY / KISS / YAGNI** — Delete duplicated _knowledge_, not duplicated _text_. The wrong abstraction is worse than duplication — re-inline before re-abstracting. Complexity ceiling: cyclomatic ≤10, nesting ≤5. No speculative parameter, flag, env var, interface, or base class without a present-day caller. → [references/dry-kiss-yagni.md](references/dry-kiss-yagni.md)

**Refactoring discipline** — A refactor preserves observable behavior: same inputs → same outputs, same exceptions, same side effects, same ordering. A bug fix and a refactor are two operations; never bundle them. If you spot a bug while refactoring, flag it separately.

### DDD / Hexagonal checks

Apply only when the project shows the indicators above. These violations are blocking — they erode the architecture's guarantees:

- **Layer integrity** — domain must not import infrastructure or presentation; application depends on domain through interfaces only; infrastructure adapts inward and isn't imported by domain/application; no business logic in controllers, DTOs, or persistence adapters.
- **Domain purity** — aggregates and value objects free of framework decorators, ORM annotations, and HTTP concerns; domain events carry only primitives/value objects; invariants enforced on the aggregate, not only in services/controllers/tests.
- **Result / Either** — `Either`/`Result` returns handled exhaustively (no unchecked `.getValue()` before checking which side); error branches never silently return success; errors extend the base error type and use the established factory if that convention exists.
- **Ports & adapters** — repository ports don't leak persistence types into the domain; controllers don't call infrastructure directly.
- **Coverage** — domain-layer changes require tests (often 100%); application orchestrators tested with mocked ports, not real infrastructure.

### Concurrency, state-machine & terminal-path checks

The highest-value findings on this kind of change are omission- and invariant-shaped: a branch that looks locally correct but diverges from its sibling or admits an illegal state. Bots and shallow passes miss all of these. When a change touches command handlers, orchestrators, or read-modify-write repositories, walk this list — each is blocking:

- **Error/terminal-branch symmetry** — enumerate every `Either` `left`, early `return`, and `catch` in the changed handlers. For each, confirm it performs the _same_ terminal side-effects as its sibling success/conflict path (terminate jobs, publish the decision/failure envelope, claim or delete state). A branch that just returns `left(...)` while its neighbor also terminates + publishes is an omission bug that leaves work permanently pending.
- **No swallowed failure → false success** — an error path must surface failure, not resolve normally. A failed delete/terminate/persist that returns success silently skips the retry mechanism (BullMQ, envelope resubmission) and strands the entity in a non-terminal state.
- **Correct semantic code per branch** — a branch copied from a sibling must not emit the sibling's event/error code for a _different_ transition (e.g. reusing `FLUSH_READY_RETRY_EXHAUSTED` for a later `FLUSH_READY → FLUSHED` failure). Wrong codes make logs, metrics, and downstream consumers unable to distinguish the two failures.
- **State-pair preconditions** — when a write is guarded on multiple fields, check that the predicate models _correlated legal pairs_ (`$or` of `{status, runId}` tuples), not independent `$in` lists whose Cartesian product admits an illegal state (e.g. `IN_PROGRESS + null`). Ask for a negative test proving the illegal pair does not match.
- **Coalescing overwrites** — flag `input.x ?? existing.x` (or `|| existing.x`) in a write payload where a stale or absent value can overwrite an authoritative one already on the primary. Authoritative fields should be omitted from `$set` unless the caller supplies a real value.
- **Stale-read / replication-lag races** — any read that feeds a write filter _or_ an early-return decision under possible secondary lag. Writes must use absolute preconditions from the state machine, not values copied from a prior read; early returns must not bypass the atomic guard below them.
- **Ordering / partial-failure** — don't delete or mutate authoritative state before all dependent fallible effects are confirmed. Deleting a batch before its jobs are known-terminated leaves the jobs unrecoverable.

## Guard mode self-check

Before showing code you wrote or edited, walk this and fix every violation:

1. Walk the [quality rulebook](#the-quality-rulebook) and [AI failure modes](references/ai-failure-modes.md) against your diff.
2. New functions: lines ≤20? params ≤4? complexity ≤10? names reveal intent?
3. New comments: does each explain _why_? If it explains _what_, delete it.
4. New error handling: is the caught type specific? Does the handler do something other than silently return?
5. New abstraction (interface, factory, base class, registry): is there a second concrete user _today_? If not, inline it.
6. Did you read the file you edited and a neighbor, and match the style?
7. Any hardcoded "ok" return or fixture data? Replace with a real implementation or an explicit unimplemented/unsupported failure.
8. Every import / external API call verified to exist in the installed version?
9. If this is a refactor: did you change observable behavior? If yes, you bundled a bug fix — split it and ask.

If you can't answer yes to every check, fix before shipping.

## Report templates

### Terse findings (default)

For each finding:

```
### <Short title>
**Type:** issue | question | suggestion | nitpick
**File:** `path/to/file.ts:42`
**Issue:** What the code does wrong and why — cite the specific line.
**Impact:** The concrete failure, regression, exposure, or cost if left unfixed.
**Fix:** The smallest practical change. Snippet only when it clarifies.
```

End every review with a summary:

- `Findings:` count by type (e.g. `2 issues, 1 question, 1 suggestion`), or `none`
- `Requirements:` `Met` | `Partially met (<n> gaps)` | `Not met` — **only when a description was provided**; omit otherwise
- `Verdict:` `Ready to merge` | `Needs changes` | `Needs rework`
- `Next step:` one concise action, or `none`

When there are no findings:

```
No issues found.
Reviewed: <scope>
Skipped: <files/categories, or "none">
Residual risk: <untested area or assumption, or "none identified">
Verdict: Ready to merge
```

### Conventional Comments (team PR / on request)

```markdown
# Review: <PR #, branch, commit, or "working tree">

**Goal (as I understand it):** <one or two lines; from criteria / PR / inferred>
**Verdict:** <Ready to merge | Needs work | Needs discussion> — <one-line why>
**Scope:** <N files, +X/−Y lines>

## Acceptance criteria coverage

<!-- Only when criteria/description were provided. Omit otherwise. -->

| Criterion   | Status                                             | Evidence / gap      |
| ----------- | -------------------------------------------------- | ------------------- |
| <criterion> | ✅ Met / 🟡 Partial / ❌ Not met / ❓ Can't verify | <file:line or note> |

## Blocking

- **issue(blocking):** `file.ts:42`
  — <observation>
  — <impact>
  — <request>

## Non-blocking

- **suggestion(non-blocking):** `file.ts:88`
  — <observation>
  — <impact>
  — <request>
- **question:** `file.ts:15`
  — <question>

## Manual verification before merge

- <what you couldn't confirm statically and a human should run/check>
```

## Calibration

- **Don't drown the signal.** A long list of trivia reads as hostile and hides real problems. Lead with blockers; keep nitpicks few and clearly non-blocking.
- **Match the change.** A one-line config tweak gets a proportionate review; a new orchestrator gets the full sweep. Don't manufacture findings to look thorough — if it's clean, say so and praise it.
- **Severity is honest.** "Blocking" / "issue" means _don't merge until fixed_ (correctness, security, data loss, unmet acceptance criteria). Don't inflate preferences into blockers.
- **Uncertain? Ask, don't assert.** Use `question:` when you're not sure something is a bug — false alarms stated as fact erode trust.
- **Classless respect.** Same tone whether the code is from a junior or a staff engineer.

## What this skill does not do

- Run linters, formatters, or type checkers — defer to the project's tooling.
- Review test-only diffs (use **test-guard**) or docs-only changes (use **docs-guard**).
- Edit files in review mode unless the user explicitly asks for fixes.
