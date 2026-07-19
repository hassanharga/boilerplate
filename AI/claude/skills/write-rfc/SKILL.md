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

An RFC turns a design decision into something a team can review, argue with, and
approve. The value is not the prose — it's forcing the author to state the
problem crisply, show the alternatives they considered, and be honest about
tradeoffs. A good RFC makes disagreement productive: a reader can see exactly
what is being proposed and where they'd push back.

Your job: produce a clear, honest, appropriately-scoped RFC, then help the
author put it where their team will read it.

## Workflow

1. **Decide draft-now vs. interview.** Look at what the user gave you.
   - **Enough to draft** (a description with a real problem + a proposed
     direction, a linked ticket, a code area, a prior discussion): draft
     immediately. Fill genuine gaps with clearly-marked `> **Open question:**`
     callouts or `_TODO(author): …_` placeholders rather than inventing facts.
   - **Too thin** (one vague line, "write an RFC for caching"): ask a short,
     targeted batch of questions first — see _Interviewing_ below. Don't
     interrogate; 3-5 sharp questions beat a long form.
   - When unsure, draft from what you have and list what you assumed at the top
     under "Open questions". A concrete draft the author can correct is more
     useful than a blank interview.

2. **Read the template.** Read `references/template.md` for the section-by-section
   structure and what "good" looks like in each section. Follow that structure.

3. **Write the draft.** Match the codebase/domain: use real component names,
   real constraints, real numbers where you have them. Keep it as short as the
   decision allows — length is not quality. Cut sections that genuinely don't
   apply (say so rather than padding).

4. **Publish where the author wants.** After the draft is ready, **always ask
   where to put it** — the author decides per RFC. Offer: local Markdown file,
   Notion page, Confluence page (or "just leave it here for now"). Then follow
   `references/publishing.md` for the chosen destination.

## Interviewing (only when input is too thin)

Ask about the things you cannot invent. Batch them; don't drip one at a time.

- **Problem:** What's broken or missing today? Who feels the pain, how often?
- **Proposal:** What's the rough direction you have in mind (if any)?
- **Constraints:** Deadlines, systems that must not change, team size, budget.
- **Alternatives:** Are there approaches you've already ruled in or out, and why?
- **Scope:** What's explicitly _not_ in scope?

If the user answers some but not all, proceed with what you have and mark the
rest as open questions in the draft.

## Principles that make RFCs good

- **State the problem before the solution.** If a reader can't articulate the
  problem after the Motivation section, the RFC has failed regardless of how
  elegant the design is.
- **Alternatives are mandatory and must be real.** "We could do nothing" and one
  seriously-considered other approach, each with why it lost. An RFC with no
  credible alternatives reads as a decision already made — reviewers can't
  contribute.
- **Be honest about tradeoffs and risks.** The costs, the things that could go
  wrong, the parts you're unsure about. Hiding these destroys trust and they
  surface in review anyway.
- **Goals AND non-goals.** Non-goals prevent scope-creep arguments during review.
- **Write for the reviewer, not yourself.** Assume a competent teammate who
  doesn't have the context in your head. Define domain terms the first time.
- **Match scope to stakes.** A small decision gets a short RFC. Don't inflate a
  one-page decision into ten pages of ceremony.

## Output format

Produce clean GitHub-flavored Markdown that renders correctly both in a `.md`
file and when converted to Notion/Confluence. Use `##` for top-level sections
(the title is `#`), tables for comparisons, and fenced code blocks for schemas,
APIs, or diagrams. Keep a metadata block at the top (author, status, date,
reviewers) — see the template.
