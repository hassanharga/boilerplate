---
name: find-security-gaps
description: Use when auditing source code, configuration, dependencies, or architecture for security vulnerabilities; answering whether a system is safe to ship; tracing cross-user access, secret exposure, injection, or other exploit paths; or producing a security assessment. Do not use for ordinary code review unless security is the requested focus.
---

# Find Security Gaps

Find exploitable security weaknesses, distinguish them from hardening ideas, and
state what the available evidence cannot establish. Prefer a narrow, defensible
answer over a broad checklist with shallow or speculative findings.

## Hard boundaries

- Treat the audit as read-only. Do not edit code, dependencies, configuration,
  tickets, pull requests, or external systems until the user approves that action.
- Source and local configuration review do not authorize live testing. Do not send
  payloads, crawl, scan, brute-force, create accounts, validate credentials, or
  interact with staging or production without explicit authorization and bounds.
- Never print, copy, transmit, use, or remotely validate a discovered credential.
  Preserve only its location, detector rule, and a redacted fingerprint. Use
  `scripts/secret-scan.py`, which enforces this mechanically — prose cannot.
- **Any request that reaches a target is active testing**, including a crawler,
  browser interaction, fuzzer, scanner, brute force, payload, account creation, or
  credential check. It requires mode 3 authorization below. Never infer authorization
  from a hostname such as "staging".
- Treat scanner output and suspicious patterns as candidates, not findings.
- Do not declare a system safe, clean, compliant, or launch-ready beyond the
  components and environments actually verified.
- Do not install tools, update dependencies, enable services, or run remediation
  modes merely to complete an audit.

## Choose the assessment mode

Use the narrowest mode that answers the request.

1. **Focused question, module, or diff** — inspect only the relevant trust boundary
   and security domains. Answer in chat unless the user asks for an artifact.
2. **Repository or release audit** — map the architecture, select every applicable
   domain from [coverage.md](references/coverage.md), and record uncovered areas.
3. **Active testing** — before any request reaches a target, obtain confirmation of
   ownership or authorization, exact targets, allowed techniques, accounts/roles,
   time window, rate/concurrency limits, prohibited actions, stop conditions, and
   an emergency contact. If these are missing, stop and ask for them.

If scope is ambiguous but a safe local review is possible, begin with that review
and label the limitation. Do not silently expand a focused request into a full audit.

## Workflow

### 1. Establish context

Read applicable agent/repository instructions. Identify:

- assets, entry points, trust boundaries, privileged operations, and sensitive data;
- authentication, session/token, authorization, tenancy, and validation models;
- public, internal, administrative, asynchronous, and machine-to-machine surfaces;
- data stores, outbound calls, file/parser behavior, queues, caches, and third parties;
- deployment, CI/CD, infrastructure, secret, dependency, and observability controls;
- what code, runtime configuration, infrastructure, and production evidence are absent.

For a diff, trace enough unchanged code to understand the changed path. For a broad
audit, build a compact coverage matrix before hunting.

### 2. Select applicable coverage

Use [coverage.md](references/coverage.md). Select domains based on reachable assets
and trust boundaries, not a fixed category count. Mark excluded domains as `Not
applicable` with a reason; mark unavailable evidence as `Not verified` or `Needs
input`, never as clean.

Use the current OWASP ASVS as the primary application-verification baseline and the
current OWASP Top 10 as a risk taxonomy, not as a completeness checklist. Verify
time-sensitive protocol, framework, library, cryptographic, and advisory claims in
current official documentation.

### 3. Hunt for candidates

Search from both directions:

- entry points and attacker-controlled sources toward privileged actions or sinks;
- sensitive sinks, assets, and configuration backward toward their callers and guards.

Include tests, deployment configuration, IaC, CI/CD, lockfiles, generated exposure
points, and documentation when they affect real behavior. Exclude dependency caches
and generated noise unless the artifact itself ships or controls the build.

Use tools already installed, in this order, and never install one to complete an audit:

| Question | Default | Fallback |
| --- | --- | --- |
| Vulnerable dependencies | The project's own audit command (`pnpm audit`, `npm audit`, `pip-audit`) | `osv-scanner` if present, otherwise resolve advisories manually from the lockfile |
| Exposed credentials | `scripts/secret-scan.py`, which prefers an installed Gitleaks with redaction forced on | Its built-in detectors, which never emit a matched value |
| Code patterns | `semgrep` or `codeql` if the project already configures them | Targeted `rg` searches from the trust boundary inward |

Every tool result is a candidate. None of them establishes business impact.

`scripts/secret-scan.py` is bundled with this skill: the path is relative to the
directory containing this `SKILL.md`, not the repository under audit. Resolve that
directory once and invoke it by absolute path.

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final report, and every external write
stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means one pass per independent security domain, each carrying the same trust
model, secret rules, and read-only boundary. Subagents return candidates and evidence;
cross-domain tracing, disproof attempts, deduplication, and final classification stay
with the main agent. Mark a domain unverified only when the required evidence is itself
unavailable, never because delegation failed. A focused assessment usually needs no
delegation.

### 4. Verify every candidate

Apply [verification.md](references/verification.md). A reportable vulnerability needs:

1. an attacker-controlled source or plausible precondition;
2. a security-relevant operation, asset, or sink;
3. the complete path between them;
4. the actual guards, normalization, framework behavior, and deployment controls;
5. a concrete impact and affected boundary;
6. an attempt to disprove exploitability.

Classify unresolved evidence honestly. Do not turn missing proof into a finding merely
because the code looks unusual. Conversely, do not dismiss build-time, install-time,
or operational exposure only because a package is not reached at runtime.

### 5. Report proportionately

Follow [reporting.md](references/reporting.md). For focused questions, lead with the
answer and the decisive evidence. For broad audits, include scope, verdict, findings,
coverage, limitations, and prioritized next actions.

Give remediation outcomes and acceptance checks. Include an exact patch only when the
user asks for one or when it is safely bounded and verified against the repository.
Do not create a report file unless requested or clearly useful, and state its path
before writing it.

### 6. Fix only after approval

After the user selects findings to fix, switch from audit to implementation. Preserve
the repository's architecture and test policy. Add behavior-level regression tests,
including security-boundary cases. Enforce 100% coverage only where the repository,
service, or acceptance criteria require it; never invent a universal target. Run the
repository's required verification chain and report every pass, failure, and unverified
check accurately.

## Reference routing

- [coverage.md](references/coverage.md) — choose applicable security domains.
- [verification.md](references/verification.md) — prove or reject candidates safely.
- [reporting.md](references/reporting.md) — severity, confidence, statuses, and output.
