# Review Workflow

Use this reference for every review. The objective is a complete, evidence-led
comparison, not a checklist-shaped performance.

Follow the [evidence lifecycle](evidence-lifecycle.md) for packet integrity,
old/new snapshots, and stage invalidation.

## Resolve the target

| Target              | Evidence to resolve                                                     |
| ------------------- | ----------------------------------------------------------------------- |
| GitHub pull request | Repository, PR number, base SHA, head SHA, changed files, complete diff |
| Branch              | Intended review/integration base, merge base, current head             |
| Commit              | Exact commit and selected parent; empty tree for a root commit          |
| Staged              | Index diff                                                              |
| Unstaged            | Working-tree diff                                                       |
| Local changes       | Status plus staged, unstaged, and untracked files                       |

Use an available connector, API, or CLI. Tool names are runtime-specific; the
evidence contract is not. Preserve unrelated local changes and do not switch
branches merely to review.

Resolve a branch's review base from the explicit request or its PR target.
Tracking upstream may be the remote copy of the same feature branch; do not use
it as the review base unless it represents the requested comparison. If the
integration target remains ambiguous, establish it with the user before judging
the diff. For merge commits, establish which parent comparison the user intends;
do not silently substitute a combined diff that can omit changes against a parent.

For PRs, collect metadata, PR body, checks, commits, file list, patches, existing
reviews, review comments, and thread resolution. Paginate APIs where required.
Confirm that the diff is complete: large PR limits, renamed files, binary files,
submodules, generated outputs, and truncated patches can otherwise disappear.

For local changes, inspect untracked files directly because ordinary `git diff`
does not include their contents. State the comparison base and any excluded
files in the report.

Bind source reads and local verification to the reviewed snapshot: the selected
commit, index contents for staged work, or captured working-tree/untracked contents
for local work. Surrounding code and tests must come from that same snapshot.
A working-tree test can pass while the staged version is broken. Use a permitted
isolated snapshot when necessary, without switching branches or changing the user's
index or files. If a check runs on a different version, label that version and do
not count its result as a pass for the target. Record commit/blob identities or
content hashes for mutable inputs and recheck them before the report; reconcile
changes or explicitly limit conclusions to the recorded snapshot.

## Establish intent before judging implementation

The gate itself is in step 1 of the skill's Review Contract. This is the source
precedence it selects from:

1. User-supplied acceptance criteria or specification.
2. Jira or issue content available through an authorized connector/API.
3. PR description.
4. Commit messages and branch name.
5. Explicitly stated inference from the changed behavior.

Take the highest source actually available and name it in the report. A read-only
ticket lookup does not authorize Jira mutations.

## Read project rules before generic guidance

Read applicable `AGENTS.md`, `CLAUDE.md`, contributing guides, architecture
documents, test configuration, package manifests, and path-specific
instructions. More specific project rules win. A guideline that does not match
the project version, architecture, or path is not evidence.

## Apply the guideline freshness gate

Treat cached references as investigation prompts. A rule is stale for the
current review when its version or architecture does not match, version-matched
official evidence contradicts it, or its factual claim cannot be refreshed from
authoritative evidence. A new technology or version is a maintenance candidate
only when the review proves a reusable cross-project prompt or principle; do not
copy ordinary product documentation into the skill.

When the gate triggers:

1. exclude the cached claim from findings and use current project evidence;
2. continue the review without waiting for anything to be fixed;
3. report it as a `Guidance:` line following
   [stale guideline reporting](guideline-maintenance.md);
4. keep the reviewed repository, this skill's own references, and Review mode
   read-only.

## Build a change map

The map does double duty: it forces you through the changed behavior before you
judge it, and it is what the reader sees in Summary to understand the PR. Render
it per the output contract — ASCII in a terminal, Mermaid on a GUI surface.

For each changed area, identify:

- externally visible behavior or contract;
- data representations crossing boundaries;
- state mutations and side effects;
- error, retry, cancellation, and rollback paths;
- configuration, deployment, migration, and compatibility requirements;
- tests and checks intended to protect it.

Note the entry point and the order you traced each flow in, with the exact
`path:line` of each stop. That trace becomes the Review path in the report.
Before judging, check it against the diff: every changed hunk sits on a flow
stop or belongs on the Skim line. A hunk on neither is behavior you have not
traced yet; trace it, or name it as unreviewed in the Verdict.

Open enough surrounding and sibling code to trace the scenario. Do not infer a
contract from a diff hunk when the caller, interface, schema, or adjacent branch
can establish it.

## Review all changed artifact types

- **Production code:** logic, contracts, failure paths, concurrency, security,
  performance, observability, compatibility.
- **Tests:** weakened or tautological assertions, incorrect mocks, missing
  negative paths, tests that cannot fail when production behavior regresses.
- **CI and build:** skipped checks, permissive failure flags, wrong paths,
  secret exposure, environment drift.
- **Configuration and deployment:** defaults, environment parity, rollout
  prerequisites, flags, topics, IAM, migrations, rollback.
- **Dependencies and lockfiles:** intended version, manifest/lock consistency,
  runtime compatibility, unexpected package or script changes.
- **Documentation and contracts:** examples, API semantics, operational steps,
  user-visible promises. Review prose only when it changes behavior or guidance.
- **Generated artifacts:** verify source-of-truth consistency; avoid reviewing
  machine formatting as handwritten logic.

## JavaScript and TypeScript lens

When relevant, pay particular attention to:

- promises that are neither awaited, returned, nor deliberately handled;
- `forEach(async ...)`, dropped `map(async ...)` results, and unintended
  sequential or unbounded parallel I/O;
- runtime data asserted with `as` but never parsed or validated;
- catch values used without narrowing and wrapped errors that lose their cause;
- config/env keys absent from validation and deployment declarations;
- imports or APIs not present in the project’s installed major version;
- `||` versus `??`, truthiness of `0`/empty string, and changed null semantics;
- tests that assert only mock calls, truthiness, or definedness when a concrete
  value or side effect is the contract.

Analyzer output and type systems are evidence, not proof of runtime behavior.
Verify unfamiliar or version-sensitive APIs against official documentation or
source rather than inspecting `node_modules` or trusting memory.

## Check and deduplicate existing feedback

Do this after your own draft findings exist, not before (see step 2 of the skill).
`scripts/collect.sh` already fetched every thread with pagination into
`existing-feedback.json`; GitHub exposes thread resolution only through GraphQL
`reviewThreads`, not the REST comments list, so do not substitute a REST listing.
A thread marked `truncated` has more than 100 comments; open it on the host before
judging it. Bot comments get the same treatment as
human ones.

Give each existing thread one status against the current head, from the code rather
than its resolved flag:

- **still valid:** the problem it describes is present at the head;
- **fixed:** the cited fix commit or current code removes the problem;
- **fix incomplete:** marked resolved, but the problem survives in part. The gap is a
  candidate finding of its own and goes through the finding gate;
- **outdated:** the code it discusses no longer exists or no longer applies.

Do not re-trace another reviewer's reproduction in full unless the thread's status
decides the verdict; say when a status rests on their evidence.

For PRs, compare each candidate with existing reviews, line comments, and thread
resolution. Equivalent feedback remains duplicate even when wording or line
differs. Do not republish unresolved, resolved, dismissed, or previously posted
findings unless the user explicitly asks for a follow-up and new evidence makes
the old comment materially incomplete. Explicitly authorized placement repairs
follow the narrow replacement exception in the GitHub publishing reference.
Mention confirmed existing feedback in
the report without presenting it as a new finding.

## Finding decision

A finding needs a concrete failure scenario and evidence. Ask:

1. What input, state, timing, or environment triggers it?
2. What observable behavior becomes wrong?
3. Which changed line introduces or exposes it?
4. What code, test, contract, or official source proves the claim?
5. Would the author likely change the patch if they knew?

Preferences and speculative future flexibility fail this gate. A pre-existing
problem belongs in residual risks unless the change makes it newly reachable or
worse. Questions must name the missing evidence; uncertainty alone is not a
blocking defect.

## Checks contract

Inspect the command and relevant project scripts before execution: lint fixes,
build generation, coverage, caches, and test setup can write files or affect
services. Use non-fixing options and route generated outputs to a disposable
workspace outside the reviewed target; if output paths cannot be redirected,
run the check against a permitted isolated copy of the reviewed snapshot. Keep
verification artifacts out of the captured staged/unstaged/untracked target.
Do not run commands that would mutate the original files, index, or shared state;
report the check as not run when no permitted isolated execution is available.
The main agent assigns exact commands, test targets, output locations, and resource
limits to any verification delegate and avoids overlapping resource-heavy runs.

Record current CI conclusions by check name and head SHA. For local commands,
record exact command and pass/fail. Respect repository test-scope constraints;
run directly affected tests by default unless the user or repository requires a
full suite. Never convert “not run,” “not available,” or an unrelated baseline
failure into a pass.

Keep the user-facing result compact and inside the six report parts. Green CI is
one clause in the Summary naming the status and head SHA — not a `Checks:` line,
not a table, not a section. A failure, pending or skipped check, stale result,
command not run, or unrelated baseline failure earns another sentence there,
because the author needs it.

If review coverage is partial, list the unreviewed files or lenses. High signal
with an honest boundary is better than a false claim of completeness.
