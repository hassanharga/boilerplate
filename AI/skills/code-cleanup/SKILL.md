---
name: code-cleanup
description: >-
  Use when auditing or performing approved behavior-preserving cleanup in an
  existing codebase in any language, including dead code, unused dependencies,
  duplication, oversized files, or an unreadable function. Do not use for
  feature work, bug fixes, PR review, performance work, security upgrades, or
  repository housekeeping.
---

# Code Cleanup

Remove maintenance cost without changing supported behavior. Static-analysis
findings are candidates, not deletion proof; current code, public surfaces,
runtime conventions, and repository policy decide what is safe.

## Choose the Mode

| Request                                                         | Mode               | Mutation boundary                               |
| --------------------------------------------------------------- | ------------------ | ----------------------------------------------- |
| Whole repo/package, unknown blast radius, “what can we delete?” | Repository audit   | Read-only; report in chat and stop              |
| User approves IDs from an audit                                 | Approved execution | Only named items                                |
| One named function/file is unreadable or duplicated             | Targeted refactor  | Only the named unit and necessary tests/imports |

If the mode or scope would change what gets edited, ask one focused question.
Stale branches, scratch directories, ignored files, and other filesystem or Git
housekeeping are outside this skill.

## Shared Safety Rules

- Read repository instructions, package/workspace boundaries, public entry
  points, generated-code policy, and the working-tree state first.
- Preserve unrelated local changes. Do not reformat or modernize untouched code.
- Do not install analyzers or dependencies during an audit. Use only tools already
  available through the repository's package manager or environment.
- Do not create branches, stage, commit, push, open a PR, delete untracked files,
  or publish anything unless the user explicitly requests that action.
- Do not rename public exports, route paths, environment variables, CLI flags, or
  package entry points during cleanup.
- A bug discovered during cleanup is a separate behavior change. Report it and
  leave it unless the user separately authorizes a fix.

## Mode 1: Repository Audit

### 1. Establish scope and blind spots

Identify the repository/workspace boundary and every relevant entry point:
`package.json` exports, bins and scripts; framework convention files; dependency
injection and registries; tests, migrations and seeds; CI, Docker, infrastructure,
cron and serverless configuration; published packages and sibling workspaces.

State what static analysis cannot see, especially external consumers, mobile or
partner callers, runtime registration, secret managers, gateways, dashboards,
and repositories outside the selected workspace.

Audit commands must not modify repository files. Do not run an analyzer mode that
writes configuration, fixes findings, updates a baseline, or creates a cache in
the repository. Redirect or disable caches when the tool supports it.

### 2. Detect candidates

Detection is the same four mechanisms in every language. Work through them in order;
the tools are whatever the repository already has.

| Mechanism | What it establishes | What it cannot see |
| --------- | ------------------- | ------------------ |
| **Reachability from entry points** — follow imports, requires, and includes outward from every entry point mapped in step 1 | What is statically reachable | Dynamic loading, reflection, framework discovery, external callers |
| **Compiler and linter diagnostics** already configured in the repository | Unused locals, unreachable branches, unused imports | Only what the project's settings enable |
| **Declaration versus reference counting** — enumerate declared symbols, dependencies, environment variables, and routes, then search for each | Candidates with zero in-repository references | A zero-result search proves what was searched, not that nothing uses it |
| **Similarity** — compare blocks that appear to implement the same rule | Duplication candidates | Similar text is not always the same responsibility |

A semantic analyzer is a shortcut for the first mechanism, not a prerequisite. If the
repository already configures one, use it and save the traversal. If it does not, do the
traversal — do not install anything, and do not report less because a tool was absent.

Read [the TypeScript and JavaScript recipes](references/detection-recipes-ts-js.md) for
that stack, or [the generic recipes](references/detection-generic.md) for any other
language.

Assess only categories relevant to the request, and state which were not assessed:

- unused files, exports, imports, variables, functions, and dependencies;
- unused environment-variable declarations;
- apparently dead routes or handlers;
- commented-out code;
- duplicated business rules;
- oversized units with a clear responsibility seam.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final audit, and every external write
stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means one pass per detection category — unused files and exports, dependencies,
environment variables, routes and handlers, commented-out code, duplication. Each returns
candidates with rerunnable evidence. Clustering, classification, and risk assignment stay
with the main agent, because a candidate is only safe once the whole graph is visible.

### 3. Validate and classify

For every candidate, record a rerunnable command or tool result and inspect the
current code around it. Group dead clusters so partial approval cannot leave a
broken graph. Classify each item without invented percentages:

| Evidence class            | Meaning                                                                                                                      | Audit action                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `safe-candidate`          | Strong static evidence, no known public/dynamic reachability, and a wrong deletion should fail available verification loudly | May be proposed for approval                          |
| `needs-external-evidence` | Reachability may exist outside the static graph or selected repository                                                       | Do not propose deletion yet; name the evidence needed |
| `not-actionable`          | Current evidence shows it is used, generated, intentional, or only superficially similar                                     | Keep it and explain why                               |

Assign risk separately: Low, Medium, or High based on blast radius if the
classification is wrong. Lack of runtime observations is useful only when the
observation window covers representative traffic cycles and relevant tenants,
regions, jobs, and feature states. “No calls seen” without that context is not
deletion evidence.

### 4. Report and stop

Use [the audit template](references/audit-template.md). Report in chat by default.
Do not create `CLEANUP-AUDIT.md` or any other file unless the user requested a
file or approved its location. If a report file is authorized, disclose that it
is the only Phase 1 repository artifact; never claim that no files changed.

Give every proposed change a stable ID. Then stop and ask for approval by ID.
`needs-external-evidence` items require either the named evidence or explicit,
item-specific risk acceptance; blanket approval does not include them.

## Mode 2: Execute Approved Audit Items

### 1. Confirm authorization and baseline

Restate the exact approved IDs and files. Recheck the current head, working tree,
and candidate evidence because code may have changed since the audit.

Before editing, run the repository-defined baseline verification: typecheck,
lint, build, and directly affected tests. Record existing failures exactly. If a
baseline failure prevents proving an approved cleanup safe, stop and ask rather
than guessing.

### 2. Apply the smallest approved changes

Work in dependency order:

1. Remove approved dead clusters, then now-unused imports and symbols.
2. Remove approved dependencies with the existing package manager and review the
   manifest and lockfile diff.
3. Extract approved duplicated logic only when copies implement the same concept
   and behavior. If they have drifted, stop for a behavior decision.
4. Split an approved oversized file only along the documented seam, preserving
   its public import path when consumers depend on it.

Do not add a dependency to perform cleanup, and follow the repository's own testing
and coverage policy.

### 3. Verify incrementally and finally

After each independent cluster, run its directly affected tests and applicable
typecheck/build checks. At the end, run the full project-defined verification
chain: typecheck, lint, build, and directly affected tests unless the repository
or user requires a full suite. Compare failures with the recorded baseline.

Static verification is strong evidence for statically referenced code and weak
evidence for dynamic or external reachability; state that limitation explicitly.
If an item cannot be verified, leave or restore it and report why.

Report ID, files, lines added/removed, verification commands and results, and any
approved item not completed. Leave changes uncommitted unless the user requested
a commit.

## Mode 3: Targeted Behavior-Preserving Refactor

For one named function or file, briefly state the intended seam and why it
improves readability. The user's cleanup request authorizes that bounded edit;
ask only if the approach changes a public contract or expands beyond the named
unit.

Record the applicable verification baseline first. Preserve inputs, outputs,
errors, side effects, ordering, timing assumptions, and public names. Use existing
characterization tests when available; add focused tests when repository policy
requires them or when they are necessary to prove a risky refactor. Do not invent
a coverage target.

Make one coherent structural change at a time and rerun affected verification.
If duplicated copies differ, do not choose a winner under the label “cleanup.”
Surface the behavioral decision and stop.

## References

- [TypeScript and JavaScript recipes](references/detection-recipes-ts-js.md):
  concrete commands, entry-point mapping, and false-positive traps for that stack.
- [Generic recipes](references/detection-generic.md): the same four mechanisms for
  any other language, with per-ecosystem entry points.
- [Audit template](references/audit-template.md): what the report must contain.
