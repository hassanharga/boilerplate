# Prove It: Minimal Reproductions

Read when a finding depends on how a language, runtime, library, or framework
behaves — parsing, coercion, validation order, retry or timeout semantics, date and
number handling, concurrency, ORM or driver behavior — and that behavior cannot be
settled by reading the repository's own code and tests.

A reviewer's memory of library behavior is the most common source of confident,
wrong findings. A ten-line reproduction against the installed version turns "I think
X does Y" into "X 4.2.1 does Y", and it is usually faster than arguing from docs.

## When to reproduce

- The finding's trigger or impact rests on third-party or language behavior.
- The behavior is version-sensitive, or official docs are ambiguous.
- The finding would be blocking, or the author is likely to dispute it.

Skip it when the repository's code, an existing test, or authoritative versioned
documentation already settles the question. Cite that instead.

## Rules

- Write the reproduction in the session scratch directory, never in the reviewed
  repository. Keep it to the smallest code that shows the behavior.
- Use only what is already installed for this repository: its runtime, its
  dependencies at their resolved versions. Do not install, upgrade, or download
  anything. Running the interpreter from the repository root so it resolves the
  installed packages is fine; writing files there is not.
- Mirror the changed code's real inputs and configuration closely enough that the
  result transfers. When the change itself can be imported without side effects,
  import it instead of re-implementing it.
- Compare before and after when the claim is a regression: run the same input
  through the old and the new logic.
- Never run code that touches networks, databases, queues, or shared services.
  Reproductions are pure and local.
- Record the exact command, the resolved library version, and the output.

## Using the result

- Reproduction confirms the claim: the finding cites it in `Issue:` with the version,
  for example "With Joi 18.2.3 the new logic accepts …; the old logic rejects it".
- Reproduction contradicts the claim: drop or rewrite the finding. Do not keep it on
  the strength of the original reasoning.
- Reproduction is not possible (missing runtime, behavior needs infrastructure): the
  claim is a `Question - Non-blocking` at most, unless other evidence settles it.

Mention reproductions in Summary in one clause, as verification that ran.
