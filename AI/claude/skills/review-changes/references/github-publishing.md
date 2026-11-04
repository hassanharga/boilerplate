# GitHub Publishing

Read this reference only after the user asks to publish review feedback.
Publishing creates notifications and shared state; review authorization alone
does not authorize it.

## Authorization contract

Before the first write, require both:

1. The exact findings to publish: IDs, “all,” or another unambiguous selection.
2. Review action: normal comment or request-changes.

If the user already supplied either choice, do not ask for it again. Never infer
approval. Never submit an approval unless the user explicitly says to approve.
Do not add labels, assignments, commits, or fixes as part of publication.

Outside-diff findings stay in the chat report by default. Publishing one in a
review body or PR conversation comment requires separate explicit authorization
because it is not a changed-line comment.

## Fresh pre-write snapshot

Immediately before writing, re-fetch through an available connector, API, or
CLI:

- current head SHA and base SHA;
- PR open/closed state, merged status, draft status, and conversation lock status;
- current changed-file list and target diff lines;
- current checks;
- reviews, line comments, and review-thread resolution;
- existing comments matching each selected finding.

Revalidate every selected finding against that snapshot. Stop before writing if
the head changed and the finding has not been re-reviewed, the anchor is no
longer in the diff, the issue was fixed, equivalent feedback already exists
(except the explicitly authorized placement repair below), or new evidence
changes its classification. A failing check is not automatically a
stop, but it is when it invalidates the intended review message or requires the
user to reconsider the action.

Apply the PR-state gate before any write. If state cannot be established, stop
publication and report the missing evidence. Do not submit pre-merge approval or
request-changes on a closed or merged PR. Posting comments after closure or merge
requires explicit user intent for that state; an earlier pre-merge publication
request does not supply it. A draft does not by itself block explicitly requested
feedback, and the skill must not mark it ready for review. If the conversation is
locked, establish that the requested action is permitted for the publishing actor;
do not unlock it or bypass restrictions.

For packet validity and journal recovery, follow the
[evidence lifecycle](evidence-lifecycle.md). Dry runs print exact plan content and
make no local journal or remote writes. `--yes` maintains the recovery journal;
retain it with the plan. The script does not replace the fresh pre-write snapshot
or semantic deduplication against other reviewers.

## Write order

`scripts/publish.py` implements this order, the head and state rechecks, the
deduplication of your own earlier posts, and the post-write verification. Prepare the
plan (repo, PR, reviewed head, event, opener, comments with path, line, side, body),
validate the report with `python3 check-report.py <report> --publish --snapshot <packet>/snapshot --base-snapshot <packet>/base-snapshot --diff <packet>/diff.patch`, dry-run the script, then run it
with `--yes`. The rules below remain the contract; follow them by hand only when the
script cannot run.

The first GitHub write is the review action with a short, genuine opener:

1. Submit normal comment or request-changes with the opener and explicitly set
   `commit_id` to the reviewed snapshot's head SHA. Never let the API default to
   the newest commit. Verify the returned review's commit SHA and action; if they
   differ or cannot be verified, stop further writes and report the uncertainty.
2. Re-fetch the head SHA and PR state. If the head changed, stop and report the
   opener's actual reviewed commit; re-review before any inline comment. Apply the
   PR-state gate again, and recheck head and state before each remaining comment.
3. Post only the selected findings as individual changed-line comments.

Do not publish a large summary comment unless the user explicitly requested it.
Keep the opener to one natural sentence and do not repeat the findings in it. Make it
specific to the reviewed area when possible. Avoid generic enthusiasm, canned praise,
emojis, and internal review labels.

Each inline comment is a natural, self-contained explanation using the published
line comment shape in [output.md](output.md) — the finding's own `Type:`, `Issue:`,
`Impact:`, and `Fix:` fields, unchanged, without the location line the anchor
already provides.

Remove every placeholder before publication. A proven defect should be stated
directly rather than softened into a rhetorical "Could we...?" question; a
genuine uncertainty should name the evidence that would answer it in `Fix:`.

Use the reviewed snapshot's head SHA as `commit_id`. Derive the repository-relative
`path`, 1-indexed blob `line`, and side from that snapshot's actual diff: `RIGHT`
for added/context lines and `LEFT` for deleted lines. Resolve RIGHT content from
the head and LEFT content from the diff's old-side revision and path, accounting
for renames and deleted files. The old side may be a merge base rather than the
current base tip. For a rename, distinguish the old source path used for LEFT blob validation
from the host's diff-file path. Resolve the publication path from fresh host
metadata; local validation alone does not prove remote acceptance. The
[GitHub comment API](https://docs.github.com/en/rest/pulls/comments#create-a-review-comment-for-a-pull-request)
defines the path, side, and line/range fields. If the exact rename anchor cannot
be established, withhold that finding and explain the gap before any write.
For multi-line findings use the host/API range fields. Do not
use obsolete diff positions when line/side fields are available.

If the real problem is outside the diff but the changed line creates the failing
call path, anchor to the smallest relevant changed line and name the outside
location in the prose. If no honest changed-line anchor exists, keep it out of
the inline set.

## Placement: one independent anchored comment per finding

Each published finding is its own independent, line-anchored comment on the code
it concerns. One finding, one thread, one anchor. Do not batch several findings
into a single comment, and do not stack them under an anchor that belongs to a
different topic.

A comment's anchor is part of its evidence: it puts the reader on the lines the
finding is about and renders the surrounding diff. A reply inherits its parent's
file and line, so a finding posted as a reply loses that context and the author
must reconstruct the location from prose.

### When the user asks to post into an already-open thread

“Post it in my thread,” “reply on that thread,” or a named/linked existing
comment is a placement request, and it is satisfied by anchoring, not by
replying, unless the finding is genuinely about that thread's subject. Before
any write:

1. Take the fresh pre-write snapshot above.
2. Resolve an exact anchor for each selected finding using the side-aware diff
   procedure above. Confirm that the line exists on the relevant side of the
   target diff; deleted content need not exist at HEAD.
3. Compare each anchor with the open thread's own path, side, and line, including
   whether its position is outdated.

Then place each finding by where it actually belongs:

- **Anchor differs from the thread's subject:** post it as an independent
  line-anchored comment. Say plainly in the report that you anchored instead of
  replying, and link the new comment so the user can follow it from the thread.
- **The finding answers, refines, or confirms that thread:** reply in the thread.
  This is the case the request is literally asking for, and the parent's anchor
  is already correct.
- **The user insists on the thread after being told:** reply there, and open the
  comment with the `file:line` the finding concerns so it stands alone.

### Correcting placement after the fact

Placement repair is a separate operation. Permission to publish findings does not
authorize deleting existing comments. Identify the exact superseded comment IDs
and their intended replacements. For an explicitly authorized repair, those named
originals are replacement sources, not a reason to reject the repair as duplicate.
Still check that each correctly placed replacement has not already been posted;
all other equivalent feedback remains subject to the normal deduplication gate.
Identify which original comment IDs, if any, the user wants removed,
and obtain explicit deletion authorization unless already supplied. Obtain any
missing authorization for replacement comments through the publication contract.
Post authorized replacements first and verify they landed. Before deleting any
authorized superseded comment, preserve its body locally and tell the user where
it is kept; delete only the identified comments authored by the publishing agent.
Never delete another author's comment. Without deletion authorization, leave the
originals in place and report the remaining repair work.

## Ambiguous failures and retries

A timeout or connection error after a write request is ambiguous: GitHub may
have accepted it. Before retrying any write, re-fetch reviews/comments and look
for the expected author, body, path, line, commit SHA, and creation time. Retry
only when absence is confirmed. Never blindly resend the opener or a line
comment.

Respect secondary rate limits by posting sequentially. If one selected comment
fails, classify the failure, check whether it actually landed, and stop when a
retry could duplicate feedback or when the head changed. Report partial
publication exactly.

## Post-write verification

Re-fetch the resulting review and line comments. Verify each intended artifact
by identity and content, not only by total count:

- expected review action and opener;
- expected author;
- exact selected finding body or stable identifying text;
- path, line/range, side, and commit SHA;
- no unselected finding was posted;
- expected number of new matching comments.

Return the verified URLs or IDs when available. If verification is unavailable,
say publication is unverified rather than claiming success.
