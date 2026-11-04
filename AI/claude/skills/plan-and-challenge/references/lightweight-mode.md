# Lightweight Mode

Use only when all five strict-workflow criteria hold. Preserve the selected planning
method or supplied plan; for a new plan use the entrypoint's planning-method question
(Superpowers default or agent Plan mode), with no silent direct-plan fallback. The task snapshot,
normative specification, metadata, run invalidation, evidence hashes and approval gate still
apply. Use `assets/light-review-template.md` and `agents/lightweight-challenger.md`.

Pass task, optional specification, plan, repository, review contract, run ID and script path.
The challenger reads every normative source, returns both evidence lists, findings and exact
reviewed-byte metadata. Missing or unreadable supplied inputs block review. Save all returned
lists and reports, including clean reviews; a lone CLEAR is insufficient.

`CLEAR` means every requirement is covered, every added observable constraint is supported,
and no Blocker/Major remains. Genuine Minors may remain open with a recorded disposition.

| Initial result | Required transition |
|---|---|
| CLEAR, no subsequent input edits | Approve those exact bytes. No separate verifier. |
| Minor correction requested, or BLOCKED with Minor findings only | One revision and one recheck by the same challenger. Save its new complete evidence. |
| Any Blocker/Major, or eligibility fails | Escalate to full in the same run. This initial dispatch counts as Round 1 challenger; obtain revision if needed, then a fresh full verifier. That verifier rebuilds all evidence with the required domain lens. |

| Result of the single allowed Minor recheck | Required transition |
|---|---|
| CLEAR | Approve the newly reviewed bytes. |
| Any other verdict, unreadable input, or still-ineligible task | Record BLOCKED and return to the user. No third lightweight dispatch or automatic counter reset. A user-directed new full run may follow. |

On initial escalation: one review dispatch is already used; a fresh Round 1 verifier is the
second. If it blocks, Round 2 allows one full challenger and one fresh verifier. At most four
review attempts and two reviser attempts total; keep existing counters. A transient failed
attempt also consumes budget. If required review no longer fits, stop rather than exceed it.
The separate-session challenger action counts exactly as its equivalent dispatch here.
Never downgrade full to lightweight. If independent review is unusable, use the accurately
labelled local fallback and explicit user-approval rules in the main skill.
