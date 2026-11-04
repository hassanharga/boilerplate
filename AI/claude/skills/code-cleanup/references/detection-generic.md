# Generic Detection Recipes

Use this when the repository is not TypeScript or JavaScript. The four mechanisms in the
skill are the same everywhere; only the entrypoints and the tools change. These recipes
identify candidates; they do not prove that deletion is safe.

## Boundaries

- Use only tools already present in the repository or environment. Do not install anything
  during an audit.
- Run analyzers through the repository's own build tool or task runner.
- Do not use fix, write, or baseline-update modes during an audit.
- Keep searches inside an explicit repository path.
- Treat text search as corroboration, not an import-graph substitute.

## Search setup

Define the exclusions once and reuse them:

```bash
EX=(--hidden
  --glob '!**/{.git,vendor,third_party,node_modules,target,build,dist,out,bin,obj,.venv,venv,__pycache__,.gradle,.tox,.mypy_cache,coverage}/**')
```

Add the repository's own generated directories. Use `rg -F` for literal identifiers,
package names, and environment variables.

## Entrypoints by ecosystem

Reachability means nothing until you know where execution starts. Map these before
classifying anything.

| Ecosystem | Where execution starts | Non-import reachability to check |
| --- | --- | --- |
| Python | `__main__`, console_scripts in `pyproject.toml`/`setup.cfg`, ASGI/WSGI app objects, Celery tasks, Airflow DAGs | `importlib`, entry-point plugins, Django app/URL/settings discovery, pytest fixtures and conftest, `getattr` dispatch |
| Go | `func main` per `cmd/`, `TestMain`, `//go:generate` | `init()` side effects, blank imports, interface satisfaction, reflection, build tags |
| Java / Kotlin | `main`, Spring `@SpringBootApplication`, servlet and JAX-RS registrations | Annotation and classpath scanning, `ServiceLoader`, DI modules, reflection by class name, resource bundles |
| Rust | `main.rs`, `[[bin]]`, `[[example]]`, `#[test]` | Feature flags, `cfg` attributes, macro expansion, trait impls used only generically |
| Ruby | `bin/`, Rack `config.ru`, Rails initializers, Rake tasks | Autoloading, `const_missing`, metaprogramming, `send`, gem plugin hooks |
| PHP | front controller, console commands | Autoload maps, container definitions, attribute/annotation routing, magic methods |
| C# | `Main`, ASP.NET startup, hosted services | Reflection, DI registration, source generators, `InternalsVisibleTo` |
| C / C++ | `main`, exported symbols in the build files | Preprocessor conditionals, linker scripts, weak symbols, `dlopen` |
| SQL / migrations | migration runner order | Views, triggers, scheduled jobs, external reporting consumers |
| Infrastructure | pipeline and deployment definitions | Modules referenced by path, workflow reuse, cron and serverless triggers |

Also check, in every ecosystem: tests and fixtures, build and packaging manifests, CI and
deployment configuration, container entrypoints, scheduled jobs, message-queue consumers,
webhooks, generated-code inputs, and anything published to another repository.

Record what the repository cannot establish as a blind spot.

## 1. Reachability from entry points

Walk the import, include, or module graph outward from every mapped entrypoint. Anything
never reached is a candidate — never a conclusion, because dynamic loading and framework
discovery are exactly what a static walk misses.

Most ecosystems ship a graph tool that is already installed with the toolchain rather than
added as a project dependency: a build tool's dependency report, a module-listing command,
or the compiler's own import resolution. Use it if it is there.

## 2. Compiler and linter diagnostics

Run the repository's configured build and lint with its existing settings, and read the
warnings it already emits: unused variables, imports, parameters, unreachable branches,
dead stores. Do not raise the strictness level to manufacture findings — a warning the
project has deliberately disabled is not an audit finding.

## 3. Declaration versus reference counting

Enumerate what is declared, then search for each name.

```bash
# Declared dependencies, per manifest format
rg -n '^\s*[a-zA-Z0-9._-]+\s*[=><~]' requirements.txt         # Python
rg -n '^\s+' go.mod                                            # Go
rg -n '<artifactId>' pom.xml                                   # Maven
rg -n '^\s*(implementation|api|compileOnly)' build.gradle*     # Gradle
rg -n '^[a-zA-Z0-9_-]+ = ' Cargo.toml                          # Rust
rg -n '^\s+' Gemfile                                           # Ruby
```

Then, for each name, a literal search across source, tests, scripts, and configuration:

```bash
rg -n -F "${EX[@]}" -- 'exact_name' .
```

A package can be used without its name appearing in an import: a build plugin, a binary
invoked from a script, a transitive pin held deliberately, a runtime driver loaded by
string. Check those before proposing removal.

Environment variables follow the same shape — find the read sites, then search each name:

```bash
rg -n "${EX[@]}" -- 'os\.environ|getenv|System\.getenv|ENV\[' .
rg -n -F "${EX[@]}" -- 'EXACT_ENV_NAME' .
```

A variable declared only in a deployment system outside the repository is invisible here.
Classify it `needs-external-evidence`. Never put a value or secret in the report.

## 4. Similarity

Without a clone detector, compare the units that share a name stem, import the same domain
module, or repeat the same literal set. For each match:

1. Confirm the blocks implement the same concept and change for the same reasons.
2. Compare edge cases, error handling, types, performance constraints, and ownership.
3. Propose the smallest shared boundary that preserves behavior.
4. Stop if unification would create flags, branching, or an abstraction harder to
   understand than the duplication.

Duplication is a refactor candidate with its own ID and verification plan, never dead code.

## Commented-out code

```bash
rg -n "${EX[@]}" \
  -- '^\s*(#|//|--)\s*(if|for|while|def|func|class|return|import|from|public|fn|end)\b' .
```

Inspect every match. Exclude documentation, examples, test explanations, legal headers,
generated markers, and intentional lint or type directives.

## Oversized units

```bash
fd -0 -t f -e py -e go -e java -e rb -e rs . src | xargs -0 wc -l | sort -rn | head -30
```

Line count prioritizes; it does not prove a defect. Before proposing extraction, identify
responsibilities, change boundaries, state ownership, tests, and externally visible
contracts.

## Runtime evidence quality

Runtime evidence is useful only when its coverage is credible. Record the environment and
telemetry source, the observation window, traffic volume and tenant coverage, deployments
and feature flags in effect, sampling and instrumentation gaps, and the seasonal,
scheduled, failover, and low-frequency paths the window may miss.

Absence in an unrepresentative window is not evidence of absence.

## Common false-positive traps

- public API, exported symbols, and consumers in other repositories;
- reflection, dynamic loading, service discovery, DI containers, and plugin registries;
- build plugins, codegen inputs, and dependencies used only in configuration;
- tests, fixtures, migrations, seeds, and operational scripts;
- platform-specific, feature-flagged, fallback, recovery, and disaster paths;
- routes, queues, events, webhooks, jobs, and CLIs called from outside the repository;
- monorepo root tooling and cross-package references.

When a trap cannot be closed with repository evidence, classify the item as
`needs-external-evidence`, state exactly what would resolve it, and leave it out of
blanket approval.
