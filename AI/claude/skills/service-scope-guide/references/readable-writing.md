# Readable writing

The Scope Guide is read by product managers, ops, QA, and engineers from other squads, often in a
hurry and not always in their first language. If a requirement can't be understood on one read, it
won't be agreed on properly. Write so a newcomer to the team could explain the requirement back
after reading it once.

## Contents

- [Rules](#rules)
- [Summary and story](#summary-and-story)
- [Scenarios](#scenarios)
- [Before and after](#before-and-after)
- [Check before presenting](#check-before-presenting)

---

## Rules

- **Lead with the outcome.** The first sentence says what changes for whom. Background comes after.
- **Short sentences, one idea each.** Aim for 20 words or fewer. Split sentences joined by
  "and", "which" or a semicolon when each part is a separate fact.
- **Name who does what.** "The client system cancels the request", not "the request is cancelled".
- **Use everyday words.** Say "use", not "leverage"; "start", not "initiate"; "must", not "shall".
- **Define before you use.** Use glossary terms as defined, and add missing ones to the glossary.
  Spell out an acronym the first time it appears in a row: "estimated time of arrival (ETA)".
- **Break up noun stacks.** Rewrite "candidate job proposal timeout state handling" as "what happens
  when a driver doesn't answer an offer in time".
- **Concrete over abstract.** Give numbers with units ("within 2 seconds", "7 days ahead"). Add one
  short example when a rule is hard to picture.
- **Code format only for contract names** that a consumer really sees, such as a field or a status
  value. Explain in words what the value means the first time it appears.
- **Fewer, clearer items.** Five sharp scenarios beat ten overlapping ones. Cut any scenario that
  repeats another with a trivial change.

## Summary and story

- The `Summary` is two or three plain sentences a non-engineer can follow, then an optional
  "Example:" line using a real situation, such as a rider, a driver, or a city.
- The story's `So that` states a benefit someone outside engineering would recognize, such as fewer
  unassigned rides or a clearer message to the rider. "So that the pipeline is consistent" is not
  that kind of benefit.

## Scenarios

- The scenario title says the situation in plain words: "Rider cancels while the ride is waiting to
  be grouped", not "Cancel in POOLED state pre-flush".
- Each table row holds one fact. Put a second fact in an `AND` row instead of a longer sentence.
- `THEN` rows describe what someone can see: the rider, the client system, a downstream service,
  or an operator looking at a dashboard.
- Say the negative plainly: "no driver is offered the ride", not "no Candidate Job Proposal
  entity is emitted".

## Before and after

Before (dense, correct but hard to read):

> `strategyMode` is additive; existing consumers may continue reading `type` and the current EN-12
> response and correlation fields without interpreting AUTO as a runtime type.

After (same meaning):

> | | |
> | --- | --- |
> | **AND** | the envelope adds a new field, `strategyMode`, set to `AUTO` |
> | **AND** | the existing `type` field still says what actually happened: `IMMEDIATE` or `POOLED` |
> | **AND** | services that read only `type` keep working without changes |

Before:

> Leverage the candidate responsiveness signal to deprioritize low-acceptance-probability
> candidates in the ranked list.

After:

> Drivers who often ignore or reject offers move down the ranking, so riders are matched with
> drivers who are likely to accept.

## Check before presenting

Read the draft once as someone from ops or product would, then fix anything that fails:

1. Can the Summary be understood without knowing the code? If not, rewrite it.
2. Is any sentence longer than about 25 words? If so, split it.
3. Are any terms undefined, or any acronyms not spelled out? If so, define them or add them to the
   glossary.
4. Does every `THEN` describe something a person or system outside the service can check? If not,
   rewrite it.
5. Do two scenarios say nearly the same thing? If so, merge them.

Keep existing human-written text as it is unless the user asked for rewording. Readability edits to
approved rows are still changes and need approval.
