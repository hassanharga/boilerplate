# Conventional Comments & Constructive Feedback (Principle 5)

How to phrase review comments so they help the team improve instead of just
pointing fingers. The manifesto is blunt about this: review is an _amplifier_. A
healthy culture gets amplified into mentorship; a careless one gets amplified into
friction. Wording is most of the difference.

## Criticism vs. feedback

> "This is wrong, redo it." → criticism. Closes the conversation, triggers defense.
>
> "I noticed this loop re-reads the list on every iteration — that could get slow on
> large inputs. Could we hoist it out, or is there a reason it's inside?" → feedback.
> Opens a conversation, explains the why, leaves room for the author to know
> something you don't.

Three habits turn criticism into feedback. Apply all three.

### 1. Frame as a request or a question

Don't issue commands. Ask. A question also protects you when you're not 100% sure —
the author may have a reason you can't see from the diff.

- ❌ "Move this to a helper."
- ✅ "Could we pull this into a helper so the orchestrator stays focused?"
- ✅ "Is there a reason this lives here rather than in the mapper?"

### 2. Say "we"/"me", talk about the code — never "you"

"You" puts a person on trial. "We" makes it shared ownership (Principle 3: it's the
team's code, not the author's). Or just talk about the code itself.

- ❌ "You didn't handle the null case."
- ✅ "Looks like the null `userId` case isn't handled here — should we guard it?"
- ✅ "Can we add a guard for when `userId` is undefined?"

### 3. Apply OIR — Observe, Impact, Request

The **Impact** is the part most reviewers skip, and it's what makes a comment
persuasive instead of bossy. It answers "why should I care?"

- **Observe**: what you see, neutrally.
- **Impact**: what it leads to / costs.
- **Request**: the concrete change you're asking for.

> **suggestion:** This query runs inside the `for` loop _(observe)_, so it hits the
> DB once per item and will dominate latency on big batches _(impact)_. Could we
> fetch the set once before the loop and look up in memory? _(request)_

## Conventional Comments format

```
<label> [decorations]: <subject>

[optional discussion — context, reasoning, next steps]
```

Adhering to a consistent format sets reader expectations and is machine-readable.

### Labels

| Label          | Use it for                                                                                |
| -------------- | ----------------------------------------------------------------------------------------- |
| **praise**     | Something genuinely good. Leave at least one per review. Never fake it.                   |
| **issue**      | A real problem (user-facing or internal). Pair with a `suggestion` for the fix.           |
| **suggestion** | A proposed improvement. Be explicit about _what_ and _why_.                               |
| **question**   | A genuine concern you're unsure about. Asking can resolve it fast.                        |
| **nitpick**    | Trivial, preference-based. Always non-blocking by nature.                                 |
| **todo**       | Small, necessary change — separated from `issue`/`suggestion` so it's clearly low-effort. |
| **thought**    | A non-blocking idea sparked by the review; can seed future work or mentoring.             |
| **chore**      | A process task needed before acceptance (link the process if you can).                    |
| **note**       | Always non-blocking; just something to be aware of.                                       |
| **typo**       | Like `todo`, but the issue is a misspelling.                                              |
| **polish**     | Like `suggestion`, where nothing's wrong but quality could rise.                          |

### Decorations

Optional parenthesized, comma-separated context after the label. Keep to a minimum
(one or two) so they aid rather than clutter.

| Decoration         | Meaning                                         |
| ------------------ | ----------------------------------------------- |
| **(blocking)**     | Must be resolved before the change is accepted. |
| **(non-blocking)** | Should not prevent acceptance.                  |
| **(if-minor)**     | Resolve only if the fix turns out trivial.      |
| **(security)**     | This comment concerns security.                 |
| **(performance)**  | This comment concerns performance.              |

Example: `suggestion(non-blocking, performance): ...`

### Worked examples

> **praise:** The retry logic here is clean and the back-off is well chosen 👍

> **issue(blocking):** `dispatch-run.orchestrator.ts:142` — when no job is claimed,
> the run state is never persisted, so a restart loses the terminal status
> _(impact)_. Can we persist the failed state before returning, the way the
> claimed path does?

> **question:** `entity-id.value-object.ts:30` — at this point does it matter which
> thread won? If two requests race, could we end up with two ids?

> **nitpick(non-blocking):** `little star` → `little bat` — and maybe update the
> other references too.

## Review process etiquette

- **Review all at once.** One complete pass with every comment, not comment-by-comment
  drips. If the author then pushes changes, do another full pass. Aim for **≤2
  iterations** to keep frustration low, and stay consistent between iterations — don't
  reverse a request you made last round without a reason.
- **Reply to every comment** (as reviewer _and_ author), even with an emoji, so the
  sender knows it was seen and considered. "Done", "Fixed!", 🚀, or "Added a test for
  this" — then resolve it.
