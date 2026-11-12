# Evidence Lifecycle

Read during collection and before reporting or publishing. One review assesses
one explicit comparison. Its evidence moves through the following stages; a
later stage does not grant permission for the next action.

| Stage | Required evidence | What invalidates it |
| --- | --- | --- |
| Target selected | Repository, intent source, exact base/head or index/local scope; merge parent when applicable | A different comparison or changed acceptance criteria |
| Packet collected | Fresh packet directory, diff, changed paths, old/new snapshots, metadata, feedback, manifest | Collection failure, mutable source changing during capture, manifest mismatch |
| Findings assessed | Caller/contract trace for changed behavior, prior-feedback reconciliation, explicit coverage gaps | Changed evidence or a refuted factual premise |
| Report validated | Findings bound to the packet, observed checks, challenge outcome or skip, side-aware anchors | Changed report, packet, checks scope, or material finding |
| Publication prepared | Exact selected findings and action authorized; fresh PR state, diff, checks, feedback; dry-run plan inspected | Head/base or relevant evidence changes; authorization no longer matches the content |
| Publication observed | Review action and each selected comment read back with exact identity | Missing or mismatched destination state; unresolved write outcome |

## Collect and preserve

Use a new packet path for each collection. `collect.sh` refuses an existing path,
so it cannot mix prior feedback/checks with another target or delete a retained
snapshot. A failed collection leaves an incomplete packet for diagnosis; do not
use it as complete evidence. Select a new path for the next attempt.

The collector exports Git blobs directly, preserving executable bits and symlinks
without archive exclusions, substitution, checkout filters, or hooks. It captures
`snapshot/` and `base-snapshot/`. Submodule contents are not exported: each
`*-gaps.json` identifies the excluded path and revision. Review those separately
with explicit revision evidence or disclose the gap. A snapshot with gaps is not
proof of complete repository coverage. Ignored/untracked dependencies are absent;
run checks only where existing dependencies can be used safely for that revision.

Index/local fingerprints surround collection, including tracked contents and
untracked paths. A changed fingerprint fails collection; the stable value is
retained as `meta.json.source_fingerprint`. Recompute it from the source repository
with `python3 <skill-dir>/scripts/snapshot.py fingerprint <index|local>` when
checking source freshness. `manifest.json` binds the
captured files, modes, symlink targets, diff, metadata, checks, and feedback.
Before reporting, run:

```bash
python3 <skill-dir>/scripts/snapshot.py verify <packet>
```

Keep the captured evidence unchanged. Run checks in a separate disposable copy,
then record their revision, command, and result in the report. Recheck mutable
source fingerprints before reporting; when they changed, recollect or explicitly
limit the report to the previously captured snapshot. A manifest proves packet
integrity, not that a mutable working tree or GitHub head is still current.

## Coverage is explicit

Map each changed hunk to a traced flow, a justified skim, or an unreviewed gap.
For monorepos, rerun `profile.sh <snapshot> --files <packet>/files.txt` after
collection. Inspect `packages`, `instruction_scopes`, and discovery gaps; commands
carry a package directory and must run there. Source-side ancestor instructions
already loaded remain applicable to the isolated snapshot. Deleted paths can
require old-side package rules, so inspect `base-snapshot/` when routing differs.

## Publish and resume

Publication is an ordered sequence of remote writes. It cannot be atomic across
GitHub requests. Keep one publisher per plan, and retain the exact JSON plan and
its default `<plan-stem>.journal.json` (or explicit `--journal` path).

The journal identifies the plan/actor and each exact operation. It is saved before
each write, and records attempts, uncertain outcomes, and verified destination
identities. Full bodies, review action, revision, path, side, and range determine
matches. It never substitutes a local success record for a fresh destination read.

After an ambiguous response, the publisher reads the destination once. A matching
artifact allows progress; a missing artifact or unavailable read stops dependent
writes. Resume with the same plan and journal only after the required fresh-state
checks. A new attempt first reads the destination, and the journal permits at most
two attempts per operation. Permanent failures require inspection. A changed plan
requires a distinct journal and renewed authorization when the content changed.

A lock prevents concurrent runs sharing a journal. After an interrupted process,
inspect the recorded attempt and establish that no publisher is still active
before explicitly clearing a stale lock. Never remove locks or journals as an
automatic retry. No helper edits or deletes earlier remote feedback.
