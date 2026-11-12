# Stale Guideline Reporting

Read this reference when a review exposes cached guidance that no longer matches
current evidence. The job here is to protect the current review and record the
problem — never to fix it mid-review.

## When a rule is suspect

A cached rule is stale for the current review when:

- its version range does not match the project's pinned version;
- version-matched official documentation or source contradicts it;
- its factual claim cannot be verified against an authoritative source;
- the architecture it assumes is not the one this repository uses.

## Protect the current review

1. **Quarantine the rule.** Do not use it as evidence for any finding.
2. **Decide from current evidence instead** — repository instructions, pinned
   versions, configuration, code, tests, and version-matched primary documentation.
3. **Continue the review.** Never block or delay it waiting on guidance to be fixed.

## Report it

Add a `Guidance:` line to the review report naming the reference file, the rule, the
pinned version it failed against, and what current evidence says instead. One or two
sentences. Put it only in Conflict notes, not in Findings or Verdict: it reports
a problem with the skill rather than a defect in the author's patch.

Example shape:

```text
Guidance: references/frontend.md's Next.js caching rule assumes v14 defaults; this
project pins v15.2, where the default changed. Rule excluded from findings; the
caching claim below was verified against current official documentation instead.
```

## Fix it later, elsewhere

Refreshing guidance is a separate job done outside any review, through
`turn-into-skill`'s reference-refresh path. A reported `Guidance:` line or an explicit
refresh request can trigger it. It inspects dated and undated cached claims;
`Last verified` headers help age-based discovery but are not a prerequisite.
It checks claims against their sources, applies mechanical confirmations, and
proposes substantive changes for approval. Add or advance a verification date only
after checking the actual source; a historical snapshot date is not proof of a
fresh verification. Investigation prompts do not need artificial freshness stamps.

Two things stay out of the skill regardless of who fixes it:

- **A one-off project fact** belongs in that repository's own instructions, not in
  shared guidance.
- **Duplicated documentation** belongs at its primary source. Point reviewers there
  rather than copying a manual into a reference.

The durable fix is usually not a refresh at all — it is rewriting the rule so it
cannot go stale. Store *what to verify for the pinned version*, not the answer. A
reference that says "check whether the supplied AbortSignal propagates to the
transport" stays correct across versions; one that states what the current version
does will not.
