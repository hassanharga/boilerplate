# Security coverage selection

Use this reference to select coverage, not as a demand to perform every check on every
request. Start from assets and trust boundaries. For each applicable domain, identify
the entry points, security controls, sensitive operations, and evidence available.

For broad application assessments, reconcile the chosen domains with the current
[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/).
Use stable, versioned ASVS requirement identifiers when requirements must be tracked.
Use the current [OWASP Top 10](https://owasp.org/Top10/) to communicate common risk
classes, not to claim complete verification.

## Core domains

| Domain                                          | Apply when                                                                                                      | Verify                                                                                                                                                                                                                                                                                                      |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Architecture, threat model, and business logic  | Always; depth follows scope                                                                                     | Assets, actors, trust boundaries, privileged workflows, abuse cases, invariants, insecure defaults, tenant or money movement, and assumptions enforced only by UI or convention.                                                                                                                            |
| Authentication and identity lifecycle           | Humans or machines authenticate                                                                                 | Enrollment, login, recovery, MFA/OTP/magic links, enumeration, throttling, credential change, account linking, service identities, disabled users, and development bypasses.                                                                                                                                |
| Sessions, tokens, OAuth/OIDC                    | Cookies, bearer tokens, JWT/PASETO, API keys, or delegated identity are used                                    | Issuance, binding, rotation, revocation, expiry, replay, fixation, logout, secure transport/storage, issuer/audience, key selection, callback state/nonce/PKCE, and library defaults.                                                                                                                       |
| Access control and multi-tenancy                | Resources or actions differ by user, role, organization, or service                                             | Authentication versus authorization, ownership/tenant predicates, default deny, admin and support paths, indirect callers, read/write/delete parity, field-level access, IDOR, mass assignment, and confused-deputy paths.                                                                                  |
| Input validation and injection                  | Untrusted input reaches interpreters, queries, templates, selectors, headers, logs, or generated content        | Schema validation at the boundary, canonicalization, parameterization/contextual encoding, SQL/NoSQL/command/template/header/LDAP injection, XSS, unsafe deserialization, prototype pollution, regex denial of service, and second-order flows.                                                             |
| API and route surface                           | HTTP/RPC/GraphQL/webhook/admin/debug endpoints exist                                                            | Complete route/resolver/handler inventory, consistent guards and validation, schema/introspection exposure, method/content-type handling, batch/alias/depth limits, webhook authenticity/replay, debug endpoints, and deprecated versions.                                                                  |
| Cryptography and key management                 | Secrets, credentials, signatures, encryption, hashes, or random values protect assets                           | Approved purpose-fit primitives, authenticated encryption, randomness, nonce/IV use, key generation/storage/rotation/separation, password hashing policy, signature verification, certificate validation, downgrade behavior, and migration strategy.                                                       |
| Secrets and client-side exposure                | Credentials or sensitive configuration exist                                                                    | Source/history/config exposure, client bundle and source-map exposure, examples versus live values, environment boundaries, least privilege, rotation/revocation, logs/artifacts, CI variables, image layers, and secret-manager integration. Never reproduce a value.                                      |
| Data protection and privacy                     | Personal, financial, location, health, credential, or business-sensitive data is processed                      | Classification, minimization, purpose, consent where relevant, retention/deletion, access/export, encryption, backups, caches, analytics, logs, error responses, support tooling, data residency, and third-party transfer.                                                                                 |
| Browser and transport controls                  | Browsers, cookies, cross-origin requests, or public network traffic are involved                                | TLS and certificate validation, proxy trust, HSTS, cookie flags and scope, CSRF for ambient credentials, CORS origin/credential behavior, CSP and contextual output encoding, clickjacking, cache controls, redirects, and security headers based on actual threat.                                         |
| Server-side requests, files, and parsers        | User input influences URLs, redirects, uploads, paths, archives, images, XML, templates, or document conversion | SSRF and DNS/redirect rebinding, destination allowlists, private/link-local/metadata access, protocol restrictions, upload size/content/storage/serving, traversal/symlinks/archive extraction, parser external entities, resource exhaustion, and open redirects.                                          |
| Resource abuse and state integrity              | Costly endpoints, retries, queues, payments, inventory, or concurrent state changes exist                       | Rate and concurrency limits, per-identity and distributed enforcement, brute force, enumeration, quotas, pagination, payload size, timeouts, backpressure, replay, idempotency, race conditions, duplicate delivery, and atomic invariants.                                                                 |
| Dependencies, supply chain, and build integrity | Third-party packages, images, actions, generators, or build services are used                                   | Resolved versions and provenance, lockfile integrity, compromised or abandoned packages, install/build scripts, transitive/runtime/dev exposure, advisories, artifact signing/verification, registries, SBOM where required, update process, CI actions pinned appropriately, and generated artifacts.      |
| Deployment, cloud, IaC, IAM, and CI/CD          | Deployment or infrastructure material is in scope                                                               | Public exposure, network boundaries, IAM least privilege, workload identity, secret access, storage/database policies, container/user/capabilities, metadata service, environment separation, branch/deployment protection, untrusted CI input, artifact provenance, and drift from reviewed configuration. |
| Logging, alerting, and exceptional conditions   | The system handles failures or produces security telemetry                                                      | Sensitive-data redaction, tamper resistance, actor/request correlation, auth and privilege-change events, alert ownership, useful thresholds, fail-open/fail-closed behavior, partial failure, retry storms, stack traces, crash loops, cleanup, and recovery paths.                                        |

## Conditional platform domains

Apply these only when the platform exists in scope:

- **Mobile and desktop:** local secret storage, deep links/custom schemes, IPC, update
  signing, WebViews, certificate policy, exported components, backups, screenshots,
  rooted/jailbroken assumptions, and native permission boundaries.
- **AI/LLM and agentic systems:** prompt/data trust boundaries, tool authorization,
  indirect prompt injection, retrieval tenant isolation, secret/context disclosure,
  output handling, model/plugin supply chain, human approval for consequential actions,
  and resource/cost abuse.
- **Realtime, messaging, and event systems:** channel/topic authorization, publisher and
  consumer identity, message authenticity, replay/ordering, poison messages, tenant
  partitioning, subscription leakage, and delivery semantics.
- **Hardware, embedded, and operational technology:** secure boot/update, physical
  interfaces, device identity, key extraction, unsafe fail states, and recovery.

## Coverage rules

- Merge overlapping domains for a focused question. An IDOR question usually needs one
  access-control trace, not a broad audit.
- Split a domain when different trust boundaries need independent conclusions—for
  example, customer API versus admin API or runtime dependency versus build dependency.
- A search with no match is evidence of what was searched, not proof that the control
  is sound.
- Tests prove exercised behavior, not production configuration. Configuration proves
  declared intent, not necessarily deployed state.
- When infrastructure, secrets, identity-provider settings, or runtime policy are not
  visible, use `Not verified` or `Needs input`.

## Time-sensitive claims

Check current primary documentation before relying on:

- framework or library defaults and patched versions;
- token algorithm/key behavior and OAuth/OIDC requirements;
- cryptographic algorithms, password work factors, and protocol versions;
- browser behavior, cookie defaults, CORS/CSP details, and parser configuration;
- CVEs, affected version ranges, fixes, exploit prerequisites, and scanner support.

Record the relevant version and source. Do not freeze a numeric threshold into a
finding when the correct value depends on current guidance, threat model, or measured
service capacity.
