# Evaluation

Evaluate the staged package before installation and the installed package afterward. Keep the test
set small but behavioral.

## Structural validation

Use the active runtime's current validator or the current Agent Skills reference validator when
available. Otherwise parse the frontmatter with a real YAML parser and verify:

- the directory and `name` match;
- the name meets the current length and character rules;
- the description is non-empty, within the current limit, and distinguishes when to use the skill;
- every referenced file exists at the stated relative path;
- optional frontmatter fields are supported by the current specification;
- no scaffold placeholders remain unintentionally.

Do not hardcode today's specification limits into a generated validator when current documentation is
cheap to retrieve. Record which validator or specification version/date was used.

## Trigger checks

Create realistic prompts from the user's wording:

- two or more that should trigger, including a casual or abbreviated phrasing;
- two or more near-misses that share keywords but need another skill or ordinary response.

Check selection using a fresh agent or the runtime's trigger evaluator when available. Do not merely
assert that the expected words appear in the description.

## Behavioral evaluations

For a substantial, safety-sensitive, or explicitly tested skill, run two or three fresh-context
scenarios with the staged skill. Give each evaluator only the request, skill path/package, and minimum
artifacts needed. Use a temporary workspace and prohibit external writes unless the user separately
authorized them.

Choose scenarios that exercise demonstrated risks:

1. the normal completed workflow with all information present;
2. missing, conflicting, or overlapping context;
3. sensitive values, risky actions, or runtime/tool variation when relevant.

Define observable expectations before running. Inspect the evaluator's decisions and produced
artifacts; do not accept its “passed” label without evidence. If instructions cause a failure, change
only the guidance needed for that observed behavior and rerun the affected scenario.

Use smaller/fast agents for routine behavioral checks when they can faithfully exercise the skill.
Use a stronger model only for a failure that depends on deeper reasoning. Avoid large repetitive
benchmark loops unless the user requests quantitative optimization.

## Scripts and coverage

Run focused tests for every new or changed script. Exercise successful input, relevant edge cases,
errors, and CLI behavior. Use the target repository's test runner and coverage policy when the skill
belongs to a repository.

Do not impose a universal coverage percentage. If repository policy or acceptance criteria requires
100% coverage, verify and report that metric. If it does not, report the focused tests that ran and
do not claim numeric coverage that was not measured.

## Installation verification

After installation:

1. compare the installed package with the validated staging package;
2. re-run structural validation against the installed path;
3. re-run changed script tests from the installed package when feasible;
4. verify the intended runtimes discover the canonical path or configured alias;
5. report unsupported or unverified runtimes plainly.

Do not say the skill is active everywhere merely because one runtime loaded it.
