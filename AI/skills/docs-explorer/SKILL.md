---
name: docs-explorer
description: Use when answering questions that require current or version-specific documentation for a library, framework, protocol, standard, API, or developer tool, including API behavior, configuration, migration guidance, deprecations, and supplied documentation URLs.
---

# Documentation Explorer

Answer from documentation that matches the version the user is actually running. The
common failure is answering correctly for the latest release while the repository is
pinned two majors back.

## Resolve the version first

1. A version the user explicitly named.
2. The version pinned or resolved by the repository: manifests, lockfiles, runtime
   metadata, or generated dependency reports.
3. The latest version only when the user asks about latest or upgrade behavior.
4. Otherwise verify the current stable version and state the retrieval date.

If the repository version cannot be established, say what was checked and label the
assumption. Never apply current documentation to an older repository without saying so.

## Retrieve

Use Context7 as the default documentation index; it resolves a library and returns
focused excerpts faster than a web search. Fall back to whatever documentation,
web, repository, or file-reading capability the current runtime provides.

When Context7 has no entry for the library, or its entry does not cover the pinned
version, discover the official source directly:

1. Resolve the project's own metadata — `package.json` `homepage`/`repository`,
   `pyproject.toml`, `go.mod`, or the equivalent — to find the canonical docs site
   or source repository.
2. Read the documentation at the **matching tag** in that repository: `docs/`,
   `README`, `CHANGELOG`, and release notes. Not the default branch.
3. Read public types, source, and tests at that tag when prose documentation is
   absent or ambiguous.
4. Search the web last, and label anything community-derived.

When the user supplies a page, specification, paper, dataset, or PDF, inspect that
source directly and follow links only as needed.

## Prefer stronger evidence

1. Official versioned documentation, API reference, standard, or RFC.
2. Official release notes, changelog, deprecation notice, or migration guide.
3. Official source at the matching tag, including public types and tests.
4. A documentation index or retrieval service, used for discovery and extraction.
5. Maintainer discussions and reputable community sources when primary sources do not
   cover the issue, or the user asks for field experience and workarounds.

Indexes and aggregators are retrieval aids, not authorities; follow their citations to
the original. For security-sensitive, version-sensitive, or high-impact claims, confirm
against a direct primary source. When sources conflict, prefer the one closest to the
relevant version and implementation, report the conflict, and avoid false certainty.

## Delegate independent lookups

When the runtime supports subagents and the work splits into independent read-only
passes, delegate. Give each subagent a disjoint scope and the same evidence standard,
and require it to return findings with sources — never decisions, conclusions, or
writes. Reconciliation, conflict resolution, the final answer, and every external write
stay in the main agent. If subagents are unavailable or a pass fails, run the same
passes sequentially without reducing coverage.

Here that means one pass per independent source class or per library when a question
spans several. Give each the exact question, the applicable version, the source class,
and the citation requirement. Keep dependent lookups and small questions in the main
agent.

## Answer

Lead with the answer. Then include only what helps the user apply or verify it: the
applicable version, direct citations, a minimal example when it clarifies, and any
deprecation, compatibility, security, or migration caveat.

Separate documented fact from source-backed inference and from repository-specific
conclusion. Do not expose internal retrieval tool names or narrate the search unless
asked.

Deprecated APIs may still describe the repository correctly. Explain their behavior for
the installed version, flag the status, and give the supported migration path rather
than suppressing them.

## Boundaries

- Do not invent API behavior, defaults, version support, or citations.
- A search snippet is not sufficient evidence for a precise claim.
- Do not mutate repositories, dependencies, accounts, or external systems during a
  documentation lookup.
- If authoritative documentation is unavailable, say so and give the best labeled
  evidence instead of presenting it as confirmed.
