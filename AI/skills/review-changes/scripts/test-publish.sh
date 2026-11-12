#!/usr/bin/env bash
# Regression tests for publish.py. A stub `gh` on PATH serves a fake PR from a state
# file and records every write, so no GitHub call is made.
# Run: bash scripts/test-publish.sh
set -uo pipefail

script="$(cd "$(dirname "$0")" && pwd -P)/publish.py"
tmp="$(cd "$(mktemp -d)" && pwd -P)"
trap 'rm -rf "$tmp"' EXIT
fails=0
test_case=0
ok()   { echo "ok   $1"; }
fail() { echo "FAIL $1"; fails=$((fails + 1)); }

mkdir -p "$tmp/bin"
cat >"$tmp/bin/gh" <<'EOF'
#!/usr/bin/env python3
import json, os, sys
st_path = os.environ["STUB_STATE"]; st = json.load(open(st_path))
args = sys.argv[2:]  # drop "api"
method = "GET"
if "-X" in args: method = args[args.index("-X") + 1]
path = [a for a in args if a.startswith("repos/") or a == "user"][0]
body = json.loads(sys.stdin.read()) if "--input" in args else None
def save(): json.dump(st, open(st_path, "w"))
if path == "user": print(json.dumps({"login": "me"})); sys.exit(0)
if path.endswith("/reviews") and method == "GET": print(json.dumps(st["reviews"])); sys.exit(0)
if path.endswith("/comments") and method == "GET": print(json.dumps(st["comments"])); sys.exit(0)
if path.endswith("/reviews") and method == "POST":
    st["writes"].append({"kind": "review", **body})
    r = {"id": 1, "user": {"login": "me"}, "commit_id": body["commit_id"], "body": body["body"],
         "state": "COMMENTED" if body["event"] == "COMMENT" else "CHANGES_REQUESTED", "html_url": "u/review"}
    st["reviews"].append(r); save(); print(json.dumps(r)); sys.exit(0)
if path.endswith("/comments") and method == "POST":
    st["writes"].append({"kind": "comment", **body})
    if st.get("move_head_after_first_comment"): st["head"] = "f" * 40
    c = {"id": 100 + len(st["comments"]), "user": {"login": "me"}, "path": body["path"], "line": body["line"],
         "commit_id": body["commit_id"], "body": body["body"], "side": body["side"],
         "start_line": body.get("start_line"), "start_side": body.get("start_side"), "html_url": "u/c"}
    st["comments"].append(c); save(); print(json.dumps(c)); sys.exit(0)
if "/pulls/" in path:
    print(json.dumps({"head": {"sha": st["head"]}, "state": st.get("state", "open"),
                      "merged": False, "locked": st.get("locked", False), "draft": False})); sys.exit(0)
sys.exit(1)
EOF
chmod +x "$tmp/bin/gh"
export PATH="$tmp/bin:$PATH" STUB_STATE="$tmp/state.json"

head="$(printf 'a%.0s' {1..40})"
reset() { test_case=$((test_case+1)); jq -n --arg h "$head" '{head: $h, reviews: [], comments: [], writes: []}' >"$STUB_STATE"; }
plan() { jq -n --arg h "$head" --arg e "${1:-COMMENT}" '{repo: "o/r", pr: 1, commit: $h, event: $e,
  opener: "Went through the change.", comments: [
    {path: "a.ts", line: 3, body: "Type: Issue - Blocking\n\nIssue: x"},
    {path: "b.ts", line: 9, body: "Type: Question - Non-blocking\n\nIssue: y"}]}' >"$tmp/plan-$test_case.json"; }
writes() { jq '.writes | length' "$STUB_STATE"; }
run() { python3 "$script" "$tmp/plan-$test_case.json" "$@" >"$tmp/out.txt" 2>&1; }

reset; plan; run
[[ $? -eq 0 && "$(writes)" == 0 ]] && grep -q "would post" "$tmp/out.txt" &&
  ok "dry run writes nothing" || fail "dry run writes nothing"

reset; plan APPROVE; run --yes
[[ $? -eq 2 && "$(writes)" == 0 ]] && ok "APPROVE refused" || fail "APPROVE refused"

reset; jq '.head = "b"' "$STUB_STATE" >"$tmp/s" && mv "$tmp/s" "$STUB_STATE"; plan; run --yes
[[ $? -eq 1 && "$(writes)" == 0 ]] && grep -q "head moved" "$tmp/out.txt" &&
  ok "stops when head moved before writing" || fail "stops when head moved before writing"

reset; plan; run --yes
[[ $? -eq 0 && "$(jq -r '.writes[0].kind' "$STUB_STATE")" == review && "$(writes)" == 3 &&
   "$(jq -r '[.writes[] | .commit_id] | unique | length' "$STUB_STATE")" == 1 ]] &&
  grep -q "posted and verified" "$tmp/out.txt" &&
  ok "opener first, both comments pinned to the commit and verified" ||
  fail "opener first, both comments pinned to the commit and verified"

run --yes
[[ $? -eq 0 && "$(writes)" == 3 ]] && grep -q "already posted" "$tmp/out.txt" &&
  ok "re-run is idempotent" || fail "re-run is idempotent"

reset; jq '.move_head_after_first_comment = true' "$STUB_STATE" >"$tmp/s" && mv "$tmp/s" "$STUB_STATE"; plan; run --yes
[[ $? -eq 1 && "$(writes)" == 2 ]] && grep -q "PR changed before this comment" "$tmp/out.txt" &&
  ok "stops mid-way when head moves, reports partial" || fail "stops mid-way when head moves, reports partial"

echo; [[ $fails -eq 0 ]] && echo "all passed" || { echo "$fails failed"; exit 1; }
