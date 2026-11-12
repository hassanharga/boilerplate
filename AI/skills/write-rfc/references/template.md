# RFC template & section guidance

Use this structure. Keep the metadata block, `#` for the title, `##` for
sections. Drop sections that genuinely don't apply and say why in one line
rather than padding. Guidance under each heading below is for _you_ — don't copy
it into the output.

---

# RFC: [Concise title — name the change, not the problem]

|               |                                                      |
| ------------- | ---------------------------------------------------- |
| **Author**    | [name]                                               |
| **Status**    | Draft · In Review · Accepted · Rejected · Superseded |
| **Created**   | [YYYY-MM-DD]                                         |
| **Reviewers** | [names / teams, or _TBD_]                            |
| **Related**   | [ticket / PR / prior RFC links, or _none_]           |

## Summary

> Two to four sentences. What is being proposed and why, in plain language a
> busy reader skims first. If they read only this, they should understand the
> decision. Write this last.

## Motivation / Problem

> What is broken or missing today. Concrete: who is affected, how often, what it
> costs (time, money, reliability, developer pain). Use real numbers or examples
> when you have them. This section earns the reader's attention — if the problem
> isn't real, nothing else matters.

## Goals & Non-Goals

> **Goals:** bulleted, specific, ideally measurable outcomes this RFC aims for.
> **Non-Goals:** what is explicitly out of scope. Non-goals are as important as
> goals — they stop review from sprawling into unrelated territory.

## Proposed Design

> The heart of the RFC. Explain the approach clearly enough that a competent
> teammate could critique it. Include, as relevant:
>
> - High-level approach / architecture (a diagram or ASCII sketch helps)
> - Key components and how they interact
> - Data model / schema / API changes (use fenced code blocks)
> - Failure modes and how the design handles them
>   Prefer showing the shape of the thing (interfaces, request/response, table
>   definitions) over long prose.

## Alternatives Considered

> At least "do nothing / status quo" plus one real alternative. For each: a
> sentence on the approach and why it lost to the proposal. A comparison table
> works well:
>
> | Option           | Pros | Cons | Verdict      |
> | ---------------- | ---- | ---- | ------------ |
> | Proposed: …      | …    | …    | ✅ chosen    |
> | Alternative A: … | …    | …    | rejected — … |
> | Do nothing       | …    | …    | rejected — … |

## Risks & Tradeoffs

> Honest list of what could go wrong and what you're trading away. Performance,
> complexity, migration risk, operational burden, security, team ramp-up.
> Where possible, note the mitigation.

## Rollout / Migration Plan

> How this ships without breaking things: phases, feature flags, backfills,
> backward compatibility, rollback plan, metrics to watch. Omit only if the
> change truly has no rollout concerns (say so).

## Open Questions

> Things not yet decided, or where you want reviewer input. This is where
> `_TODO(author)_` items and unresolved assumptions live. An RFC in Draft
> status is _expected_ to have these.

## Appendix (optional)

> Benchmarks, detailed schemas, references, prior art — anything supporting but
> not required for the main decision.
