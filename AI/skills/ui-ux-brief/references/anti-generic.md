# Product-specific design decisions

Use this reference when a recommendation could have been copied into an unrelated
product. Familiar choices are allowed. Unexamined choices are not.

## Decision test

For each consequential choice, ask:

1. Which user need, environment, approved pattern, or technical constraint drives
   it?
2. What does the choice make easier?
3. What does it make harder?
4. Would the same choice still be right for a different product and audience?

If the only explanation is a broad adjective, the decision is not ready.

## Common weak defaults

| Weak output | What is missing | Better question |
| --- | --- | --- |
| Clean, modern, intuitive | Observable behavior or visual rule | What should be faster to notice or harder to do by mistake? |
| Untouched framework blue | Product, brand, or semantic rationale | Is the color inherited, required by the domain, or proposed? |
| Inter or a system font without comparison | Script, density, licensing, and legibility evidence | Which existing or candidate face best serves the actual content? |
| Cards on every screen | Information-task analysis | Is the user scanning, comparing, monitoring, or completing a sequence? |
| One modal for every task | Interruption cost | Does the task require isolation, or should it remain in context? |
| Toast for every outcome | Feedback hierarchy | Where should the result remain visible after the toast disappears? |
| Skeleton for every load | Timing and layout predictability | Is the wait noticeable and is the final shape stable? |
| Placeholder interface copy | Content behavior | Which exact recovery or next action must the message explain? |
| A large primitive inventory | Screen evidence | Which components do the agreed screens actually use? |

## Principles that settle arguments

A principle is useful when it can reject an attractive alternative. It should
name the condition and the accepted cost.

Weak:

> Keep the interface simple.

Useful:

> Keep the dispatch queue visible while details open. This uses more horizontal
> space, but operators can compare a request without losing their place.

Do not force a fixed number of principles. Two strong rules are better than three
generic virtues. A large product may need more.

## Choose layout from the task

- Scanning for one item usually favors a list with strong identifiers and search.
- Comparing rows favors a table with aligned values and a small-screen strategy.
- Monitoring favors a hierarchy of signals, not a wall of equal cards.
- Completing a sequence favors a focused form or staged flow.
- Browsing visual material may favor a grid.
- Responding to events favors a queue or feed with unresolved and resolved states.

These are starting points, not automatic answers. Existing approved patterns still
win unless the task exposes a real failure.

## Reference products

Use named products only when they clarify a specific pattern. Record what is being
adopted, what is being rejected, and why it fits this product. Do not use another
brand as a substitute for a design decision, and do not reproduce proprietary
assets or distinctive trade dress.

## Writing check

Remove:

- promotional claims and inflated adjectives;
- fake certainty;
- repeated Why and Instead of labels on routine details;
- long lists included only to sound complete;
- three-part slogans that do not change a decision.

Keep:

- concrete conditions and consequences;
- uncertainty where evidence is missing;
- short examples using the product's real language;
- an explicit tradeoff for decisions someone may challenge.
