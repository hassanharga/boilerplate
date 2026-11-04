# Cleanup audit report

A content contract, not a form. Deliver it in chat by default; create a file only when the
user asks for one. Lead with the conclusion and the approval request, write natural prose,
and omit an empty category rather than printing a heading followed by "None." Bullets read
better than tables for a handful of items; use tables when several items need comparing.

If the report is saved to a file, open with: *No code or configuration changes were made.
This report is the only Phase 1 artifact.* In chat, say simply that no files were changed.

## What the report must contain

**Scope and blind spots.** Repository or workspace boundary, languages, head or reference
commit, entrypoints reviewed, tools that were already available, paths excluded, and which
categories were assessed and which were not. Name what static analysis could not see —
external consumers, runtime registration, other repositories.

**Candidates, each with a stable ID.** Use `D1`, `D2` for deletions and `X1` for refactors
so approval is unambiguous. For each: what it is, its category, the rerunnable evidence,
its evidence class (`safe-candidate`, `needs-external-evidence`, `not-actionable`), its
risk (Low/Medium/High), and the cluster it belongs to if partial approval could break the
graph. Say what was checked, not just what was found.

Evidence class and risk are separate judgments — strong evidence for a change with a wide
blast radius is still High risk. Do not invent percentages.

**Refactor candidates**, kept separate from deletions, each with its proposed boundary and
verification plan.

**`needs-external-evidence` items**, each naming the specific blind spot and the exact
evidence that would resolve it. These are never covered by blanket approval.

**`not-actionable` items** — investigated false positives and intentional code — so the
next audit does not repeat the analysis.

**Baseline.** Current typecheck, lint, build, and affected-test status; missing tools or
checks that could not run; the runtime evidence window and its representativeness if any
was used. Never describe a failing baseline as passing: a pre-existing failure can prevent
safe execution even when a candidate is valid.

**Approval request.** Ask for approval by ID or by a clearly defined cluster. State that
blanket approval covers only the listed safe candidates, and that approval to edit is not
approval to branch, stage, commit, push, publish, or post anything externally.

Never put an environment-variable value or a secret in the report.
