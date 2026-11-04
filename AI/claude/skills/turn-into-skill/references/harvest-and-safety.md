# Harvest and safety

Use this checklist to recover the reusable workflow without leaking instance-specific or sensitive
material.

## Harvest map

For each source, record:

| Evidence | Capture | Exclude or parameterize |
| --- | --- | --- |
| Goal | Repeatable outcome and success criteria | One-off business context that does not change execution |
| Inputs | Required formats, sources, and discovery rules | A single user's identifying path or account |
| Actions | Non-obvious sequence, decisions, stopping conditions | Tool chatter and routine steps agents already know |
| Commands | Stable interface, necessary flags, prerequisites | Tokens, live targets, temporary paths, transient IDs |
| Corrections | Final rule and failure it prevents | Frustrated wording or personal criticism |
| Failed attempts | Reusable symptom, cause, and countermeasure | Incidental errors unlikely to recur |
| Output | Accepted shape and quality bar | Exact content when only the structure is reusable |
| Verification | Checks that established success | Claims unsupported by captured output |

Prefer the latest accepted behavior. When two sources conflict and neither clearly supersedes the
other, mark the conflict and ask instead of combining them.

## Sensitive-data gate

Before drafting, scan source notes, proposed instructions, examples, scripts, and command snippets.
Never persist:

- bearer tokens, API keys, passwords, cookies, session values, private keys, or secret files;
- credentials embedded in URLs, headers, environment variables, or command history;
- personal data that is unnecessary for the workflow;
- production payloads or internal content whose reuse destination is not appropriate.

Replace sensitive or variable material with meaningful placeholders such as `<service>`,
`<repository-root>`, `<token-from-secret-store>`, `<topic>`, or `<approved-production-target>`. State
how the value is discovered securely; never include a real secret as the example.

Internal URLs and repository paths are not automatically secrets, but they are often non-portable or
sensitive. Keep them only when they are a stable requirement, the destination is appropriate, and
their inclusion is necessary. Otherwise parameterize them.

Run a final source-to-draft comparison specifically looking for copied credentials and identifying
values. If the active environment has a secret scanner, use it on the staged package. A clean scan is
evidence, not permission to publish.

## Commands and tools

Classify every harvested command:

| Class | Treatment in the skill |
| --- | --- |
| Read-only and stable | Preserve the command when exact syntax is useful; parameterize values |
| Runtime-specific tool | Describe the capability first; include the command as one supported example |
| External or shared-state write | Preserve the confirmation gate immediately before execution |
| Destructive or production action | Resolve the exact target, require explicit approval, and include verification/rollback guidance |
| Secret-bearing command | Never copy verbatim; replace the secret source and sensitive values |
| Failed command | Include only when its failure teaches a reusable diagnostic or prohibition |

Do not infer that because a command was authorized once, it may run automatically in future uses.

## Generalization test

For every concrete value, ask:

1. Does changing this value preserve the workflow?
2. Can a future agent discover it from the current project or runtime?
3. Is it a stable company convention, a repository rule, or only this instance?

Parameterize instance values. Keep stable conventions with their source or discovery rule. Read live
project instructions at execution time instead of freezing mutable repository policy into a global
skill.

Generalize only as far as evidence supports. A workflow demonstrated for one language, repository,
or provider does not automatically apply to all of them. State the verified scope and add variations
only when the source or user confirms them.

## Authorization map

Extract where the original workflow required approval and why. Preserve gates for:

- production, destructive, or irreversible actions;
- publishing, posting, messaging, pushing, deploying, or external account changes;
- modifying an existing installed skill or shared configuration;
- installing dependencies or transmitting sensitive artifacts.

Do not carry over temporary approval, authentication state, or the identity of the original approver.
The future run must obtain current authorization from the current user immediately before the action.

## Human output

Write the generated skill for another capable agent, not as a transcript summary. Use direct, plain
instructions. Explain the reason for a non-obvious rule in one sentence. Remove praise, narrative,
internal deliberation, and repeated warnings. Preserve user-facing terminology and accepted output
style when they are part of the workflow's success.
