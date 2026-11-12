---
name: review-changes
description: >-
  Use when reviewing a proposed change in a pull request, branch, commit, staged,
  unstaged, or untracked work; re-reviewing after new commits; or publishing
  selected review findings. Covers code, tests, configuration, CI, documentation,
  migrations, dependencies, and generated artifacts. Fixing feedback belongs to
  address-review-comments; broad security audits belong to find-security-gaps.
---

# Code Review

Find material defects introduced by the change and explain them so the author
can act. Review is read-only by default. Publishing is a separate, explicitly
authorized mode.

Read-only protects the reviewed files, index, and shared state. Verification may
create disposable outputs in an isolated workspace under the checks contract;
those outputs never become part of the review target.

## Choose the Mode

| Request                                             | Mode           | Mutation boundary                              |
| --------------------------------------------------- | -------------- | ---------------------------------------------- |
| Review a PR, diff, commit, branch, or local changes | Review         | Read-only                                      |
| Review again after new commits                      | Re-review      | Read-only                                      |
| Post selected findings to a PR                      | Publish        | Only the authorized review action and findings |
| Fix review findings                                 | Not this skill | Use `address-review-comments`                  |
| Broad security or whole-repository audit            | Not this skill | Use `find-security-gaps`                       |
| Refresh stale review guidance                       | Not this skill | Use `turn-into-skill`, outside any review      |

This skill never edits the reviewed target or its own guidance. When the freshness
gate detects a stale rule, quarantine that rule, complete the review from current
project evidence, and report the staleness — do not fix it here. Do not stage,
commit, push, label, approve, or publish while in Review mode.

## Choose the Depth

Depth decides how much review machinery the change gets. Pick it after collecting
evidence, from the size in `meta.json` and the risk of what changed, and state it
in Summary. The user's explicit choice wins.

| Depth    | When                                                                                               | What runs                                                                    |
| -------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Quick    | The user asks for a quick look, or a small change with no behavior: docs, version bump, rename     | Main review only; no challenger; design pass on changed units                |
| Standard | Default                                                                                            | Full contract, challenge round                                               |
| Deep     | Over 400 changed lines or 15 files outside lockfiles and generated code | Full contract with one subagent per risk area, then the challenge round |

A small change in a high-risk area (auth, money, data
migration, concurrency, public contracts) stays Standard and gets more scrutiny
instead: trace every caller, and prove runtime claims rather than reason about
them. Never downgrade such a change to Quick because it is small.

## Scripts

Invoke shell helpers with `bash` and Python helpers with `python3` instead of
redoing their steps by hand. None edits reviewed files or the index; PR collection
only fetches objects into FETCH_HEAD.

| Script                    | Use                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------- |
| `scripts/profile.sh`      | Step 1: detect languages, frameworks, package manager, project commands, instructions, architecture, and which stack references apply |
| `scripts/collect.sh`      | Step 2: write the evidence packet for a PR, branch, commit, range (re-review), staged or local target: merge-base diff, isolated snapshot, checks, paginated existing feedback, ticket keys |
| `scripts/snapshot.py`     | `verify <packet>` before reporting or publishing: the evidence packet is unchanged |
| `scripts/check-report.py` | Before showing the report, and with `--publish` before posting: six parts, Types, fields, anchors, Suggestion cap |
| `scripts/publish.py`      | Publish mode: dry run by default; posts opener then line comments pinned to the reviewed head, idempotently |
| `scripts/run-challenger.sh` | Step 6: launch an external challenger CLI read-only                                      |

When a script cannot run here (missing `jq`, `gh`, or `python3`), do its steps by
hand following the same reference and say so in Summary.

## Reference Routing

Read only what the current review needs:

| Reference                                                                  | Read when                                                                                    |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| [Evidence lifecycle](references/evidence-lifecycle.md) | Collecting evidence, and before reporting or publishing |
| [Review workflow](references/review-workflow.md)                           | Every review                                                                                 |
| [Challenge round](references/challenge-round.md)                           | Every review, before the report, unless the round is skipped                                 |
| [Output contract](references/output.md)                                    | Preparing the report or inline findings                                                      |
| [Design principles](references/design-principles.md)                       | Every review that changes production code                                                    |
| [Prove it](references/prove-it.md)                                         | Before running a reproduction for a finding that depends on language, runtime, or library behavior; it sets where to run it and what to record |
| [Re-review](references/re-review.md)                                       | Re-review mode                                                                               |
| [GitHub publishing](references/github-publishing.md)                       | Publication is explicitly requested                                                          |
| [Reliability and state machines](references/reliability-state-machines.md) | Concurrency, retries, orchestration, state transitions, or multiple side effects change      |
| [Yassir NestJS/DDD profile](references/yassir-nestjs-ddd.md)               | `profile.sh` lists it in `stack_references`, or other signals match the Yassir Mobility stack |
| [Frontend risks](references/frontend.md)                                   | `profile.sh` lists it, or React, Next.js, Angular, Vue, or browser-facing code changes        |
| [Stale guideline reporting](references/guideline-maintenance.md)           | Cached guidance conflicts with current evidence for the pinned version                       |

Stack-specific guidance lives in its own reference file, selected from the profile.
A stack without one gets the general contract plus the project's own instructions;
that is a supported case, not a gap.

Project instructions and explicit user requirements outrank every reference.
Version-sensitive framework claims require version-matched official evidence;
cached skill text never outranks the current project or official documentation.

## Review Contract

### 1. Establish target and intent

Run `bash scripts/profile.sh <repo-root>` and read the instruction files it lists. Use
its commands for verification and its `stack_references` for routing, and confirm
anything that matters in the files themselves: the profile points to evidence, it
does not replace it. Resolve the exact comparison target before judging code. In an
interactive review, make the intent-source gate visible before deep analysis:

- if the user supplied acceptance criteria, a Jira key, or another specification,
  use it and state the selected source;
- if the PR body contains a Jira key or linked issue and an authorized read
  capability is available, fetch it and state that it anchors the review;
- otherwise ask once: “Do you have acceptance criteria or a Jira ticket, or
  should I use the PR description?” and wait for the answer.

In the same message, ask which challenger to use for step 6, with the options the
[challenge round](references/challenge-round.md) builds from the installed agents.
One combined question keeps the review to a single interruption. Skip the
challenger part when the user already named one or the round is skipped.

Do not hide this gate in internal reasoning. If the user already said “PR
description,” “go ahead,” or declined to provide another source, continue
without asking again and label coverage inferred where appropriate. A
non-interactive reviewer uses the best available PR body, commit message, or
branch context and discloses the fallback.

### 2. Collect complete evidence

Run `bash scripts/collect.sh <packet-dir> <pr|branch|commit|range|staged|local> …` from the
repository, with the packet in the session scratch directory. Use a new packet directory; existing packets are retained and refused. It captures base,
head, and merge-base SHAs, the merge-base diff, the changed-file list, isolated old/new
snapshots for reading, PR checks, and every review thread with its
resolution state. For a PR or branch the diff starts at the merge base, as the host
shows it, not at the base branch tip. For a merge commit, pass `--parent N` after selecting the intended parent.
For local work it includes staged, unstaged,
and untracked changes unless the user narrowed the target. Follow the [evidence lifecycle](references/evidence-lifecycle.md), inspect snapshot gaps,
and profile changed packages with `bash scripts/profile.sh <snapshot> --files <packet>/files.txt`.
Review tests, CI, docs, manifests, lockfiles,
migrations, and deployment configuration when changed; do not categorically
skip them.

Review blind first. Collect existing feedback here, but do not read its content
until your own trace (step 3) and draft findings (step 4) exist. Then compare: use
it to deduplicate, and check each thread against the current head as the
[review workflow](references/review-workflow.md) describes. Feedback read first
anchors the review on what others already noticed.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
target/index/shared-state writes. Include the repository's test-scope and resource
limits in each brief. The main agent coordinates verification commands; a delegate
runs only explicitly assigned checks with bounded scope and isolated outputs under
the checks contract. Reconciliation, conflict resolution, the final report, and every external write
stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means one pass per independent risk area, each carrying the same intent and
revision evidence and the same finding gate. At Deep depth, delegate these passes:
behavior and logic; design principles; tests; plus configuration, deployment, and CI
when such files changed, and reliability when its routing condition matches. Skip a
pass whose area the change does not touch, and say so in Summary. Cross-cutting analysis,
deduplication, and final verification stay with the main agent. At Quick and
Standard depth, keep the review in the main agent entirely.

### 3. Inspect behavior, not taste

Trace changed behavior through callers, callees, contracts, sibling paths, and
tests. Prioritize correctness, security, data integrity, reliability,
performance with a demonstrated impact, acceptance-criteria gaps, and tests that
fail to protect changed behavior. Generic style preferences are not findings.

Then run the [design principles](references/design-principles.md) pass on the units
the change adds or materially rewrites: duplication, unneeded complexity or
generality, responsibilities, substitutability, dependency direction, names and
contracts that are expensive to change once shipped, and operability. A principle
is a reason to look; the finding is the concrete cost it causes in this change.

When a library or framework claim depends on a version, inspect the project’s
declared version and verify the claim against current official documentation or
source. A cached rule that conflicts with, does not cover, or cannot be verified
for the pinned version is not evidence. Quarantine it from the current review
and follow the [guideline-maintenance workflow](references/guideline-maintenance.md).
When a finding rests on how a language or library behaves at runtime, settle it
with a minimal reproduction against the installed version, following
[prove it](references/prove-it.md), rather than from memory.
Do not install analyzers or mutate shared skill files inside Review mode.

### 4. Apply the finding gate

Report a defect only when all are true:

- the reviewed change introduced or exposed it;
- the impact is material and the affected scenario is traceable;
- the claim is supported by current code or authoritative evidence;
- the author can take a concrete action;
- the location is exact and overlaps the changed diff when emitted inline;
- existing tests, checks, invariants, or prior feedback do not already settle it.

Use a Question for a material uncertainty that cannot be resolved from available
evidence. A design-principle finding passes the same gate as any other defect;
without a demonstrated defect it can only be a design Suggestion. Design
Suggestions are on by default and capped at three; other Suggestions and
Nitpicks are opt-in under the output contract. Do not present a Suggestion as a
demonstrated defect. Do not turn missing context into a blocker.
Continue through the full target after finding one issue. If the diff is too large
or unavailable, state exactly what was not reviewed.

### 5. Verify proportionately

Read CI results for remote PRs. For local changes, run repository-required or
directly affected typecheck, lint, build, and tests when feasible and allowed by
repository instructions. Bind checks to the reviewed snapshot as described in the
review workflow; current output from another version is not a pass for the target.
Do not claim a check passed unless its output was observed. Report commands not run
and why. Follow the review workflow's checks contract for command side effects and
output isolation.

Coverage is repository-specific: require 100% when the active configuration or
acceptance criteria requires it, enforce another configured threshold when that
is the policy, and invent no threshold where none exists. Missing tests remain a
finding when changed behavior has a realistic unprotected failure path.

### 6. Challenge the draft

Before reporting, send the change and the draft findings to one independent,
read-only challenger, following the [challenge round](references/challenge-round.md).
The challenger runs this same skill as a full review, blind to the draft, then tries
to disprove each draft finding. The challenger can be Codex, OpenCode, Pi, Claude
Code, or a fresh subagent. Never launch your own CLI as the challenger; when you want
the same provider, use a fresh subagent instead.

Its output is evidence, not a verdict. Compare the two reviews, verify every finding
against the code yourself, put challenger-only findings through the step 4 gate, and
merge them into one list in which each finding appears once. Stay the only author of
the report.
Run one round. Skip it at Quick depth, and when `REVIEW_CHANGES_CHALLENGER=1` is set,
because then you are the challenger.

## Report

Use the [output contract](references/output.md): exactly **Summary → Review path →
Findings → Conflict notes → AC coverage → Verdict**, and nothing else. The behavioral
change map goes inside Summary so the reader understands the PR before the defects —
ASCII flow in a terminal, Mermaid on a GUI surface that renders it. The Review path
then guides the user's own review: the entry point to start reading from, the
stops in execution order with what to check and which test proves each one, and
which files only need a skim.

Summary also names the references loaded, and any reference whose routing condition
matched but was skipped, with the reason. A skipped matching reference is a coverage
gap the reader needs to see.

Print findings as markdown text; do not call `ReportFindings` or any other
structured finding reporter. Order them by `Type:` and material impact, and give
every one the explicit `Type:`, `Issue:`, `Impact:`, and `Fix:` fields with a
`path:line` anchor on its title line.

`Type:` is one of the five values fixed by the output contract — `Issue -
Blocking`, `Issue - Non-blocking`, `Question - Non-blocking`, `Suggestion -
Non-blocking`, `Nitpick - Non-blocking`. A risk area such as reliability,
testing, or migrations describes what the finding is about, so it goes in
`Issue:` and `Impact:`; it is never a `Type:` and never a heading over the
findings.

Verification belongs inside the six parts as prose: CI status with head SHA,
the challenge-round outcome, and anything not run go in Summary,
blocking-findings yes/no with scope and residual risk go in Verdict. No `Checks:` line of its own, no verification table, no
"Overall" block.

Before showing the report, verify packet integrity per the evidence lifecycle, then run
`python3 scripts/check-report.py <report.md|-> --snapshot <packet>/snapshot --base-snapshot <packet>/base-snapshot --diff <packet>/diff.patch`.
Pass `-` to pipe the report on stdin when you cannot write files. Fix every error
it reports; warnings about outside-diff anchors are acceptable for chat-only
findings that cite them deliberately. When the user asked for the report in a file
and writing is blocked, return the full report as text and say where it was meant
to go.

Do not say `Ready to merge` or submit approval merely because no blocker was
found. No findings means no qualifying defects were found in the reviewed scope,
not that every possible behavior was proven.

## Publication Gate

After reporting, stop. Publish only when the user explicitly identifies what to
post and chooses normal comment or request-changes. Never approve unless the user
explicitly requests approval. Publication must follow the fresh-state,
deduplication, placement, write-order, ambiguity-recovery, and verification rules
in [GitHub publishing](references/github-publishing.md). On GitHub, write the
selected findings into a plan file and use `python3 scripts/publish.py`: run it without
`--yes` first and check the plan it prints, then run it with `--yes`. It refuses
approval; an explicitly requested approval is a separate, manual action.

Each published finding is one independent, line-anchored comment on the code it
concerns. A request to post into an already-open thread is a placement request:
take the fresh snapshot and resolve exact anchors first, then reply only when the
finding is genuinely about that thread's subject, and otherwise anchor it and say
so.
