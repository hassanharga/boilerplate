#!/usr/bin/env bash
# Regression tests for run-challenger.sh. Stub CLIs on PATH record what they receive,
# so no provider is called. Run: bash scripts/test-run-challenger.sh
set -uo pipefail

script="$(cd "$(dirname "$0")" && pwd -P)/run-challenger.sh"
tmp="$(cd "$(mktemp -d)" && pwd -P)"  # macOS /var is a symlink to /private/var
trap 'rm -rf "$tmp"' EXIT
fails=0

ok()   { echo "ok   $1"; }
fail() { echo "FAIL $1"; fails=$((fails + 1)); }
has()  { grep -qF -- "$2" "$1"; }

# Stub: record argv (one per line), cwd, the recursion marker, stdin and
# OPENCODE_CONFIG_CONTENT, then behave enough like the real CLI for the script.
mkdir -p "$tmp/bin"
for cli in codex opencode pi claude; do
  cat >"$tmp/bin/$cli" <<'EOF'
#!/usr/bin/env bash
name="$(basename "$0")"
if [[ "$name" == codex && " $* " == *" mcp list "* ]]; then
  [[ -n "${STUB_MCP_FAIL:-}" ]] && exit 1
  echo '[{"name":"node_repl","enabled":true},{"name":"off_one","enabled":false}]'
  exit 0
fi
rec="$STUB_DIR/$name.rec"
{ printf '%s\n' "$@"; echo "CWD=$PWD"; echo "MARK=${REVIEW_CHANGES_CHALLENGER:-}"
  echo "OCC=${OPENCODE_CONFIG_CONTENT:-}"; } >"$rec"
[[ -t 0 ]] || cat >"$rec.stdin"
prev=""; for a in "$@"; do [[ "$prev" == -o ]] && echo "## Verdicts" >"$a"; prev="$a"; done
echo "## Verdicts"
exit "${STUB_EXIT:-0}"
EOF
  chmod +x "$tmp/bin/$cli"
done
export PATH="$tmp/bin:$PATH" STUB_DIR="$tmp"

# Fixture: workdir and packet whose paths contain spaces.
work="$tmp/my repo"; pkt="$tmp/my packet"
mkdir -p "$work" "$pkt"; echo "PROMPT-BODY" >"$pkt/prompt.md"
export XDG_STATE_HOME="$tmp/state"; mkdir -p "$XDG_STATE_HOME/opencode"

# </dev/null: stubs read stdin when it is not a terminal, and an inherited open pipe
# would block them forever.
run() { bash "$script" "$@" </dev/null >/dev/null 2>&1; }

# Every adapter: runs from workdir, marks recursion, writes output, keeps spaces intact.
for cli in codex opencode pi claude; do
  rm -f "$tmp/$cli.rec"
  if run "$cli" "$work" "$pkt" && has "$tmp/$cli.rec" "CWD=$work" &&
     has "$tmp/$cli.rec" "MARK=1" && [[ -s "$pkt/challenger-$cli.md" ]]; then
    ok "$cli: cwd, recursion marker, output file (paths with spaces)"
  else fail "$cli: cwd, recursion marker, output file (paths with spaces)"; fi
done

# The skill is copied into the packet so the sandboxed challenger can follow it.
skill_src="$(cd "$(dirname "$script")/.." && pwd -P)"
mkdir -p "$pkt/skill/stale"; rm -f "$pkt/challenger-pi.md"
if run pi "$work" "$pkt" && cmp -s "$skill_src/SKILL.md" "$pkt/skill/SKILL.md" &&
   cmp -s "$skill_src/references/design-principles.md" "$pkt/skill/references/design-principles.md" &&
   [[ ! -e "$pkt/skill/stale" ]]; then
  ok "skill copied fresh into the packet"
else fail "skill copied fresh into the packet"; fi

# Relative packet path still resolves after the script changes into workdir.
rm -f "$pkt/challenger-pi.md"
if (cd "$tmp" && bash "$script" pi "my repo" "my packet" </dev/null >/dev/null 2>&1) &&
   [[ -s "$pkt/challenger-pi.md" ]] && has "$tmp/pi.rec" "@$pkt/prompt.md"; then
  ok "relative workdir and packet paths"
else fail "relative workdir and packet paths"; fi

# Read-only and MCP restrictions per adapter.
run codex "$work" "$pkt"
if has "$tmp/codex.rec" "read-only" && has "$tmp/codex.rec" "apps" &&
   has "$tmp/codex.rec" "plugins" && has "$tmp/codex.rec" "mcp_servers.node_repl.enabled=false" &&
   ! has "$tmp/codex.rec" "off_one" && has "$tmp/codex.rec.stdin" "PROMPT-BODY"; then
  ok "codex: read-only sandbox, apps/plugins off, enabled MCP servers disabled"
else fail "codex: read-only sandbox, apps/plugins off, enabled MCP servers disabled"; fi

if STUB_MCP_FAIL=1 run codex "$work" "$pkt"; then fail "codex: refuses to run when MCP list fails"
else ok "codex: refuses to run when MCP list fails"; fi

run opencode "$work" "$pkt"
occ="$(sed -n 's/^OCC=//p' "$tmp/opencode.rec")"
if has "$tmp/opencode.rec" "--standalone" && has "$tmp/opencode.rec" "$pkt/prompt.md" &&
   jq -e --arg p "$pkt/*" '.permission["*"] == "deny" and .permission.read == "allow"
     and .permission.external_directory[$p] == "allow"
     and .permission.external_directory["*"] == "deny"' <<<"$occ" >/dev/null; then
  ok "opencode: standalone, deny-all except reads, packet readable"
else fail "opencode: standalone, deny-all except reads, packet readable"; fi

# A failing jq (only for the script under test) must stop OpenCode from launching.
mkdir -p "$tmp/badjq"; printf '#!/usr/bin/env bash\nexit 9\n' >"$tmp/badjq/jq"
chmod +x "$tmp/badjq/jq"; rm -f "$tmp/opencode.rec"
PATH="$tmp/badjq:$PATH" run opencode "$work" "$pkt"; rc=$?
if [[ $rc -ne 0 && ! -e "$tmp/opencode.rec" ]]; then
  ok "opencode: refuses to run when permission config cannot be built"
else fail "opencode: refuses to run when permission config cannot be built"; fi
# Same when jq succeeds but prints nothing.
printf '#!/usr/bin/env bash\nexit 0\n' >"$tmp/badjq/jq"; rm -f "$tmp/opencode.rec"
PATH="$tmp/badjq:$PATH" run opencode "$work" "$pkt" some/model; rc=$?
if [[ $rc -ne 0 && ! -e "$tmp/opencode.rec" ]]; then
  ok "opencode: refuses to run with empty permission config"
else fail "opencode: refuses to run with empty permission config"; fi

run pi "$work" "$pkt"
if has "$tmp/pi.rec" "--no-mcp" && has "$tmp/pi.rec" "--no-extensions" &&
   has "$tmp/pi.rec" "read,grep,find,ls"; then
  ok "pi: no MCP, no extensions, read tools only"
else fail "pi: no MCP, no extensions, read tools only"; fi

run claude "$work" "$pkt"
if has "$tmp/claude.rec" "--strict-mcp-config" && has "$tmp/claude.rec" "Read,Grep,Glob" &&
   has "$tmp/claude.rec" "plan" && has "$tmp/claude.rec.stdin" "PROMPT-BODY"; then
  ok "claude: strict MCP, read tools only, plan mode"
else fail "claude: strict MCP, read tools only, plan mode"; fi

# OpenCode model selection.
st="$XDG_STATE_HOME/opencode/model.json"
model_arg() { awk 'p{print; exit} $0=="-m"{p=1}' "$tmp/opencode.rec"; }
echo '{"recent":[{"providerID":"prov","modelID":"m1"}],"variant":{"prov/m1":"max"}}' >"$st"
run opencode "$work" "$pkt"; [[ "$(model_arg)" == "prov/m1#max" ]] &&
  ok "opencode: last TUI model with variant" || fail "opencode: last TUI model with variant"
echo '{"recent":[{"providerID":"prov","modelID":"m2"}]}' >"$st"
run opencode "$work" "$pkt"; [[ "$(model_arg)" == "prov/m2" ]] &&
  ok "opencode: last TUI model without variant" || fail "opencode: last TUI model without variant"
echo '{"recent":[]}' >"$st"
run opencode "$work" "$pkt"; ! has "$tmp/opencode.rec" "-m" &&
  ok "opencode: no saved model leaves default" || fail "opencode: no saved model leaves default"
run opencode "$work" "$pkt" other/x; [[ "$(model_arg)" == "other/x" ]] &&
  ok "opencode: explicit model wins" || fail "opencode: explicit model wins"

# Optional model for the other adapters.
run pi "$work" "$pkt"; ! has "$tmp/pi.rec" "--model" &&
  ok "pi: no model flag by default" || fail "pi: no model flag by default"
run claude "$work" "$pkt" opus; has "$tmp/claude.rec" "opus" &&
  ok "claude: explicit model passed" || fail "claude: explicit model passed"

# Exit code propagates; bad input is rejected.
STUB_EXIT=7 run pi "$work" "$pkt"; [[ $? -eq 7 ]] &&
  ok "CLI exit code propagates" || fail "CLI exit code propagates"
mkdir -p "$tmp/empty"; run pi "$work" "$tmp/empty"; [[ $? -eq 2 ]] &&
  ok "missing prompt.md rejected" || fail "missing prompt.md rejected"
run nosuch "$work" "$pkt"; [[ $? -ne 0 ]] &&
  ok "unknown agent rejected" || fail "unknown agent rejected"

echo; [[ $fails -eq 0 ]] && echo "all passed" || { echo "$fails failed"; exit 1; }
