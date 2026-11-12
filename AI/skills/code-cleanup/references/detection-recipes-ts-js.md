# TypeScript and JavaScript Detection Recipes

Use these recipes during a read-only cleanup audit. They identify candidates; they do not prove that deletion is safe.

## Boundaries

- Use only analyzers and dependencies already present in the repository or agent environment. Do not install tools during an audit.
- Use the repository's configured package manager and scripts. Do not inspect `node_modules` directly.
- Read repository instructions before running commands.
- Keep searches inside an explicit repository path. Adjust generated and vendored exclusions to match repository configuration.
- Treat text search as corroboration, not an import-graph substitute.
- Do not use analyzer fix, write, or delete modes during Phase 1.

## Search setup

`rg` respects ignore files. Explicit exclusions also skip committed build output and
generated code. Define them once and reuse the variable in every search below:

```bash
EX=(--hidden
  --glob '!**/{node_modules,bower_components,vendor,dist,build,out,target,.next,.nuxt,.astro,.svelte-kit,.output,.cache,.turbo,coverage,.git}/**'
  --glob '!**/{__generated__,generated}/**')
```

Adjust the list to match the repository's own generated and vendored paths. Use literal
mode, `rg -F`, for an exact package, environment variable, route, or identifier containing
regex characters.

## Tools, when the repository already has them

A semantic analyzer skips the manual traversal; it is not required to run the audit.
Check `package.json` scripts and devDependencies for what is already configured, run it
through the repository's package manager, and if nothing is there, use the searches in
this file instead.

| Question                               | Existing evidence, if configured                    | Important limit                                                             |
| -------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------- |
| Unused files, exports, or dependencies | A dead-code analyzer such as Knip, ts-prune, depcheck | Framework discovery and dynamic imports can create false positives.       |
| Unused locals and unreachable code     | TypeScript and ESLint configured by the repository  | Compiler and lint settings determine coverage.                              |
| Duplicate blocks                       | A clone detector such as jscpd                      | Similar text is not always the same responsibility.                         |
| Dependency declarations                | Package-manager metadata plus a dependency checker  | Build tools, peers, types, scripts, and config-only use need manual checks. |

Analyzer output begins the investigation. Every candidate still needs traceable repository
evidence, whether a tool or a search produced it.

## Map entrypoints before classifying candidates

Check the mechanisms that make code reachable without an ordinary static import:

- package exports, bins, workspaces, and scripts;
- framework modules, decorators, route discovery, dependency injection, and registries;
- dynamic imports, glob imports, reflection, plugins, and barrel files;
- tests, fixtures, migrations, seeds, generators, and CLI commands;
- bundler, compiler, lint, test, deployment, and infrastructure configuration;
- generated-code manifests and code-generation inputs;
- public packages, webhooks, queues, scheduled jobs, and external consumers.

Record anything the repository cannot establish as a blind spot.

## Unused files, exports, and symbols

1. Start with a compiler/linter diagnostic or an analyzer if one is configured; otherwise
   enumerate exports and walk imports outward from the mapped entrypoints.
2. Trace the candidate through aliases, barrels, re-exports, dynamic imports, registries, and framework discovery.
3. Search the exact symbol and import path in source, tests, scripts, and configuration.
4. Check whether the candidate is a public export or extension point.
5. Classify it as safe only when the repository evidence closes the relevant reachability paths.

Example corroborating searches:

```bash
rg -n -F "${EX[@]}" -- 'ExactSymbol' .
rg -n -F "${EX[@]}" -- 'path/to/module' .
```

A zero-result text search does not prove an exported file is unused.

## Dependency candidates

List declared runtime dependencies without assuming every manifest field exists:

```bash
jq -r '(.dependencies // {}) | keys[]' package.json
```

For each analyzer-reported package, use a literal search and inspect:

- imports, requires, dynamic imports, and type-only imports;
- package scripts and executable names that differ from the package name;
- compiler, bundler, lint, test, codegen, and deployment configuration;
- peer dependency and plugin relationships;
- monorepo package boundaries and root-level tooling;
- transitive-looking declarations that are intentionally direct for stability.

Do not edit lockfiles manually. During approved execution, use the repository package manager's removal command and review the resulting manifest and lockfile diff.

## Environment variables and configuration

Search both access sites and declarations:

```bash
rg -n "${EX[@]}" -- 'process\.env|import\.meta\.env|Deno\.env|getenv\(' .
rg -n -F "${EX[@]}" -- 'EXACT_ENV_NAME' .
```

Check schemas, example files, deployment templates, Helm or Terraform, CI variables, secrets documentation, and runtime injection. An environment variable declared only outside the repository is invisible to static analysis. Classify removal as `needs-external-evidence` unless repository ownership is complete and explicit.

Never put environment-variable values or secrets in an audit report.

## Routes, handlers, consumers, and jobs

Enumerate them using the framework's existing metadata, tests, or configured tooling. Then check registration, guards, middleware, queue/topic bindings, schedules, and generated API specifications.

No internal caller does not mean a route, event consumer, webhook, CLI, or scheduled job is dead. Require representative traffic or ownership evidence before removal. State the observation window, environment, and whether it covered normal and seasonal usage.

## Commented-out code

Search for code-like comments, then inspect each match manually:

```bash
rg -n -U -t ts -t js "${EX[@]}" \
  -- '^\s*//\s*(if|for|while|const|let|var|function|class|return|import|export)\b|/\*[\s\S]{80,}?\*/' .
```

Exclude documentation, examples, test explanations, legal headers, generated markers, and intentional lint or type directives. Version control may make disabled implementation redundant, but the surrounding intent still matters.

## Duplication

Use a configured clone detector if there is one. Without one, compare the units that
share a name stem, import the same domain module, or repeat the same literal set. For
each match:

1. Confirm the blocks implement the same concept and change for the same reasons.
2. Compare edge cases, error handling, types, performance constraints, and ownership boundaries.
3. Propose the smallest shared boundary that preserves behavior.
4. Stop if unification would create flags, branching, or an abstraction harder to understand than the duplication.

Do not classify duplication as dead code. Give it a refactor ID and separate verification plan.

## Oversized files and functions

Line count is a prioritization signal, not a defect:

```bash
fd -0 -e ts -e tsx -e js -e jsx . src | xargs -0 wc -l | sort -rn | head -30
```

Before proposing extraction, identify responsibilities, change boundaries, state ownership, tests, and externally visible contracts. A targeted refactor needs a named unit and behavior-preserving verification; it is not blanket cleanup approval.

## Runtime evidence quality

Runtime evidence is useful only when its coverage is credible. Record:

- environment and telemetry source;
- start and end of the observation window;
- traffic volume and relevant user or tenant coverage;
- deployments, feature flags, retries, sampling, and known instrumentation gaps;
- seasonal, scheduled, failover, and low-frequency paths the window may miss.

Absence in an unrepresentative window is not evidence of absence.

## Common false-positive traps

- public exports and external consumers;
- dynamic imports, reflection, registries, dependency injection, and framework discovery;
- config-only dependencies and executable names;
- generated sources and generator inputs;
- tests, fixtures, migrations, seeds, and operational scripts;
- platform-specific, feature-flagged, fallback, recovery, and disaster paths;
- routes, queues, events, webhooks, jobs, and CLIs called from outside the repository;
- monorepo root tooling and cross-package references.

When a trap cannot be closed with repository evidence, classify the item as `needs-external-evidence`, state exactly what would resolve it, and leave it out of blanket approval.
