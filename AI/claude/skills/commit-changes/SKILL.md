---
name: commit-changes
description: Use when a user asks to commit their changes, or to draft or generate Git commit messages for them, including staged, unstaged, and untracked work, splitting it into commits by logical change, and summarizing the commits created. Also use for "commit what I staged" requests, for adding forgotten files or changes to an earlier unpushed commit (amend or fixup), and when committing is the first step of a larger request, such as "commit and push" or "commit, push and open a PR"; this skill handles the commits and push. Do not use for squashing or reordering history, rebasing onto another branch, reverting, resolving conflicts, or code review.
---

# Commit Changes

Commit the user's work grouped by logical change, treat whatever they already staged as a deliberate choice, hold back suspicious files until they confirm, and finish with a summary of what was committed. The same rules apply when folding changes into an earlier unpushed commit.

## Authorization modes

| Request                                     | Allowed outcome                                                                                       |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| “Draft/generate a commit message”           | Return the grouping and one message per group only. Never stage or commit.                            |
| “Commit my changes” / “commit everything”   | Commit staged, unstaged, and untracked changes, one commit per confirmed group, after the gates pass. |
| “Commit what I staged” / “commit staged”    | Commit only the staged snapshot. Leave unstaged and untracked work untouched.                         |
| “… and push”                                | Create the commits, then perform only a normal push. Push requires explicit authorization.            |
| “Add this to the last/that commit” / “amend” | Fold the named changes into an existing unpushed commit, after confirmation. See [Amend an earlier commit](#amend-an-earlier-commit). |
| “… and open a PR”                           | This skill covers the commits and push only. Open the PR afterwards under the active PR rules.        |

No mode authorizes amending a pushed commit, force-pushing, `git commit -a`, `git add -A`/`git add .` across the repository, discarding work, or bypassing hooks. Hook bypass stays outside this skill even when requested later; stop and report the failure instead of using `--no-verify` or an equivalent.

## Inspect the changes

Read active repository instructions first. Then inspect, without changing the index or working tree:

```bash
git status --short --branch --untracked-files=all
git diff --cached --name-status      # staged
git diff --cached
git diff --name-status               # unstaged
git diff
git diff --cached --check; git diff --check
git log -10 --format=%s
```

Read untracked files that matter for grouping. Use repository-relative paths.

Stop and report instead of committing when:

- there is nothing to commit, or the index has unresolved conflicts;
- a merge, rebase, cherry-pick, or bisect is in progress;
- the intent of the changes is unclear;
- HEAD is detached, or the current branch is the default/protected branch without explicit branch-specific permission.

## Respect the staging

The index is the user's selection. Do not unstage, restage, or reshape it to suit a grouping:

- Staged content is committed first, as its own groups, exactly as staged. It may split into several groups by logical change, but never absorbs unstaged or untracked content.
- Unstaged and untracked changes are grouped and committed after the staged groups. A file with both staged and unstaged hunks contributes its staged hunks to the staged groups and its remaining hunks to a later group.
- In “commit staged” mode, stop after the staged groups.

When the staged content and the rest belong to the same logical change, say so in the proposal, but keep them as separate commits unless the user asks to combine them.

## Flag suspicious files

Before proposing groups, look for files that probably should not be committed, especially untracked ones the user has not selected. Examples:

- secrets: `.env*`, credentials, tokens, private keys (`*.pem`, `id_rsa`, `*.p12`), cloud config with keys;
- generated or local output: build directories, coverage, `node_modules`, caches, `*.log`, database files, dumps;
- OS or editor debris: `.DS_Store`, `Thumbs.db`, swap and backup files, local IDE settings;
- large binaries or archives, or anything the repository's `.gitignore` conventions suggest should be ignored.

Use judgment: a `.env.example` with placeholder values or a checked-in fixture can be legitimate. Hold every flagged file out of the groups, list it with a one-line reason, and ask whether to include it. Approval of the grouping does not cover flagged files: if the user pre-approved the grouping, commit the rest and ask about the flagged files in the summary. Never print secret values when explaining a flag. Do not edit `.gitignore` or delete a flagged file unless asked.

## Group by logical change

Group by logical change (a feature, fix, or refactor). Keep tests, config, and docs with the change they support; do not group by file type. Do not split trivially small changes. Order groups so each commit builds and passes on its own; when dependencies make that impossible, merge those groups (within the staged/unstaged boundary above).

If everything is one logical change, propose one commit. Otherwise show each proposed group with its paths, whether it comes from staged or unstaged content, and its message, plus any flagged files, and wait for confirmation. Skip the wait only when the user has already approved the grouping.

Split at file boundaries and keep both sides of a rename in one group. When one file holds hunks from different groups *within the same side* (staged or unstaged), do not split it: put the whole file in the group it mostly belongs to and say so, or, if that would make a commit misleading, name the groups, print the `git add -p` commands that would separate them for the user to run, and stop.

## Commit the groups

Record the starting point once: `base=$(git rev-parse HEAD)`.

**Staged groups.** Change only the index, never the working tree:

```bash
target=$(git write-tree)                      # once: the full staged snapshot
git restore --staged -- <staged paths not in this group>
git commit -F <message file>
git read-tree "$target"                       # restore the remaining staged content
```

Repeat the last three steps per staged group. If any step fails, run `git read-tree "$target"` so the index again holds every staged change not yet committed, then stop and report. After the last staged group, `git diff --cached` must be empty and `git rev-parse HEAD^{tree}` must equal `$target`.

**Unstaged and untracked groups.** Stage only the group's paths, then commit:

```bash
git add -- <paths in this group>              # also records deletions of those paths
git diff --cached --name-status               # confirm the index holds exactly this group
git commit -F <message file>
```

If any step fails, run `git restore --staged -- <paths in this group>` so the work returns to unstaged, then stop and report. Never stage a flagged file the user has not approved.

## Amend an earlier commit

Use this when the user wants changes folded into a commit that already exists, such as a forgotten test file, instead of a new commit. Amending rewrites history, so keep it to local commits and confirm before doing it.

1. **Find the target.** “The last commit” means HEAD. When the user describes it instead (“add this to the retry commit”), find it with `git log --format='%h %s' -20`, and confirm it unless only one commit matches.
2. **Refuse pushed or awkward targets.** Stop when `git branch -r --contains <sha>` lists any remote branch: amending would need a force push. Offer a normal follow-up commit instead. Also stop if the target or any commit after it is a merge commit.
3. **Pick the changes.** Take only the files or hunks the user named. If they already staged exactly those, use the index as is; otherwise stage only those paths, never anything else. Flag suspicious files as usual. Leave every other change where it is, unless the user also asked to commit it; then run the normal grouping flow afterwards.
4. **Confirm.** Show the target SHA and subject, the files being added, whether the message changes, and the exact commands. Wait for confirmation unless the user named both the target and the files.
5. **Rewrite.** Record `before=$(git rev-parse HEAD)` first.

   When the target is HEAD:

   ```bash
   git add -- <paths>                 # skip if exactly these are already staged
   git commit --amend --no-edit       # or -F <message file> when the message should change
   ```

   When the target is older:

   ```bash
   git add -- <paths>
   git commit --fixup=<sha>
   GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash --autostash <sha>~1   # use --root if <sha> is the first commit
   ```

   `GIT_SEQUENCE_EDITOR=:` accepts the generated todo list unchanged, so the rebase runs without an editor. If the rebase stops on a conflict, run `git rebase --abort`. That returns the branch to the fixup commit on top, with nothing lost. Then report and stop; do not resolve conflicts here.
6. **Verify.** `git diff "$before" HEAD --stat` must show only the added changes. `git show --name-status <new sha>` must list the target's original files plus the added ones. The other commits after the target keep their subjects but get new SHAs. In the summary, title it `Amended <old sha> → <new sha>`, list any rewritten commits with old and new SHAs, and give `$before` as the pre-amend HEAD, recoverable through `git reflog`.

A later push of the amended branch is an ordinary push, because the target was never on the remote.

## Compose the message

Precedence is: repository instructions and configured tooling, then established recent history, then this fallback:

```text
<type>[optional scope][!]: <concise subject>

[optional body explaining motivation or behavior]

[optional footer, including BREAKING CHANGE or issue references]
```

Choose the type from intent, not filenames. Common fallback types include `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, and `revert`. Use a scope or ticket only when supported by repository convention or clear evidence; never invent one. When policy requires a ticket as the Conventional Commit scope, format it after the type, such as `fix(CMB-123): correct retry handling`, rather than using the ticket as the type. Keep the subject specific and omit a final period. Add a body only when it improves understanding. Do not add generator advertising or AI attribution.

## Hooks and verification

Before committing, follow active repository verification and coverage policy, unless the repository's pre-commit hook already runs those checks; then let the hook run them and report its result rather than doing the same work twice. Never invent a coverage threshold or claim a check passed without current evidence.

Run one ordinary `git commit` per group and preserve hooks. If a hook fails or changes the staged state unexpectedly, stop, report the exact result, and wait for authorization before diagnosing or fixing anything. Do not commit or push while a required hook is failing.

Push only when explicitly requested, never force-push, and verify the remote result before reporting success.

## Summarize the result

After the last commit, verify against Git rather than memory:

```bash
git log --reverse --format='%h%x09%s' "$base"..HEAD
git show --name-status --format= <sha>        # per commit
git status --short --untracked-files=all
```

Then end the reply with this summary, in Markdown so it renders in both the terminal and GUI clients:

```markdown
## Committed N changes on `<branch>`

| # | Commit    | Message                         | Files                                   |
| - | --------- | ------------------------------- | --------------------------------------- |
| 1 | `a1b2c3d` | feat(api): add retry to client  | `M src/client.ts`<br>`A src/retry.ts`   |
| 2 | `e4f5a6b` | docs: describe retry settings   | `M README.md`                           |

**Left uncommitted:** `.env` (flagged: looks like secrets; include it?), or “nothing”.
**Checks:** pre-commit hook PASS / not configured / …
**Pushed:** no / `origin/<branch>` verified
```

Use `A`/`M`/`D`/`R` status letters from `git show --name-status`. In a client that cannot render tables, use the same content as one list item per commit. List every file in each commit; for a commit with more than about 15 files, show the first ones and `… and N more`. If something stopped the run partway, show the commits that did land, say exactly where it stopped, and state what remains staged, unstaged, or untracked.
