# Hard rules - non-negotiable, no exceptions

Violating any of these can cause real damage: lost data, broken trust, shipped-broken work. Always follow.

## Workflow Constraints

Never run `pnpm install` or `npm install` or read/explore `node_modules`. Use existing installed dependencies only. Never run binaries from `node_modules/.bin` directly — always invoke them via the package manager (e.g. `pnpm exec <binary>`, `pnpm run <script>`, or `npx <binary>`).

## Testing / Verification

Before declaring work complete, always run the full verification chain: typecheck, lint, build, and tests — and report pass/fail explicitly.

## Test Scope - run only changed files by default

Whenever you run tests — in the main agent OR in any subagent — run them **only against the files you changed (and their directly affected tests)**, never the whole suite, UNLESS the user explicitly asks for a full-suite run.

Why: a full-suite run forks many workers; several agents doing it at once can exhaust RAM and freeze the machine.

- Default: `<test-runner> <path-or-pattern-of-changed-specs>` (e.g. `pnpm test <changed-file-substring>`).
- Subagents inherit this rule. When dispatching a subagent that runs tests, tell it to scope to its changed files.
- Run the full suite ONLY when the user explicitly requests it, and prefer doing it once, serially, in a single agent — not in parallel across subagents.
- If you believe a full-suite run is warranted (e.g. a cross-cutting change), ask first; don't run it unprompted.

## Code Review

When validating code-review comments, verify each claim against the actual code before implementing; explicitly justify any comment left unaddressed.

## Communication / Response Style

Answer direct feasibility/yes-no questions first, then explore; do not launch into investigation before responding to the explicit question.

## Ask Before Destructive Commands

Never run irreversible or shared-state-changing commands without explicit permission. State the exact command, why you want to run it, and wait for an OK.
Always require confirmation:

- `git push --force` /`--force-with-lease`
- `git reset --hard`, `git clean -fd`, `git checkout -- .`
- `git merge`, `git rebase` , `git cherry-pick` onto shared branches
- `git branch -D`, deleting remote branches (`git push origin :branch`)
- `git commit --amend` on already-pushed commits
- `git tag -d` / force-pushing tags
- `rm -rf`, dropping DB tables, truncating data, running destructive migrations
- Anything touching production: deploys, infra apply, secrets, DNS
- Publishing packages, posting to GitHub/Slack/email, or anything visible to others

Safe by default: read-only commands (`status`, `diff`, `log`), local builds, tests, lint, typecheck, and edits inside the working tree.

If unsure whether a command is destructive - ask.

## Verify Before Reporting Complete

Before reporting any task as complete, verify it actually works:

- Run the tests, execute the script, check the output yourself.
- For TypeScript: run `tsc --noEmit` and fix every type error.
- For builds: run the build command and confirm it succeeds.
- If you cannot verify (no test exists, can't run the code), say so explicitly. Don't imply success.

Report outcomes faithfully:

- If tests fail, say so with the relevant output. Never claim "all tests pass" when output shows failures.
- Never suppress, simplify, or skip a failing check (test, lint, type error) to manufacture a green result.
- Never characterize incomplete or broken work as done.
- When something did pass or work, state it plainly. Don't hedge confirmed results with disclaimers, and don't re-verify things you already checked.

The goal is an accurate report, not a defensive one.

## Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them; don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

---

# Medium rules - engineering quality

Apply these by default. Push back if the user asks for something that violates one - but they can override with reason.

## Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No flexibility or configurability that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't improve adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it; don't delete it.

When your changes create orphans:

- Remove imports, variables, and functions that your changes made unused.
- Don't remove pre-existing dead code unless asked.

Every changed line should trace directly to the user's request.

## Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" -> "Write tests for invalid inputs, then make them pass"
- "Fix the bug" -> "Write a test that reproduces it, then make it pass"
- "Refactor X" -> "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

These guidelines are working if there are fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

# Low priority - references and conveniences

Useful context. Skim once, refer back as needed.

## Installed CLI tools (use these, not the defaults)

- `bun` is installed - prefer over `node` / `pnpm`
- `ripgrep` (`rg`) is installed - prefer over `grep`
- `fd` is installed - prefer over `find`
- `sd` is installed - prefer over `sed`
- `jq` is installed - use for JSON processing
- `gh` is installed - use for all GitHub operations

## Learn From Corrections

Persistent lessons live in a `learnings.md` file in the **current working directory** (the project root, not `~/.codex/learnings.md`). Read it at the start of every task and follow every rule there.
When the user corrects a mistake you made:

1. Apply the correction.
2. Append a rule to `learnings.md` file in the current working directory so the same mistake doesn't recur.
3. Show the user the new rule before continuing.

## Reading Large Files

When reading large files, run `wc -l` first to check the line count. If the file is over 2,000 lines, use the `offset` and `limit` parameters the Read tool to read in chunks rather than attempting to read the entire file at once.

---
