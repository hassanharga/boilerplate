# Review — <plan title>

<!-- Lightweight review.md. Preserve history. Fill setup values, keep Pending until actual
qualifying evidence returns. Preserve both lists from every challenge/recheck. -->

## Run <unique-run-id>

## Inputs
- Task source: <ID/path, source update time and capture time>
- Normative extract: <exact requirements>
- Execution reconciliation: <ledger path and observed revision/time, workspaces, or not started>
- Task snapshot: <absolute task.md>
- Normative specification: <absolute path or none>
- Specification ownership: <external normative source | planner-owned design note | none>
- Plan: <absolute saved plan.md>
- Repository: <root/branch/revision or not applicable>
- Agent artifacts: <task-folder .gitignore with *, verified by Git, or not applicable>
- Transport mapping: <preserved reference targets, or none>

## Protocol State
<!-- The gate reads these at approval: real values throughout, Mode matching the decision's
Review mode, counters advanced as dispatches happen, and at least 1 review dispatch for a
lightweight approval. Round stays 1 unless escalation to full opens Round 2. -->
- Mode: lightweight
- Challenge venue: <fresh subagent | separate session | local fallback>
- Current owner: <agent/session>
- Next action: <actor and step>
- Challenger: <real identifier or Pending>
- Round: 1 of 2
- Review dispatches used: 0 of 4
- Reviser dispatches used: 0 of 2
- Recheck used: No
- Required review lens: general
- Delegation: <usable/authorized or actual restriction/failure>
- Lightweight eligibility: <evidence for each of all five criteria>

## Final Decision
- Status: Pending
- Approval schema: plan-approval-v2
- Run ID: <same unique run ID>
- Recorded by: <controller>

<!-- Append the following sections when real output arrives, once per initial/recheck:

## Requirement Coverage — <initial or recheck>
<complete returned list, covering task AND specification>

## Plan Constraint Evidence — <initial or recheck>
<complete returned list, with exact source/repository evidence>

## Findings and Responses — <initial or recheck>
<real findings with stable IDs, severities, evidence, actual responses and dispositions>

## Challenger Report — <initial or recheck>
<actual identity, qualifying verdict, unique saved report path and its Review Evidence block>

Update next action and counters. Apply the terminal lightweight table. At approval append
the complete Final Decision from references/review-contract.md, with Review mode lightweight
and qualifying report hash. The same fields and gate apply as full mode; only review volume
is reduced. For local fallback use READY, then explicit user evidence under that contract. -->
