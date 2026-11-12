---
name: debug-error
description: Use when a user reports a bug, error, crash, failing behavior, or unexpected result and the root cause has not yet been confirmed.
---

# Debug Error

Confirm the cause before changing code. The failure this prevents is the plausible fix:
a change that addresses a cause you never established, which either hides the symptom or
adds a second bug beside the first.

This skill supersedes general systematic-debugging guidance when a specific error or
failing behavior has been reported. Use the general process instead when there is no
identified symptom to work backward from.

## Start from what you already have

Recover the error, the reproduction, and the relevant code from the conversation, the
repository, and the failing output before asking the user anything. A stack trace plus
the file it points at is usually enough to begin.

Ask only for what is genuinely missing and would change the diagnosis — most often the
exact reproduction, the environment, or what changed recently. Ask those in one short
batch and keep working on everything that does not depend on the answer. Do not ask the
user to restate information they have already given, and do not hold the diagnosis
behind a form.

## Rank the causes

State the observed problem in your own words first, so a wrong assumption surfaces
immediately. Keep unconfirmed explanations out of that restatement.

Then list the 3–5 most likely causes, most probable first, each with reasoning tied to
the actual evidence. Every candidate must be mechanically capable of producing the exact
reported symptom — if it would produce a *different* error, it is not a candidate for
this one. That test eliminates more hypotheses than any other.

## Check them yourself

For each cause, identify the fastest check that confirms or eliminates it: a targeted
log line, a read-only inspection, a one-line test. Prefer checks that discriminate
between candidates rather than confirming one in isolation.

Then run them. You have the repository and a shell — running the check is faster and
more reliable than describing it and waiting. Stop and ask the user only when the check
needs something you do not have: their environment, credentials, a device, a production
system you must not touch, or a reproduction only they can trigger.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final diagnosis, and every external
write stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means verifying independent hypotheses concurrently. Each subagent gets one
candidate cause and its check, and returns the evidence for or against it. Ranking,
elimination, and the causal conclusion stay with the main agent.

Report what the checks actually showed, including results that eliminated a candidate —
a ruled-out cause is real progress and stops it being re-proposed later.

## Fix only what the evidence supports

If the cause is still unconfirmed, say what remains unknown, run the next smallest
discriminating check, and repeat. Do not let an unresolved investigation drift into
trying a fix to see whether it helps.

Once the evidence confirms a cause:

- write the minimal fix for that cause;
- explain the mechanism — why this change makes the observed behavior impossible;
- name the focused tests or checks that verify it, and run them.

## Guardrails

- A plausible cause is not a confirmed cause. Say which one you have.
- No shotgun changes, and no menu of speculative fixes for the user to try.
- Do not refactor unrelated code or fix problems the user did not report. Mention them
  separately.
- Keep each investigative step small, reversible, and tied to exactly one hypothesis.
