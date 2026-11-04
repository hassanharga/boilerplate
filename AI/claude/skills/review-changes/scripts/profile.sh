#!/usr/bin/env bash
# Detect a repository's review profile from its own files.
#
# Usage: profile.sh <repo-dir> [out.json] [--files changed-files.txt]   (prints to stdout when out.json is omitted)
#
# Prints JSON: languages, frameworks, package managers, project commands (lint,
# typecheck, build, test), single-test hints, test/coverage config, agent instruction
# files, monorepo and architecture signals, and the stack references that apply.
# Read-only: it lists and reads files, and never runs project commands.
set -euo pipefail

case "${1:-}" in -h|--help|"") sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; [[ -n "${1:-}" ]]; exit $? ;; esac
dir="$(cd "${1:?repo dir required}" && pwd -P)"; shift
out=""; files=""
while [[ $# -gt 0 ]]; do
  case "$1" in --files) files="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${2:?files required}")"; shift 2 ;;
    *) [[ -z "$out" ]] || { echo "unexpected argument: $1" >&2; exit 2; }; out="$1"; shift ;; esac
done
helper="$(cd "$(dirname "$0")" && pwd -P)/workspace-profile.py"
if [[ -n "$out" ]]; then
  out="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$out")"
  case "$out/" in "$dir"/*) echo "profile output must be outside the reviewed directory" >&2; exit 2 ;; esac
fi
command -v jq >/dev/null || { echo "jq is required" >&2; exit 2; }
cd "$dir"

has() { [[ -e "$1" ]]; }
found() { local f; for f in "$@"; do has "$f" && echo "$f"; done; return 0; }
arr() { jq -R . | jq -s 'map(select(length > 0)) | unique'; }
# Search two levels deep without descending into dependency or build folders.
shallow() { find . -maxdepth 3 \( -name node_modules -o -name .git -o -name vendor -o -name dist \
  -o -name build -o -name .venv -o -name target \) -prune -o -name "$1" -print 2>/dev/null | sed 's#^\./##'; }

langs=(); frameworks=(); pms=(); refs=()
has package.json && langs+=(javascript)
{ has tsconfig.json || [[ -n "$(shallow 'tsconfig*.json' | head -1)" ]]; } && langs+=(typescript)
{ has pyproject.toml || has setup.py || has requirements.txt || has setup.cfg; } && langs+=(python)
has go.mod && langs+=(go)
{ has pom.xml || has build.gradle || has build.gradle.kts; } && langs+=(java-or-kotlin)
has Cargo.toml && langs+=(rust)
has Gemfile && langs+=(ruby)
[[ -n "$(shallow '*.csproj' | head -1)" ]] && langs+=(dotnet)
has composer.json && langs+=(php)

has pnpm-lock.yaml && pms+=(pnpm); has yarn.lock && pms+=(yarn)
has package-lock.json && pms+=(npm); { has bun.lockb || has bun.lock; } && pms+=(bun)
has poetry.lock && pms+=(poetry); has uv.lock && pms+=(uv); has Pipfile.lock && pms+=(pipenv)
has go.sum && pms+=(go); has Cargo.lock && pms+=(cargo); has Gemfile.lock && pms+=(bundler)
has pom.xml && pms+=(maven); { has build.gradle || has build.gradle.kts; } && pms+=(gradle)

pkg_deps='{}'
if has package.json; then
  pkg_deps="$(jq '(.dependencies // {}) + (.devDependencies // {})' package.json)"
  dep() { jq -e --arg d "$1" 'has($d)' <<<"$pkg_deps" >/dev/null; }
  dep @nestjs/core && frameworks+=(nestjs)
  dep next && frameworks+=(nextjs); dep react && frameworks+=(react)
  dep @angular/core && frameworks+=(angular); dep vue && frameworks+=(vue)
  dep express && frameworks+=(express); dep fastify && frameworks+=(fastify)
  dep jest && frameworks+=(jest); dep vitest && frameworks+=(vitest)
  dep @playwright/test && frameworks+=(playwright); dep cypress && frameworks+=(cypress)
  jq -e '[(.dependencies // {}), (.devDependencies // {})] | add | keys | any(startswith("@yatechnologies/"))' \
    package.json >/dev/null 2>&1 && frameworks+=(yassir-mobility-chassis)
fi
if has pyproject.toml || has requirements.txt; then
  pyfiles="$(cat pyproject.toml requirements*.txt 2>/dev/null || true)"
  grep -qiE '^\s*"?django' <<<"$pyfiles" && frameworks+=(django)
  grep -qiE '^\s*"?fastapi' <<<"$pyfiles" && frameworks+=(fastapi)
  grep -qiE '^\s*"?flask' <<<"$pyfiles" && frameworks+=(flask)
  grep -qiE 'pytest' <<<"$pyfiles" && frameworks+=(pytest)
fi
has go.mod && grep -qE 'gin-gonic|labstack/echo|go-chi' go.mod && frameworks+=(go-http)

# Commands come from the project's own scripts; nothing is invented.
commands='{}'
if has package.json; then
  pm="${pms[0]:-npm}"; [[ "$pm" == npm ]] && run="npm run" || run="$pm"
  commands="$(jq --arg run "$run" '(.scripts // {}) | to_entries
    | map(select(.key | test("^(lint|typecheck|type-check|tsc|check|build|test|test:unit|test:integration|test:e2e|test:component|format:check)$")))
    | map({key, value: {command: ($run + " " + .key), runs: .value}}) | from_entries' package.json)"
fi
make_targets="$( (has Makefile && grep -oE '^[a-zA-Z0-9_.-]+:' Makefile | tr -d : | grep -E '^(lint|test|build|check|typecheck|fmt|vet)$') || true)"
just_targets="$( (has justfile && grep -oE '^[a-zA-Z0-9_-]+' justfile | grep -E '^(lint|test|build|check|typecheck)$') || true)"

# Conventional commands for ecosystems without a script file. They are hints: confirm
# them against the instruction files before running anything.
conventions=()
has go.mod && conventions+=("go build ./..." "go vet ./..." "go test ./...")
has Cargo.toml && conventions+=("cargo build" "cargo clippy" "cargo test")
if has pyproject.toml || has setup.py || has requirements.txt; then
  if grep -qs pytest pyproject.toml requirements*.txt setup.cfg pytest.ini tox.ini; then conventions+=("python -m pytest")
  else conventions+=("python -m unittest discover"); fi
  grep -qs '\[tool.ruff' pyproject.toml && conventions+=("ruff check .")
  grep -qs '\[tool.mypy' pyproject.toml && conventions+=("mypy .")
fi
has pom.xml && conventions+=("mvn -q verify")
{ has build.gradle || has build.gradle.kts; } && conventions+=("./gradlew check")

test_configs="$(found jest.config.js jest.config.ts jest.config.cjs jest.config.mjs vitest.config.ts \
  vitest.config.js pytest.ini tox.ini setup.cfg .mocharc.json playwright.config.ts cypress.config.ts | arr)"
coverage_hint="$( (grep -hoE 'coverageThreshold|branches"?\s*:\s*[0-9]+|fail_under\s*=\s*[0-9]+|--cov-fail-under[= ][0-9]+' \
  jest.config.* vitest.config.* package.json pyproject.toml setup.cfg tox.ini .coveragerc 2>/dev/null || true) | sort -u | arr)"
lint_configs="$(found eslint.config.js eslint.config.mjs .eslintrc .eslintrc.js .eslintrc.json biome.json \
  .golangci.yml ruff.toml .ruff.toml .flake8 .pylintrc .rubocop.yml | arr)"
instructions="$( (found AGENTS.md CLAUDE.md CONTRIBUTING.md .github/CONTRIBUTING.md \
  .github/copilot-instructions.md learnings.md; shallow AGENTS.md; shallow CLAUDE.md) | arr)"
ci="$( (found .github/workflows .gitlab-ci.yml .circleci azure-pipelines.yml Jenkinsfile bitbucket-pipelines.yml) | arr)"
monorepo="$(found pnpm-workspace.yaml turbo.json nx.json lerna.json go.work rush.json | arr)"
has package.json && jq -e '.workspaces' package.json >/dev/null 2>&1 && monorepo="$(jq '. + ["package.json#workspaces"]' <<<"$monorepo")"

arch=()
for layer in domain application infrastructure presentation; do
  [[ -n "$(find . -maxdepth 3 \( -name node_modules -o -name .git -o -name vendor \) -prune -o -type d -name "$layer" -print 2>/dev/null | head -1)" ]] && arch+=("$layer")
done
architecture="$(printf '%s\n' "${arch[@]:-}" | arr)"
[[ "$(jq length <<<"$architecture")" -ge 3 ]] && arch_style="layered-or-hexagonal" || arch_style="unclassified"

fw=" ${frameworks[*]:-} "
[[ "$fw" == *" nestjs "* && "$fw" == *" yassir-mobility-chassis "* ]] && refs+=(yassir-nestjs-ddd.md)
[[ "$fw" =~ " "(react|nextjs|angular|vue)" " ]] && refs+=(frontend.md)

single_test=""
[[ "$fw" == *" jest "* ]] && single_test="jest accepts a path pattern; confirm the script forwards it and that zero matches is not a pass"
[[ "$fw" == *" vitest "* ]] && single_test="vitest run <file>"
[[ "$fw" == *" pytest "* ]] && single_test="pytest <path>::<test>"
has go.mod && single_test="go test ./<pkg> -run <TestName>"

profile="$(jq -n \
  --arg root "$dir" \
  --argjson languages "$(printf '%s\n' "${langs[@]:-}" | arr)" \
  --argjson frameworks "$(printf '%s\n' "${frameworks[@]:-}" | arr)" \
  --argjson package_managers "$(printf '%s\n' "${pms[@]:-}" | arr)" \
  --argjson scripts "$commands" \
  --argjson make_targets "$(printf '%s\n' "$make_targets" | arr)" \
  --argjson just_targets "$(printf '%s\n' "$just_targets" | arr)" \
  --arg single_test "$single_test" \
  --argjson conventions "$(printf '%s\n' "${conventions[@]:-}" | arr)" \
  --argjson test_configs "$test_configs" --argjson coverage_hints "$coverage_hint" \
  --argjson lint_configs "$lint_configs" --argjson instructions "$instructions" \
  --argjson ci "$ci" --argjson monorepo "$monorepo" \
  --argjson architecture_dirs "$architecture" --arg architecture_style "$arch_style" \
  --argjson stack_references "$(printf '%s\n' "${refs[@]:-}" | arr)" \
  '{root: $root, languages: $languages, frameworks: $frameworks, package_managers: $package_managers,
    commands: {scripts: $scripts, make: $make_targets, just: $just_targets,
      conventional_unconfirmed: $conventions, single_test_hint: $single_test},
    test_configs: $test_configs, coverage_hints: $coverage_hints, lint_configs: $lint_configs,
    instruction_files: $instructions, ci: $ci, monorepo: $monorepo,
    architecture: {dirs: $architecture_dirs, style: $architecture_style},
    stack_references: $stack_references}')"

profile="$(printf '%s\n' "$profile" | python3 "$helper" "$dir" ${files:+"$files"})"
if [[ -n "$out" ]]; then printf '%s\n' "$profile" >"$out"; else printf '%s\n' "$profile"; fi
