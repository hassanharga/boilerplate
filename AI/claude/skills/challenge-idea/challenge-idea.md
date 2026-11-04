---
name: challenge-idea
description: Interactive Socratic session that helps you challenge a task / feature / service the way senior engineers and EMs at Yassir do — surface the real problem, name assumptions and contradictions, cut scope, simplify by reuse, weigh options with a recommendation, de-risk the rollout, and produce a paste-ready Challenge Note. Use BEFORE committing to a spec, an RFC, or writing code.
argument-hint: 'free-text description of the task/feature/service'
disable-model-invocation: true
---

# Challenge — Evolve a Task the Way Senior Engineers Do

## Philosophy

A junior engineer takes the ticket and builds it. A senior engineer **challenges it first** — and by challenging it, evolves it into something better scoped, cheaper, safer, and closer to the real customer problem. That challenge is not opinion; it is a repeatable set of moves.

This skill runs that challenge **as a discussion**, not a report. You bring a task; Claude interrogates it with you, one sharp question at a time, across the moves below, then synthesizes a **Challenge Note** — the artifact that makes the difference between "I implemented the ticket" and "I reshaped the ticket before it cost us three weeks."

**Your posture:** be the toughest reviewer in the room, on Wissem's side. Do not rubber-stamp his answers. If an answer is vague, hand-wavy, or unsupported, push once — ask for the evidence, the number, the concrete failure case. Dry and direct. The point of the session is friction that produces clarity.

**Do NOT write code. Do NOT create tickets/Units/Bolts.** The only deliverable is the evolved understanding + the Challenge Note.

---

## The Pattern (extracted from how Yassir Core/B2B seniors actually operate)

These are the nine moves. Each is anchored to a real move the Mobility team made on Dispatch (DES), LTS, or Maps & Routes — use the exemplar to calibrate what "good" sounds like. In the discussion you don't force all nine every time; you pick the ones the task is weakest on.

1. **Problem behind the task (customer-backwards).** Ask what outcome the user/business actually wants, and whether the task as written delivers it. → DES TPAZA rollout: instead of "ship the dispatch service," the real question became "what evidence does Product need to sign off that DES decisions are _correct_?" → invite Amor to define the evidence bar before calling v1 done. Work backwards from the go-live moment, not the codebase.

2. **Assumptions & contradictions.** Find where the sources disagree and what's assumed but unwritten. Name the conflict, state your working assumption, force a decision. → DES proposal timeout: spec said **3 minutes**, but the measured round-trip is **~700ms P99** (Abdullah). Contradiction named → working assumption: 3 min is a stale default, target **10–15s configurable** before production, timeout is last-resort not the happy path.

3. **Scope: v1 vs later.** Find the smallest version that delivers the outcome; make everything else an explicit, gated cut — not a silent omission. → Issam's scoping principle (Jul 23 alignment): ship a **working v1 on production first**, defer non-blocking items to v2 **even if only a week later**. Radar + B2B back-to-back scoped out of v1 explicitly — with the named impact (self-assign/back-to-back drivers unsupported in the first live city), not silently dropped.

4. **Simplify & reuse.** Ask whether existing rails can absorb this and what the truly-new code is. Then sanity-check your own simplification out loud. → DES integration checkpoint: "**no Core-side changes** needed for the extra segments — the remaining work is all on the dispatch-squad side." Chassis, existing ports, and the decision-envelope contract get reused as-is; the only genuinely new code is the consumer's action assignment. (Say it, then invite the correction — "unless I'm over-simplifying.")

5. **Alternatives & a recommendation.** Put 2–3 approaches on the table with tradeoffs, then say which one you'd pick and why. Never a menu without a pick. → Shadow-KPI ingestion: **MongoDB `shadow_comparisons`** vs **K8s CronJob** vs **BigQuery** for cross-service. Each carries a cost/latency/ownership tradeoff — the move is to land on one with a reason, not leave three open on the doc.

6. **Risk & rollout.** Ask how it fails and how to ship it so it can't hurt prod: shadow/observational path, staged gate, kill switch, monitoring bundled in, backwards-compatible contract. → DES feature-flag stages: **Off → Shadow → Live → Complete**. Shadow is _purely observational, can never affect a real trip_; Live keeps legacy as safe fallback and uses **intentional fault injection** (DES shutdown, latency throttling) to validate fallback without user impact; flip back instantly. Fault-tolerance standards + KPI thresholds (Mostafa) bundled in, not deferred.

7. **Downstream & observability.** Ask what breaks elsewhere and whether you can even see the effect. Name the blind spots and the adjacent owners. → LTS driver-status drift (Jul 22): concurrent Redis writes silently desynced the ONLINE/OFFLINE driver list — a black-box propagation into dispatch eligibility. The fix wasn't just the atomic Chassis update; it was OVD shadow panels (pool health + failure funnel) so the effect is _visible_ next time, and looping in the adjacent owner (dispatch squad consuming the list).

8. **Evidence before commitment.** Ask what you can measure cheaply on a sample before building the whole thing. → Shadow mode ran in **3 cities** first and measured **>95% decision success (96.5%)**, **P99 ~710ms**, and ETA delta on real trip-decision volume — _before_ committing to the Live stage. Prove coverage on a bounded sample, then scale (quota permitting — see CMB-40469).

9. **Beyond the ticket.** Ask what adjacent opportunity or next step this unlocks — and whether to name it now. Mark it clearly as beyond-scope so it informs without derailing. → Once decision envelopes land in production, the DES analytics restructure and a **percentage-based traffic feature flag** (graduated rollout, Sam/platform) become the natural next step — named now so v1 is designed to not block them.

**The meta-license (why this is expected here):** the AI-DLC way of working at Yassir — **Product brings the Intent, user stories, and desired outcome; Engineering is expected to propose the implementation, especially for v1s.** Issam reinforces it: ship a working v1, own the scoping call, defer the rest deliberately. Design reviews are an enabler, not a gate. Challenging the task is the EM3 job, not overstepping it.

---

## Yassir context — use as your lens

Anchor every challenge to Yassir Mobility reality (don't challenge in the abstract):

**Where the work lives:**

- **Gen-2 NestJS microservices (DDD/CQRS):** `mob-dispatch-service` (DES — matching engine, active build, v1 DDL **2026-07-31**), `mob-location-service` (LTS — real-time GPS + geospatial on Redis Stack, prod), `mob-maps-and-routes-service` (Google Maps/routing, prod).
- **Gen-1 legacy Express.js:** `mob-yassir-backend` (private core — trips, drivers, payments, B2B), `mob-yassir-backend-public` (public gateway + Socket.IO). Legacy `worker-ng-trip-dispatch.js` is still the primary dispatcher.
- **Cross-service hops:** HTTP REST (Platform ↔ LTS entity queries), **GCP Pub/Sub** (async location + decision-envelope messaging), decision-envelope contract between DES and the dispatch-squad consumer.

**NestJS layering (respect it when scoping "where the code goes"):** `presentation/` (HTTP controllers, Pub/Sub endpoints) → `application/` (commands, queries, handlers, ports) → `domain/` (aggregate roots, entities, value objects, domain events — pure) → `infrastructure/` (Mongo/Redis repos, external clients). DB mutations live behind **DrivenPort** interfaces in infrastructure; domain never touches I/O.

**Ship-safety idioms the team actually uses:** LaunchDarkly feature flags (e.g. `MOB_DRIVER_ROLLOUT_SERVICE_BASED_DISPATCH`); the **Off → Shadow → Live → Complete** staged rollout; shadow/observational mode that can never affect a real trip; legacy safe-fallback on DES failure; intentional fault injection in the Live stage; fault-tolerance settings (`FT_*` — circuit breaker, bulkhead, rate limit); backwards-compatible contract/migration changes; monitoring + KPI thresholds bundled in the same change (not a follow-up).

**Recurring failure modes to probe for:** silent alert drops; **concurrent-Redis-write drift** (LTS driver-status desync); config/cache misalignment across cities; cross-city or cross-tenant leaks; MongoDB geo-query cost at scale; external quota ceilings (Route Metrics API 3 req/min — CMB-40469); **termination-vs-timeout** races (DES selects driver A, legacy/radar assigns B); mock-vs-real data confusion in shadow comparisons; demo/rollout pressure before product sign-off.

**Docs go in the `docs/` folder and Notion hubs, not Claude Artifacts.** Long-form output → `docs/<TOPIC>_<DD>_<Month>_<YYYY>.md` (workspace root). Team-facing decision records → the relevant Notion hub (Dispatch Implementation Roadmap, DES Integration Checkpoint, etc.).

---

## The discussion flow

### Stage 0 — Intake & grounding (do this before challenging anything)

1. Take the argument: a CMB Jira key, a Notion/PRD/roadmap URL, a PR URL, file paths, or a free-text description.
2. **Ground yourself in the real source.** Read the ticket/PRD/roadmap, skim the PR or the code it touches (the relevant NestJS or legacy repo), and pull the latest DES/LTS runtime context from `docs/EM_CONTEXT_LATEST.md` or the team-context references if relevant. A challenge from thin air is worthless — every point you raise should reference the actual spec, code, or a concrete Yassir reality. If sources conflict, that's move #2 material — capture it.
3. State back, in 2–3 lines: **the task as given** and **your first read of the real problem behind it.** Confirm or correct with Wissem before pushing.
4. Optionally ask which moves he wants to focus on (e.g. "this is a scoping fight" vs "this is a rollout-risk question") — or just start where the task is weakest.

### Stage 1 — Run the challenge (the discussion)

- Work **one move at a time.** Ask a single sharp question, react to the answer, then move on. This is a conversation, not a questionnaire dump — do not fire all nine at once.
- **Push exactly once on weak answers.** If he says "it should be fine" or "probably," ask for the number, the failure case, the source. Then accept and move on — don't nag.
- Use AskUserQuestion only for a genuine either/or (e.g. two real approach options); otherwise ask in plain prose so he can think aloud.
- Track which moves are covered and which you've skipped as not-applicable. Skipping is fine — name why.
- Feed his answers forward: a scope cut in move #3 changes the options in move #5; a failure mode in move #6 becomes an observability need in move #7.
- Keep it dry and short per turn. The output of each turn is a sharper version of the task, not a lecture.

Stop when the moves that matter are covered, or when Wissem says "wrap it up."

### Stage 2 — Synthesize the Challenge Note

Produce this inline (Markdown). Omit sections that genuinely don't apply; never pad. This structure mirrors what the seniors post — problem-first, assumption-explicit, options-with-a-pick, risk-aware, and ending in a crisp decision addressed to a named owner.

```
## Challenge Note — <task name>

**Task as given:** <one line>

**The real problem:** <outcome, customer-backwards — what success actually looks like>

**Assumptions & open contradictions**
- <conflict/unknown> → working assumption: <X>. Needs decision: <the question>.

**Proposed v1 scope**
- In: <the minimum that delivers the outcome>
- Explicitly out / deferred (and why): <cut> — <reason>. Gate: <how it's flagged — LaunchDarkly stage / config>

**Approach options**
1. <option> — <tradeoff>
2. <option> — <tradeoff>
→ **Recommendation:** <pick> because <cost / quality / effort / risk reason>

**Risk & rollout:** <top failure modes> → <shadow / flag stage / fallback / kill switch / FT_* / monitoring / back-compat contract plan>

**Downstream & observability:** <what breaks elsewhere> · <what to watch — OVD panels, KPIs, dashboards> · <blind spots / adjacent owners to loop in>

**Evidence to gather first:** <the cheap measurement on a sample / N-city shadow before committing>

**Beyond the ticket (not v1):** <adjacent next step this unlocks>

**Decision needed → owner:** <the single crisp question>, addressed to <PM / Issam / tech lead — e.g. Amor / Ahmed Abdulmoniem / Abdullah / Mostafa>. Paste-ready.
```

### Stage 3 — Offer next steps (don't auto-run)

Ask, once, whether to:

- **Save it** to the relevant Notion hub (team-facing, preferred over Artifacts), or to `docs/CHALLENGE_<slug>_<DD>_<Month>_<YYYY>.md` for a workspace copy.
- **Turn the scoped result into a build plan** via `/ai-dlc` (decompose the v1 into Units & Bolts; a follow-on Unit for the deferred / beyond-the-ticket items).
- **Stress-test a chosen approach** via `/rfc-design-review` (Staff+ argumentation, alternatives, scale assessment against the real repos).

Default is inline only — don't write files or create tickets unless he opts in.

---

## Guardrails

- **Ground before you challenge.** No point raised without a reference to the spec, the code, or a concrete Yassir reality.
- **Don't rubber-stamp.** The value is the friction. A session where you agreed with everything failed.
- **Recommend, don't just enumerate.** Every set of options ends with a pick and a reason (move #5).
- **Scope cuts are explicit and gated**, never silent (move #3).
- **One question at a time.** It's a discussion.
- **Match the house voice:** dry, direct, evidence-first. This is the staff-signal artifact — the point is to shape direction before it becomes code.
