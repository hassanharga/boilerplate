# Security assessment reporting

Match the output to the request. A focused authorization question may need three
paragraphs. A release assessment may need a durable report. More pages do not make the
conclusion more reliable.

## Output selection

- Default to chat for focused questions, diffs, and small assessments.
- Create a local report only when the user requests one or a broad audit needs a durable
  artifact. State the proposed path before writing outside an already-approved workflow.
- Do not post findings, create tickets, send messages, or modify external systems without
  explicit approval.
- Keep secrets, personal data, exploit-sensitive details, and internal topology minimized
  and redacted in every output.

## Lead with the result

State one of these conclusions in plain language:

- a verified vulnerability exists and what boundary it breaks;
- no vulnerability was found in the verified scope, with important limitations;
- the available evidence is insufficient, naming exactly what is missing;
- the observed issue is hardening rather than a demonstrated vulnerability.

Do not say “safe,” “secure,” “clean,” “compliant,” or “ready to ship” without defining
scope and evidence. Absence of a finding is not proof of absence.

## Coverage statuses

Use only statuses supported by evidence:

- **Finding** — at least one verified or clearly labeled likely weakness.
- **Checked** — named entry points and controls were inspected with no reportable weakness.
- **Not applicable** — the domain does not exist in the assessed scope; give the reason.
- **Not verified** — the domain may matter, but its code/configuration/environment was absent.
- **Needs input** — a specific user decision, access, or fact is required.

Never turn `Not verified` into `Checked`. For a broad audit, list which assets, paths,
versions, configurations, tests, and environments each status covers.

## Finding contract

Each finding should contain:

1. **Concrete title:** use one short line that names the failed security boundary or
   impact, not an imperative remediation command. Keep severity and confidence out of
   the title so they remain easy to scan as separate metadata.
2. **Severity and confidence:** keep them separate.
3. **Affected asset and location:** repository-relative file/line or configuration surface.
4. **Preconditions and attacker capability:** authentication, role, network, timing, or data.
5. **Evidence path:** source → transformations → failed/missing control → sink/operation.
6. **Impact and scope:** data, identity, tenant, integrity, availability, or supply chain.
7. **Disproof performed:** relevant guards, defaults, versions, tests, or deployment controls checked.
8. **Remediation outcome:** the security property the fix must establish.
9. **Acceptance check:** how to prove the boundary now holds, including negative cases.
10. **Remaining uncertainty:** runtime or operational evidence still needed.

This is an evidence contract, not a ten-heading template. For a focused finding, keep
severity and confidence visible, then combine the remaining elements into a few natural,
direct paragraphs. Lead with the vulnerability and affected boundary. Prefer concrete
actors, data, guards, and outcomes over stock phrases such as "security posture" or
"robust protection." Do not repeat the same source-to-sink path in the title, summary,
evidence, and impact sections. Remove empty sections and placeholders.

Include a proof-of-concept only when safe, necessary, within authorization, and redacted.
Do not include working credentials or unnecessarily weaponized payloads. Exact code diffs
are optional and should be produced only when requested or safely bounded by repository
context and verification.

## Severity

Use project policy when one exists. Otherwise judge:

- impact on confidentiality, integrity, availability, safety, privacy, or supply chain;
- exploit prerequisites, complexity, required privileges, and user interaction;
- exposure, affected population/tenants, blast radius, persistence, and detectability;
- reliability and likely abuse, not merely theoretical possibility;
- compensating controls and recovery/rotation cost.

Suggested qualitative bands:

- **Critical:** credible catastrophic or broad compromise with practical exploitation,
  such as systemic authentication bypass, remote code execution on a sensitive service,
  or broadly usable production credentials.
- **High:** serious cross-boundary access, privilege escalation, sensitive-data exposure,
  integrity compromise, or durable service impact with realistic prerequisites.
- **Medium:** meaningful impact with material prerequisites, limited blast radius, or
  strong compensating controls.
- **Low:** limited security impact or difficult exploitation; still a demonstrated failed
  boundary, not merely style.
- **Hardening/Informational:** defense-in-depth, hygiene, or visibility improvement without
  a demonstrated exploitable failure.

CVSS v4 may be included when consumers require a portable vector. It supplements rather
than replaces business context, release priority, or confidence.

## Confidence

- **High:** complete code/configuration path and relevant versions/controls were verified.
- **Medium:** the path is strong, but one non-decisive runtime fact or assumption remains.
- **Low:** substantial evidence is missing; normally report as `Needs input` or a candidate,
  not as a confirmed finding.

Lower confidence does not automatically lower impact. Explain the missing evidence instead.

## Broad assessment shape

When a durable broad report is justified, use:

1. Scope, mode, date, versions/commit, and evidence sources.
2. Executive verdict with the most important limitation.
3. Findings ordered by severity, then confidence and practical priority.
4. Coverage matrix using the approved statuses.
5. Detailed findings using the finding contract.
6. Rejected scanner candidates worth documenting.
7. Not-verified areas and exact inputs needed.
8. Prioritized actions before release and longer-term hardening.

For a focused assessment, omit sections that add no value.

## After fixes are approved

Convert each selected finding into behavior-level acceptance checks. Test the vulnerable
case, allowed case, denied cross-boundary case, and relevant alternate entry points. Follow
the repository's required coverage target—100% when explicitly required, otherwise the
local policy—and run its typecheck, lint, build, and affected tests. Report failures and
baseline limitations without weakening or skipping checks to manufacture a green result.
