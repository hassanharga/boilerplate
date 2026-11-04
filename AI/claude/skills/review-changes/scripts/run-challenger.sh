#!/usr/bin/env bash
# Launch one read-only challenger CLI for the review-changes challenge round.
#
# Usage: run-challenger.sh <codex|opencode|pi|claude> <workdir> <packet-dir> [model]
#
#   workdir     Directory holding the reviewed snapshot (repo checkout or isolated copy).
#   packet-dir  Directory outside the reviewed target containing prompt.md (the filled
#               challenger brief), diff.patch, draft-findings.md and existing-feedback.md.
#               The script copies this skill's SKILL.md and references into
#               <packet-dir>/skill, because the sandboxed CLIs can read only the
#               workdir and the packet.
#   model       Optional model override; omitted means the CLI's configured default,
#               except OpenCode, which reuses the model last chosen in its TUI.
#
# Writes <packet-dir>/challenger-<agent>.md (final answer) and .log (stderr/trace).
# Exit code is the CLI's. Exit 0 alone does not mean the report is complete.
#
# Read-only covers MCP servers and app connectors too: each CLI otherwise loads the
# user's servers (Jira, Notion, GitHub, ...), whose tools can write outside the sandbox.
set -euo pipefail

agent="${1:?agent required: codex|opencode|pi|claude}"
workdir="${2:?workdir required}"
packet="${3:?packet dir required}"
model="${4:-}"

[[ -d "$workdir" ]] || { echo "workdir not found: $workdir" >&2; exit 2; }
[[ -d "$packet" ]] || { echo "packet dir not found: $packet" >&2; exit 2; }
# Absolute paths, because the CLI runs from inside workdir.
workdir="$(cd "$workdir" && pwd -P)"
packet="$(cd "$packet" && pwd -P)"

prompt="$packet/prompt.md"
out="$packet/challenger-$agent.md"
log="$packet/challenger-$agent.log"

[[ -f "$prompt" ]] || { echo "missing $prompt" >&2; exit 2; }
command -v "$agent" >/dev/null || { echo "$agent is not installed" >&2; exit 127; }

# The challenger runs this same skill. Give it a fresh copy inside the packet.
skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
rm -rf "$packet/skill" && mkdir -p "$packet/skill" &&
  cp "$skill_dir/SKILL.md" "$packet/skill/" &&
  cp -R "$skill_dir/references" "$packet/skill/" ||
  { echo "cannot copy the skill into the packet" >&2; exit 4; }

# A challenger that loads review-changes must not start its own challenge round.
export REVIEW_CHANGES_CHALLENGER=1

cd "$workdir"
case "$agent" in
  codex)
    # The read-only sandbox covers files and shell only. Turn off app connectors and
    # plugins, then every MCP server still enabled in config.toml. Refuse to run if
    # that list cannot be read, rather than run with servers attached.
    off=(--disable apps --disable plugins --disable multi_agent --disable image_generation)
    servers="$(codex "${off[@]}" mcp list --json | jq -r '.[] | select(.enabled) | .name')" ||
      { echo "cannot list codex MCP servers; not running unrestricted" >&2; exit 3; }
    for s in $servers; do off+=(-c "mcp_servers.$s.enabled=false"); done
    codex exec -s read-only --ephemeral --skip-git-repo-check -C "$workdir" "${off[@]}" \
      ${model:+-m "$model"} -o "$out" - <"$prompt" >/dev/null 2>"$log"
    ;;
  opencode)
    # opencode run ignores the model last picked in the TUI, so reuse that choice
    # (with its variant) from OpenCode's state.
    state="${XDG_STATE_HOME:-$HOME/.local/state}/opencode/model.json"
    if [[ -z "$model" && -f "$state" ]] && command -v jq >/dev/null; then
      model="$(jq -r '.recent[0] as $r | select($r) | "\($r.providerID)/\($r.modelID)" as $id
        | $id + (if .variant[$id] then "#" + .variant[$id] else "" end)' "$state")"
    fi
    # Deny every tool except reads, which also removes bash and MCP tools; outside the
    # workdir only the packet is readable. Applies to this run only; --standalone is
    # required because the shared background service would ignore per-run config. The
    # prompt goes in as an attachment so its text never passes through shell interpolation.
    # Build it as its own checked step: a failure inside a VAR=$(...) command prefix
    # would not trip set -e and OpenCode would launch with no restrictions.
    config="$(jq -cn --arg p "$packet/*" '{permission: {"*": "deny",
      read: "allow", grep: "allow", glob: "allow", list: "allow",
      external_directory: {"*": "deny", ($p): "allow"}}}')" && [[ -n "$config" ]] ||
      { echo "cannot build opencode permission config; not running unrestricted" >&2; exit 3; }
    OPENCODE_CONFIG_CONTENT="$config" \
    opencode run --standalone --agent plan ${model:+-m "$model"} -f "$prompt" \
      "Follow the attached prompt.md exactly. It is your complete task." >"$out" 2>"$log"
    ;;
  pi)
    # The tool allowlist alone keeps MCP tools; --no-mcp and --no-extensions drop them.
    pi -p --no-session --no-mcp --no-extensions --tools read,grep,find,ls \
      ${model:+--model "$model"} \
      "@$prompt" "Follow the attached prompt.md exactly. It is your complete task." \
      >"$out" 2>"$log"
    ;;
  claude)
    # --tools limits built-in tools only; --strict-mcp-config with no --mcp-config
    # loads no MCP servers. --add-dir lets it open the packet.
    claude -p --no-session-persistence --permission-mode plan --strict-mcp-config \
      --tools "Read,Grep,Glob" --add-dir "$packet" ${model:+--model "$model"} \
      <"$prompt" >"$out" 2>"$log"
    ;;
  *)
    echo "unknown agent: $agent (use codex|opencode|pi|claude)" >&2
    exit 2
    ;;
esac
