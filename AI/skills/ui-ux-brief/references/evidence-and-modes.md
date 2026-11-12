# Evidence, modes, and change safety

Use this reference before deciding how much work to produce or which source wins.

## Pick the smallest useful mode

### Quick decision

Use for a typeface question, one token, a component choice, or a short visual
opinion. Answer the decision directly, state the evidence and tradeoff, and list
only the information still needed. Do not create a file.

### Feature brief

Use for a bounded flow, screen, or component family. Include only relevant
context, flow, layout, reused components, states, responsive behavior,
accessibility, draft content, and open questions.

### Full brief

Use for a new product, a broad redesign, or an explicit request for DESIGN.md.
Cover the complete system needed for the agreed scope, not every hypothetical
future feature.

### Refresh

Use when an approved design guide already exists. Preserve its structure,
terminology, and stable decisions. Propose a focused update and identify:

- inherited decisions that remain unchanged;
- new decisions;
- intentional divergences and their migration cost;
- stale material that should be removed or marked historical.

Never replace the guide with a new template just because another format is
cleaner.

### Audit

Use when the user asks whether a design or guide is coherent, accessible,
complete, or ready. Report evidence, impact, and recommendations. Do not rewrite
or publish without authorization.

## Source status

Label important material when its status is not obvious:

| Label | Meaning |
| --- | --- |
| Approved | A named authority has accepted it |
| Observed | Present in the current product or code |
| Required | Comes from a verified requirement or standard |
| Proposed | Agent or team recommendation awaiting a decision |
| Assumed | Needed to proceed but not supported by evidence |
| Open | A decision is still required |

Do not describe observed inconsistency as an approved design rule. Do not describe
a proposed value as an existing token.

## Existing-system inventory

For scan-and-adopt work, inspect only what the scope needs:

- guide location, owner, and last meaningful update;
- token sources and generated outputs;
- component library, variants, and interaction behavior;
- routes or screens in scope;
- typography, iconography, layout primitives, and content conventions;
- responsive, localization, and accessibility behavior already implemented;
- known exceptions, experiments, or migration work.

Prefer semantic tokens and component contracts over values copied from rendered
screens. Screenshots show one state; source and approved documentation explain the
system.

## Resolving conflict

1. Name the two sources and the exact conflict.
2. Determine whether either source is approved, generated, obsolete, or merely
   observed.
3. Follow explicit product and safety requirements.
4. Preserve the established pattern when neither source has higher authority.
5. Record the unresolved decision and its impact when authority is unclear.

Do not average incompatible values or silently choose the newer-looking option.

## Questions worth asking

Ask only questions that could change the result:

- Who performs the task, how often, and under what conditions?
- Which outcome matters, and which error is costly or dangerous?
- Which journeys and surfaces are in scope?
- Which design guide or component system is authoritative?
- Which platforms, locales, input methods, and connectivity states matter?
- Which legal, safety, brand, or accessibility constraints are approved?

For a quick decision, one or two questions may be enough. For a full brief, ask
one batch of at most six.

## Artifact safety

- Do not overwrite an existing guide without approval.
- Do not create DESIGN.md when the user requested advice only.
- Do not publish to Figma, Notion, a repository, or another shared system without
  authorization.
- Preserve the destination's existing structure unless the user approved a
  migration.
- If a write is approved, show the affected path and verify the resulting file.
