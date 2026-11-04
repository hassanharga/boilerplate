# Re-review After New Commits

Read when the user asks to review a target again after it changed — "they pushed
fixes", "check again", "re-review the PR" — or when a PR you reviewed has a new head.

A re-review answers two questions: did the earlier feedback get addressed, and did
the new commits introduce anything new. Re-reading the whole change from scratch
wastes the earlier work and buries the answer to the first question.

## Establish the two snapshots

- **Previous:** the head SHA of the last review. Take it from that review's report,
  or for a PR from the commit your published review or comments were pinned to.
  When it cannot be established, say so and run a full review instead.
- **Current:** the current head. Collect the increment with
  `scripts/collect.sh <packet> range <previous-sha> [head]`; it warns when the
  previous SHA is no longer an ancestor. For a PR, also collect the PR target for
  its threads and checks.
- **Earlier findings outside a PR** (a report in chat or a file): list them in the
  packet's `existing-feedback.md` with their ids, so the challenger checks the same
  set. Report the status of every earlier finding the user asks about, even when the
  output contract would only count fixed ones.

If the branch was rebased or force-pushed and the previous SHA is no longer an
ancestor, the incremental diff is unreliable. Diff the previous and current heads
directly (`git diff <previous> <current>`), name the rewrite, and widen to a full
review where the rewritten area is large.

## Review the increment

1. Diff previous → current. When master was merged into the branch, exclude the
   changes that came only from the merge: compare against the new merge base and
   keep only hunks that differ from what the base brought in.
2. Run the normal review contract on that increment, including the design pass.
3. Check whether the increment touches code an earlier finding depended on; an
   earlier "no finding" area can regress.

## Check every earlier finding

For each finding from the previous review, and each open thread from others, give
one status from the current code, not from a reply or a resolved flag:

- **fixed:** the problem no longer exists; name the commit or line that fixed it;
- **partly fixed:** some of it remains; the remainder goes through the finding gate
  as a narrowed finding;
- **not addressed:** the code is unchanged in that respect;
- **outdated:** the code it discussed was removed or no longer applies;
- **disputed:** the author replied with a counter-argument. Verify the argument
  against the code. If it holds, mark the finding withdrawn and say why.

## Report

Use the same six parts. Summary names both SHAs and states that this is a
re-review. Findings holds new findings from the increment and narrowed findings
that survived. Earlier findings are listed in Summary by status, one line each,
fixed and outdated counted rather than listed when there are many. The Verdict
covers the current head as a whole: an earlier blocker that is not addressed keeps
it blocking.
