---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

# Grill Me

Put adversarial pressure on a plan the user has already committed to. This is not
discovery and not gap-filling — it assumes a plan exists and tries to find the place
where it breaks.

## How to run it

Ask **one question at a time**. Every other skill here batches questions; this one must
not. Each answer determines which branch is worth opening next, and a batch lets the
user answer the easy three and skip the one that matters.

If the codebase, the repository instructions, or a linked document can answer a
question, go read it instead of asking. Spending the user's attention on something you
could have looked up is the fastest way to lose it.

Work down the decision tree. When an answer creates a new dependency, follow it before
returning to the parent. Say when you are moving to a new branch so the user can tell
how much is left.

## What to press on

Ordinary clarifying questions produce ordinary answers. Use pressure that forces a real
commitment:

- **Failure mode.** What breaks first, and how would you know it broke?
- **Cheapest disconfirming test.** What is the smallest thing that would prove this
  wrong, and why has it not been run?
- **Scale.** What happens at ten times the volume, or with one dependency down?
- **The alternative's case.** What would have to be true for the option you rejected to
  be the right one? If the user cannot argue it, they did not really reject it.
- **Reversibility.** If this turns out wrong in three months, what does undoing it cost?
- **The unowned part.** Which piece has no named owner, and who notices when it fails?

Challenge answers that contradict earlier ones. Name the contradiction directly and let
the user resolve it — that is the job, not a breach of it. Do not soften a real
objection into a suggestion, and do not keep pushing once the user has given a reasoned
answer you simply disagree with; record the disagreement and move on.

## When to stop

Stop when either is true:

- every decision on the tree has an answer the user would defend to a reviewer; or
- the remaining unknowns are explicitly parked, each with an owner and a trigger for
  revisiting.

Do not stop because the user sounds tired, and do not continue once the tree is
resolved. Unresolved-but-parked is a valid end state; unresolved-and-forgotten is not.

## What comes out

An interrogation with no artifact evaporates. Close with a compact record the user can
paste into an RFC, a PRD, or a ticket:

- **Decisions resolved** — the decision, and the reasoning that settled it.
- **Parked** — the open question, its owner, and what would trigger revisiting it.
- **Changed by this conversation** — anything the user revised while being pressed. This
  is the part that proves the exercise was worth it.

Keep it short. The value is in the resolution, not in a transcript.
