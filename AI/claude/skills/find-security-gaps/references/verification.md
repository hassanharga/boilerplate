# Candidate verification

Security review is not pattern matching. Use tools to locate candidates, then prove
the path and impact in the actual application.

## Evidence model

For each candidate, record:

1. **Asset and boundary:** what is protected and which trust boundary may fail?
2. **Source or precondition:** what can the attacker control, observe, or cause?
3. **Path:** which handlers, services, transformations, queues, and stores carry it?
4. **Control:** what authentication, authorization, validation, encoding, isolation,
   or operational control is supposed to stop it?
5. **Sink or security operation:** what sensitive read, write, execution, disclosure,
   request, state transition, or resource consumption occurs?
6. **Impact and scope:** which users, tenants, data, systems, or availability are affected?
7. **Disproof attempt:** which framework behavior, invariant, deployment setting, or
   unreachable condition could make the candidate safe?

A suspicious source and sink are not enough when a sound control exists between them.
A guard name is not enough when indirect callers bypass it or it trusts request data.

## Safe tool use

- Prefer read-only local inspection and already-installed tools. Do not install or
  update a scanner during an audit.
- Record tool name/version when it affects interpretation. Preserve complete stdout,
  stderr, and exit status; distinguish findings from tool failure or partial coverage.
- Do not truncate audit output or suppress errors. Large machine-readable output may
  be saved to an approved local workspace artifact and summarized after complete parsing.
- Use current official advisories and vendor documentation for version-sensitive claims.
- Tool findings remain candidates until verified against resolved versions, actual
  configuration, code paths, build/install lifecycle, and compensating controls.

### Secrets

Never expose a possible secret in terminal output, chat, reports, command history, or
third-party services.

- Prefer a local detector that supports redaction, such as an already-installed
  Gitleaks invoked with redaction enabled. Do not install it automatically.
- If safe redaction is unavailable, search for candidate filenames or matching line
  locations without emitting matched text. Do not display broad context that may contain
  adjacent credentials.
- Retain only repository-relative path, line, detector rule/type, commit or scope when
  relevant, and a redacted stable fingerprint. Do not retain enough prefix/suffix to
  make a credential usable.
- Determine whether the value is a documented placeholder, fixture, public identifier,
  revoked value, client-exposed configuration, or credible credential without contacting
  its provider. Never use a credential to “see whether it works.”
- A confirmed exposure normally requires rotation/revocation and history/artifact review;
  deleting the current line alone is not remediation.

## High-value verification patterns

### Access control, tenancy, and mass assignment

- Trace the object identifier and tenant/organization identity separately.
- Prove the effective principal comes from a trusted identity context, not body/query data.
- Inspect the database predicate or policy that scopes the read/write. A check after a
  sensitive fetch may already disclose existence or content.
- Check alternate routes, background jobs, GraphQL resolvers, exports, caches, search,
  admin/support paths, batch operations, and related write/delete endpoints.
- For updates, identify which fields can bind from external input and whether roles,
  ownership, price, state, or tenant identifiers can be overwritten.

### Injection and output handling

- Follow canonicalized input into the exact interpreter or output context.
- Parameterized queries are strong evidence for values, but identifiers, operators,
  sort clauses, raw fragments, and dynamic collections need separate review.
- Shell escaping depends on invocation mode and platform; prefer argument arrays and
  no shell. Trace second-order values loaded from storage too.
- XSS depends on the render context. Check HTML, attribute, URL, JavaScript, CSS, SVG,
  markdown, rich text, email, PDF, and client-side DOM sinks separately.
- For NoSQL, templates, LDAP, log forging, deserialization, prototype pollution, and
  regex denial of service, verify whether attacker-controlled structure—not merely a
  string—reaches the interpreter.

### Authentication, sessions, tokens, and CSRF

- Verify complete login, recovery, MFA/OTP, logout, revocation, and privilege-change flows.
- For JWT or similar tokens, check verification rather than decode-only use, expected
  issuer/audience, expiry, key source and selection, algorithm/key compatibility, rotation,
  clock tolerance, and installed library behavior. A missing explicit algorithm list alone
  is not proof of exploitation.
- For OAuth/OIDC, check the actual flow, redirect registration, state, nonce, PKCE,
  issuer mix-up defenses, token destination, and account-linking logic.
- Ambient browser credentials generally require CSRF analysis for state changes. SameSite
  helps but is not a universal substitute; verify browser flow, method, origin checks,
  tokens, and CORS/credential behavior.
- Password storage needs a suitable salted password-hashing scheme and a work factor as
  high as practical for the service, reviewed and increased over time. Validate current
  official guidance, repository policy, and measured capacity instead of using a timeless
  bcrypt number.
- When tokens, API keys, reset codes, OTPs, signatures, or other secret authenticators are
  compared in a remotely observable path, verify that the library and comparison primitive
  avoid meaningful timing leakage. Do not label every ordinary equality comparison a
  vulnerability without proving the secret path and observation model.

### SSRF, redirects, files, and parsers

- Normalize before making allow/deny decisions and validate the final effective target.
- For SSRF, inspect schemes, credentials in URLs, encoded/alternate IP forms, DNS changes,
  redirects, proxy behavior, IPv4/IPv6, loopback/private/link-local/metadata ranges, and
  every outbound hop. Prefer explicit destination allowlists and restricted egress.
- For redirects, compare parsed destinations or approved relative paths; substring,
  suffix, or naive `startsWith` checks commonly accept attacker-controlled hosts.
- For uploads, verify size limits, content inspection, safe generated names, storage
  outside executable/public paths, serving headers, image/document reprocessing, archive
  extraction, malware policy where required, and authorization on retrieval.
- For file paths, resolve/canonicalize the final path and prove it remains within the
  intended root; check absolute paths, separators, encoding, symlinks, and archive entries.
- For XML/SVG/document parsers, verify the actual installed parser and options disable
  external entities/network/file resolution and bound CPU, memory, nesting, and expansion.

### Dependencies and supply chain

- Identify the resolved affected version from the lockfile or artifact, not only the
  declared range.
- Confirm the advisory from a primary source and record the fixed version or mitigation.
- Classify runtime, build, install, CI, test, development, or transitive exposure. A
  development dependency can still affect builds, generated artifacts, or developer/CI
  credentials.
- Assess feature/configuration prerequisites and code reachability when evidence permits.
  Use `Not verified` when reachability cannot be established; do not discard the issue.
- Review package provenance, scripts, registry configuration, lockfile changes, CI action
  references, container bases, generated artifacts, and integrity/signing controls when
  relevant.
- Scanners such as OSV-Scanner, ecosystem-native audit commands, CodeQL, Semgrep, and
  secret scanners complement one another. None independently proves business impact.

### Logging, failures, and operational controls

- Trace sensitive values into structured logs, error objects, traces, metrics labels,
  crash reports, analytics, support views, and client responses.
- Verify redaction happens before serialization and across nested objects, headers, URLs,
  bodies, tokens, and third-party errors.
- Check whether suspicious authentication, authorization, privilege, secret, and
  integrity events are detectable, correlated, retained, and routed to an owner.
- Exercise reasoning about partial failure: timeouts, retries, circuit breakers, fallback,
  transaction boundaries, cleanup, duplicate delivery, stale state, and fail-open behavior.

## Active testing boundary

Passive inspection of already-captured local material is different from sending traffic.
Any crawler, requestor, browser interaction, fuzzing, DAST, active scanner, brute force,
payload delivery, account creation, or credential check is active testing.

Before active testing, record authorization and scope in the conversation. Respect host,
path, identity, data, time, rate, concurrency, technique, and environment limits. Start
with the least invasive approved method, protect evidence, and stop on unexpected impact.
Never infer authorization from a hostname such as “staging.”

## Candidate outcomes

- **Verified finding:** the path, failed control, impact, and affected boundary are supported.
- **Likely:** strong evidence exists, but one material runtime or environmental fact is missing.
- **Needs input:** a specific fact or access is needed to decide.
- **Rejected:** a verified control, non-affected version, or unreachable condition defeats it.
- **Hardening:** defense-in-depth improvement without a demonstrated exploitable failure.

Keep rejected candidates out of the findings list, but retain concise reasoning when it
prevents repeated false positives or explains a scanner discrepancy.
