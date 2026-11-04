# Challenge Venues

Read when launching another agent's CLI or preparing/receiving a manual challenge-only
handoff. Ask for the venue after presenting each new plan; honor an explicit choice
already supplied for that plan and reuse it through revisions/resume. Do not silently
choose another venue when the selected one is unavailable.

## Fresh subagent here

Dispatch a fresh subagent with the saved inputs; the planning controller retains artifact
ownership. In simple mode, record its report in `plan.md` and use the simple revision loop.
In strict mode, own `review.md`, preserve dispatch counts and use the full/fresh-verifier
sequence or lightweight table. Never substitute planner self-review without telling the user.

## Another agent through its CLI

The planning controller launches the selected CLI, collects its actual response, revises
the plan and sends it back for review. Do not stop at giving the user a command unless
they request a manual handoff or launching is blocked. The challenger is report-only;
the planning controller remains the sole writer of plan and review records.

1. Confirm the selected executable with `command -v` and inspect its installed help.
   Use a noninteractive invocation with the relevant repository as working directory,
   read-only sandbox/tool permissions, and captured output. Verify flags for that
   installed version; use official documentation if their behavior is unclear. Preserve
   the configured model unless the user chooses another. Never install a CLI, change
   global configuration, bypass permissions or switch providers to make a dispatch work.
   If read-only execution cannot be established, report the limitation and obtain a
   different route. A prompt saying “read-only” alone is not an execution restriction.
2. Send a compact `plan-and-challenge challenge-only` request with absolute task, plan,
   specification and workspace paths; workflow, revision, required lens and role. For
   strict mode also pass review/run paths and the evidence contract. Ensure the CLI can
   read this skill (include its absolute path when needed). Explicitly request a report
   only: no file edits, implementation, approval or further agent dispatch. Supply prompt
   text via stdin or a supported file argument; never interpolate it into shell code.
3. Save the actual output and returned session ID in the task folder; record CLI/reviewer
   identity and reviewed revision in the owning review record. Strict mode additionally
   requires the existing reviewed-byte metadata. Check the candidate remained unchanged
   during review. Missing, partial, malformed or stale reports and process exit code 0
   alone are not a qualifying verdict. Do not replace an incomplete report with a guess.
4. Resolve each finding with a concrete revision or an evidence-backed response. Preserve
   the findings and responses; increment material revisions. Send the revised candidate
   plus all findings/responses back for recheck, including affected interactions and new
   problems. Resume only the exact captured session ID when appropriate; never resume
   whichever session happened to run last. If resume is unavailable, start a new reviewer
   with the complete review context and count the dispatch normally.
5. In **simple mode**, the same reviewer may recheck until the current revision is CLEAR.
   Stop after two consecutive passes with no progress, or at an active resource limit;
   report unresolved findings. Do not discard a disputed finding merely to get agreement.
   In **strict mode**, follow the existing full/lightweight sequence and limits exactly:
   full mode uses a fresh verifier session after the challenger, not a resumed challenger
   in its place. Do not add extra back-and-forth calls outside those dispatch limits.
6. The planning controller validates the actual verdict against the current candidate and
   records approval using the selected protocol. On timeout or CLI failure, preserve
   outputs and pending state, confirm the old process has stopped before redispatch,
   and apply existing retry limits. Report authentication or permission blockers accurately;
   do not count a failed launch as completed review. Keep the user informed of substantive
   findings, revisions and blockers while the exchange runs.

## Manual separate session (strict)

Use this ownership-transfer route only when the user requests a manual handoff. Automated
CLI review above keeps ownership with the planning controller and does not use this table.
For a manual **simple** handoff, send the same compact paths/revision request, wait for the
actual report, and continue the simple loop; no strict review file or verifier is required.

The planning owner saves task, stamped plan, declared specification, folder `.gitignore`,
and a review run with Pending decision. Record owner/next action and counts. Give this
invocation with real absolute paths, then stop without challenging or approving:

```text
/plan-and-challenge challenge-only
Task: <absolute task.md>
Plan: <absolute plan.md>
Specification: <absolute path or none>
Review: <absolute review.md>
Run ID: <existing run ID>
Mode: <full or lightweight>
Required lens: <lens>
Next action: initial challenge
```

Open the other session in the same repository. If it lacks filesystem access, use a
user-authorized transfer of the whole task folder and referenced specification; check all
paths before continuing. Relocation after a verdict must not rewrite fingerprinted inputs
under an old approval: update transport metadata first and obtain review of the final copy.

The other session reads current run state and takes controller ownership for its action.
It can act as challenger because it did not write the plan. It never revises the plan or
records APPROVED. Save both evidence tables/lists and actual reviewed-byte metadata.

| Result / next action | Owner and transition |
|---|---|
| Full challenge CLEAR | Challenge session dispatches a fresh verifier of the unchanged candidate. Save its report, return ownership to planning owner, stop. |
| Full challenge BLOCKED | Save findings, set next action to owner revision, return ownership and stop **before verification**. |
| Owner revision | Planning owner revises against findings (or obtains one reviser's actual response), saves all responses, transfers ownership back with next action `verification after revision`, stops. |
| Verification after revision | Challenge session receives full findings and actual responses, dispatches one fresh verifier for the same round, saves report, returns ownership and stops. No repeat challenger for that round. |
| Verifier BLOCKED after Round 1 | Owner prepares Round 2 with those findings and existing counters; repeat the bounded sequence. |
| Verifier CLEAR | Planning owner compares reviewed hashes, records approval and runs the gate. |
| Lightweight CLEAR | Return evidence to owner for approval; no separate verifier. |
| Lightweight Minor correction | Owner revises, then resumes the same challenger once using `minor recheck`. Apply the lightweight terminal table. |

Resume invocation uses the same explicit paths/run/mode plus Next action. Before any action,
read the existing review and counters; do not reset the run or redispatch an already completed
role. Record every ownership transfer and pending step. The user can return to the planning
session with `Challenge completed; continue from review.md.`

If a role cannot run, preserve Pending and follow the main skill's bounded unavailability
procedure. A missing revision or failed dispatch never counts as a qualifying verdict.
