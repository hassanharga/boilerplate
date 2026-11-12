#!/usr/bin/env bash
# Collect the review evidence for one target into a packet directory.
#
# Usage:
#   collect.sh <out-dir> pr <number> [--repo owner/name]
#   collect.sh <out-dir> branch <head-ref> [base-ref]
#   collect.sh <out-dir> commit <sha> [--parent N]
#   collect.sh <out-dir> range <previous-sha> [head-ref]   # re-review: previous -> head
#   collect.sh <out-dir> staged
#   collect.sh <out-dir> local            # staged + unstaged + untracked
#
# Run from inside the repository under review. Writes:
#   meta.json            target, base, merge base, head, repo, ticket keys
#   diff.patch           the complete reviewed diff (from the merge base for PRs/branches)
#   files.txt            changed files with status (name-status)
#   snapshot/            an isolated copy of the reviewed version, outside the repo
#   checks.json          PR checks by name and head SHA (PR only)
#   existing-feedback.json  every review and review thread, paginated (PR); empty
#                        lists for other targets, so later steps can rely on the file
#
# Read-only toward the reviewed repository: no checkout, no index or working-tree
# change. PR fetches add Git objects and update FETCH_HEAD; no branch is switched.
set -euo pipefail

usage() { sed -n '2,/^set -euo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'; }
case "${1:-}" in -h|--help|"") usage; [[ -n "${1:-}" ]]; exit $? ;; esac
[[ $# -ge 2 ]] || { usage >&2; exit 2; }
out="${1:?out-dir required}"; kind="${2:?target kind required}"; shift 2
command -v git >/dev/null || { echo "git is required" >&2; exit 2; }
command -v jq >/dev/null || { echo "jq is required" >&2; exit 2; }
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "run inside a git repository" >&2; exit 2; }
root="$(git rev-parse --show-toplevel)"
helper="$(cd "$(dirname "$0")" && pwd -P)/snapshot.py"
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 2; }

out="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$out")"
case "$out/" in "$root"/*) echo "out-dir must be outside the repository" >&2; exit 2 ;; esac
[[ ! -e "$out" ]] || { echo "out-dir already exists; use a fresh packet directory" >&2; exit 2; }
mkdir -p "$out"
cd "$root"
before=""
case "$kind" in staged) before="$(python3 "$helper" fingerprint index)" ;;
  local) before="$(python3 "$helper" fingerprint local)" ;; esac

ticket_keys() { { grep -oE '\b[A-Z][A-Z0-9]+-[0-9]+\b' || true; } | sort -u | jq -R . | jq -s . ; }
export_commit() { python3 "$helper" export "$1" "$out/snapshot"; }
diff_git() { git -c core.quotePath=false diff --no-ext-diff --no-textconv --binary "$@"; }

base=""; head=""; merge_base=""; repo=""; keys='[]'
case "$kind" in
  pr)
    number="${1:?PR number required}"; shift
    repo_args=(); [[ "${1:-}" == --repo ]] && { repo_args=(--repo "$2"); shift 2; }
    command -v gh >/dev/null || { echo "gh is required for PR targets" >&2; exit 2; }
    gh pr view "$number" "${repo_args[@]}" --json \
      number,title,body,url,state,isDraft,author,baseRefName,headRefName,baseRefOid,headRefOid,files,statusCheckRollup \
      >"$out/pr.json"
    repo="$(jq -r '.url | capture("github.com/(?<r>[^/]+/[^/]+)/pull").r' "$out/pr.json")"
    head="$(jq -r .headRefOid "$out/pr.json")"; base="$(jq -r .baseRefOid "$out/pr.json")"
    git fetch -q origin "pull/$number/head" "$(jq -r .baseRefName "$out/pr.json")"
    git cat-file -e "$head^{commit}" || { echo "PR head $head not available after fetch" >&2; exit 3; }
    git cat-file -e "$base^{commit}" || { echo "pinned PR base unavailable; recollect instead of substituting FETCH_HEAD" >&2; exit 3; }
    merge_base="$(git merge-base "$base" "$head")"
    diff_git "$merge_base" "$head" >"$out/diff.patch"
    diff_git --name-status "$merge_base" "$head" >"$out/files.txt"
    export_commit "$head"
    jq '[.statusCheckRollup[]? | {name: (.name // .context), status, conclusion: (.conclusion // .state), url: (.detailsUrl // .targetUrl)}]' \
      "$out/pr.json" >"$out/checks.json"
    keys="$(jq -r '.title + "\n" + (.body // "") + "\n" + .headRefName' "$out/pr.json" | ticket_keys)"
    owner="${repo%%/*}"; name="${repo##*/}"
    # Review threads carry resolution state only in GraphQL. Paginate threads; comments
    # inside a thread are capped at 100, which is noted in the output when hit.
    gh api graphql --paginate -F owner="$owner" -F name="$name" -F number="$number" -f query='
      query($owner:String!,$name:String!,$number:Int!,$endCursor:String){
        repository(owner:$owner,name:$name){ pullRequest(number:$number){
          reviewThreads(first:100, after:$endCursor){
            pageInfo{ hasNextPage endCursor }
            nodes{ id isResolved isOutdated path line originalLine
              comments(first:100){ totalCount nodes{ author{login} body createdAt url
                commit{oid} } } } } } } }' \
      | jq -s '[.[].data.repository.pullRequest.reviewThreads.nodes[]]' >"$out/threads.json"
    gh api --paginate "repos/$repo/pulls/$number/reviews" | jq -s 'add // []' >"$out/reviews.json"
    gh api --paginate "repos/$repo/issues/$number/comments" | jq -s 'add // []' >"$out/issue-comments.json"
    jq -n --slurpfile t "$out/threads.json" --slurpfile r "$out/reviews.json" --slurpfile c "$out/issue-comments.json" '{
      threads: [$t[0][] | {path, line, originalLine, resolved: .isResolved, outdated: .isOutdated,
        truncated: (.comments.totalCount > (.comments.nodes|length)),
        comments: [.comments.nodes[] | {author: .author.login, createdAt, commit: .commit.oid, url, body}]}],
      reviews: [$r[0][] | select((.body // "") != "") | {author: .user.login, state, commit: .commit_id, submittedAt: .submitted_at, body}],
      conversation: [$c[0][] | {author: .user.login, createdAt: .created_at, body}]
    }' >"$out/existing-feedback.json"
    rm -f "$out/threads.json" "$out/reviews.json" "$out/issue-comments.json"
    ;;
  branch)
    head_ref="${1:?head ref required}"; base_ref="${2:-}"
    if [[ -z "$base_ref" ]]; then
      base_ref="$(git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null || true)"
      [[ -n "$base_ref" ]] || { echo "no base given and origin/HEAD unknown; pass the base ref" >&2; exit 2; }
    fi
    head="$(git rev-parse "$head_ref^{commit}")"; base="$(git rev-parse "$base_ref^{commit}")"
    merge_base="$(git merge-base "$base" "$head")"
    diff_git "$merge_base" "$head" >"$out/diff.patch"
    diff_git --name-status "$merge_base" "$head" >"$out/files.txt"
    export_commit "$head"
    keys="$(printf '%s\n' "$head_ref"; git log --format=%B "$merge_base..$head")"; keys="$(printf '%s' "$keys" | ticket_keys)"
    ;;
  commit)
    head="$(git rev-parse "${1:?sha required}^{commit}")"
    shift
    parents="$(git rev-list --parents -n 1 "$head")"; read -r -a parent_ids <<<"$parents"
    parent=1
    if [[ "${1:-}" == --parent ]]; then parent="${2:?parent number required}"; shift 2
    elif [[ ${#parent_ids[@]} -gt 2 ]]; then
      echo "merge commit requires --parent N; select the intended comparison" >&2; exit 2
    fi
    [[ "$parent" =~ ^[1-9][0-9]*$ && $# -eq 0 ]] || { echo "invalid parent selection" >&2; exit 2; }
    if [[ ${#parent_ids[@]} -gt 1 ]]; then base="$(git rev-parse "$head^$parent")"
    elif [[ "$parent" == 1 ]]; then base="$(git hash-object -t tree /dev/null)"
    else echo "root commit has no selected parent" >&2; exit 2; fi
    merge_base="$base"
    diff_git "$base" "$head" >"$out/diff.patch"
    diff_git --name-status "$base" "$head" >"$out/files.txt"
    export_commit "$head"
    keys="$(git log -1 --format=%B "$head" | ticket_keys)"
    ;;
  range)
    base="$(git rev-parse "${1:?previous sha required}^{commit}")"; head="$(git rev-parse "${2:-HEAD}^{commit}")"
    merge_base="$base"
    git merge-base --is-ancestor "$base" "$head" ||
      echo "warning: $base is not an ancestor of $head (rebase or force-push); the increment diff is unreliable" >&2
    diff_git "$base" "$head" >"$out/diff.patch"
    diff_git --name-status "$base" "$head" >"$out/files.txt"
    export_commit "$head"
    keys="$(git log --format=%B "$base..$head" | ticket_keys)"
    ;;
  staged)
    base="$(git rev-parse HEAD)"; merge_base="$base"; head="index"
    diff_git --cached >"$out/diff.patch"
    diff_git --cached --name-status >"$out/files.txt"
    python3 "$helper" export index "$out/snapshot"
    ;;
  local)
    base="$(git rev-parse HEAD)"; merge_base="$base"; head="working-tree"
    diff_git HEAD >"$out/diff.patch"
    diff_git HEAD --name-status >"$out/files.txt"
    while IFS= read -r -d '' f; do
      rc=0; diff_git --no-index -- /dev/null "$f" >>"$out/diff.patch" || rc=$?
      [[ $rc -le 1 ]] || { echo "cannot capture untracked file: $f" >&2; exit "$rc"; }
      python3 -c 'import json,sys; print("A\t" + json.dumps(sys.argv[1]))' "$f" >>"$out/files.txt"
    done < <(git ls-files --others --exclude-standard -z)
    python3 "$helper" export local "$out/snapshot"
    ;;
  *) echo "unknown target kind: $kind (pr|branch|commit|range|staged|local)" >&2; exit 2 ;;
esac

python3 "$helper" export "$merge_base" "$out/base-snapshot"
case "$kind" in staged) after="$(python3 "$helper" fingerprint index)" ;;
  local) after="$(python3 "$helper" fingerprint local)" ;; *) after="" ;; esac
[[ "$before" == "$after" ]] || { echo "target changed during collection; discard this incomplete packet and recollect" >&2; exit 3; }

[[ -f "$out/existing-feedback.json" ]] ||
  jq -n --arg kind "$kind" '{threads: [], reviews: [], conversation: [], source: ("none: \($kind) target has no host feedback")}' \
    >"$out/existing-feedback.json"

jq -n --arg kind "$kind" --arg root "$root" --arg repo "$repo" --arg base "$base" \
  --arg head "$head" --arg mb "$merge_base" --argjson keys "$keys" \
  --arg fingerprint "$before" --slurpfile gaps "$out/snapshot-gaps.json" --slurpfile old_gaps "$out/base-snapshot-gaps.json" \
  --arg files "$(wc -l <"$out/files.txt" | tr -d ' ')" \
  --arg lines "$(grep -cE '^[+-][^+-]|^[+-]$' "$out/diff.patch" || true)" \
  '{target: $kind, repository_root: $root, repo: $repo, base: $base, head: $head,
    merge_base: $mb, changed_files: ($files|tonumber), changed_lines: ($lines|tonumber),
    source_fingerprint: $fingerprint, snapshot_gaps: $gaps[0], base_snapshot_gaps: $old_gaps[0],
    snapshot_complete: (($gaps[0]|length) == 0 and ($old_gaps[0]|length) == 0),
    ticket_keys: $keys, collected_at: (now|todate)}' >"$out/meta.json"

python3 "$helper" seal "$out"
echo "packet: $out"
jq -r '"target=\(.target) head=\(.head) merge_base=\(.merge_base) files=\(.changed_files) lines=\(.changed_lines) tickets=\(.ticket_keys|join(","))"' "$out/meta.json"
