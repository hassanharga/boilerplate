# Review — <plan title>

<!-- Saved as review.md. Controller only. Replace run/owner values before saving.
Append new runs and decisions; preserve earlier evidence. Read the review contract.
The initial Pending decision revokes execution. Append round output after it, then append
a complete terminal Final Decision from the contract only when its preflight succeeds. -->

## Run <unique-run-id>

## Inputs
- Task source: <ID/URL/path and how read>
- Source last updated: <source timestamp or unavailable>
- Captured at: <timestamp>
- Normative extract: <exact requirements>
- Execution reconciliation: <ledger path and observed revision/time, workspaces, or not started>
- Task snapshot: <absolute task.md>
- Normative specification: <absolute path or none>
- Specification ownership: <external normative source | planner-owned design note | none>
- Plan: <absolute saved plan.md>
- Repository: <root, branch and revision or outside Git>
- Agent artifacts: <task-folder .gitignore with *, Git verification result, or not applicable>
- Transport mapping: <old and new reference locations preserving original targets, or none>

## Protocol State
<!-- The gate reads these fields at approval: every one must hold a real value, Mode must
match the decision's Review mode, and the counters must be advanced as dispatches happen.
An approved full run shows at least 2 review dispatches; lightweight shows at least 1. -->
- Mode: full
- Challenge venue: <fresh subagent | separate session | local fallback>
- Current owner: <agent/session>
- Next action: <actor and required next step>
- Required review lens: <general plus domain if applicable>
- Round: 1 of 2
- Review dispatches used: 0 of 4
- Reviser dispatches used: 0 of 2
- Delegation: <usable/authorized or actual restriction/failure>
- Execution route: <approved candidate's rule and dependency compatibility evidence>
- Review link: <exactly one, resolves from plan>
- Specification declaration: <exactly one, real path or none>

## Final Decision
- Status: Pending
- Approval schema: plan-approval-v2
- Run ID: <same unique run ID>
- Recorded by: <controller>

<!-- As results arrive, APPEND:
Round N of 2; actual challenger ID/report path; both complete evidence tables; findings;
actual planner responses if required; fresh verifier ID/report path; both rebuilt tables;
reviewed-byte metadata; updated owner/next-action/counters. Preserve reports in unique files.
Do not prefill another actor's output. No report yet means Pending.
At approval, append the complete terminal Final Decision from references/review-contract.md
and run the skill-owned gate with --verify REVIEW --plan PLAN. -->
