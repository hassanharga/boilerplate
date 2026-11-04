---
name: write-rfc
description: >-
  Write a well-structured engineering RFC (Request for Comments) / design doc /
  technical proposal, then publish it wherever the author wants — a local
  Markdown file, a Notion page, or a Confluence page. Use this whenever the user
  asks to "write an RFC", "draft a design doc", "write a technical proposal",
  "document this architecture decision", "propose a design for X", or wants to
  turn a rough idea, ticket, or Slack thread into a reviewable design document.
  Trigger even when they don't say the word "RFC" — if they're proposing a
  non-trivial technical change and want it written up for others to review,
  this is the skill. Do NOT use for PRDs (product requirements), plain READMEs,
  or short code comments.
---

# Write an RFC

Turn a design decision into something a team can review, argue with, and approve. The
value is not the prose — it is forcing the problem to be stated crisply, the alternatives
to be shown, and the tradeoffs to be admitted. A good RFC makes disagreement productive:
a reader can see exactly what is proposed and where they would push back.

## Scope boundary

- Product requirements, user outcomes, and release scope belong in a PRD — use
  `write-full-prd`.
- Interface layout, tokens, states, and accessibility belong in a design brief — use
  `ui-ux-brief`.
- When an accepted RFC changes a Yassir Mobility service's architecture, its Design
  Guide is now stale. Say so in the handoff and use `service-design-guide` to reconcile
  it. Nothing else connects those two documents.

## Decide whether to draft or interview

Draft immediately when the input contains a real problem and a proposed direction, a
linked ticket, a code area, or a prior discussion. Fill genuine gaps with
`> **Open question:**` callouts or `_TODO(author): …_` placeholders rather than inventing
facts.

Interview first only when the input is too thin to draft from — a single vague line with
no direction. Ask 3–5 sharp questions in one batch, covering only what cannot be
inferred: what is broken today and who feels it, the rough direction in mind, fixed
constraints, approaches already ruled in or out, and what is explicitly out of scope.

When uncertain, draft from what is available and list the assumptions at the top under
Open questions. A concrete draft the author can correct is worth more than a blank
interview.

## Research the alternatives

Read `references/template.md` for the section contract before writing.

Alternatives are the section that decays first when an RFC is rushed, and the section
reviewers rely on most. Establish each rejected option well enough to state honestly why
it lost.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard, and
require it to return findings with sources — never decisions, conclusions, or writes.
Reconciliation, conflict resolution, the final document, and every external write stay in
the main agent. If subagents are unavailable or a pass fails, run the same passes
sequentially without reducing coverage.

Here that means one pass per candidate approach or prior-art question. Each returns
sourced findings and constraints. Choosing the proposal, weighing the tradeoffs, and
writing the document stay with the main agent.

## Write the draft

Use the codebase's real component names, real constraints, and real numbers where they
exist. Keep it as short as the decision allows — length is not quality. Cut sections that
genuinely do not apply and say so in one line rather than padding.

Hold to these:

- **State the problem before the solution.** If a reader cannot articulate the problem
  after the Motivation section, the RFC has failed regardless of how elegant the design
  is.
- **Alternatives must be real.** Status quo plus at least one seriously considered
  approach, each with why it lost. An RFC with no credible alternatives reads as a
  decision already made, and reviewers cannot contribute to it.
- **Admit the tradeoffs and risks.** Costs, failure modes, and the parts still uncertain.
  Hiding them destroys trust and they surface in review anyway.
- **State non-goals.** They stop review sprawling into unrelated territory.
- **Write for the reviewer.** Assume a competent teammate without the context in your
  head. Define domain terms on first use.
- **Match scope to stakes.** A small decision gets a short RFC.
- **Respect the reader's time.** The audience is a busy human who skims first. If they
  cannot find the decision and the tradeoffs quickly, extra thoroughness makes the RFC
  worse, not better. Do not inflate a document for the benefit of an AI reviewer.

Never invent a benchmark, an approval, a reviewer, a commitment, or a constraint.

## Output format

Produce clean GitHub-flavored Markdown that renders correctly as a `.md` file and when
converted to Notion or Confluence. Use `#` for the title and `##` for sections, tables for
comparisons, and fenced code blocks for schemas, APIs, and diagrams. Keep the metadata
block at the top — see the template.

## Publish

The author chooses the destination for every RFC. Ask where it should go — local Markdown
file, Notion page, Confluence page, or left in chat — then follow
`references/publishing.md`. Never publish to a shared destination without confirming;
it is visible to others.
