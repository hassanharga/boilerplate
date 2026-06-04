#!/bin/sh
input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // empty')
repo=$(echo "$input" | jq -r '.workspace.repo | if . then .name else empty end')
branch=$(echo "$input" | jq -r 'if .worktree.branch then .worktree.branch elif .workspace.git_worktree then .workspace.git_worktree else empty end')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
cwd=$(echo "$input" | jq -r '.cwd // empty')

# Fallback: get branch from git
if [ -z "$branch" ] && [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)
fi

# Fallback: get repo name from git remote or directory name
if [ -z "$repo" ] && [ -n "$cwd" ]; then
  remote_url=$(git -C "$cwd" --no-optional-locks remote get-url origin 2>/dev/null)
  if [ -n "$remote_url" ]; then
    repo=$(basename "$remote_url" .git)
  else
    repo=$(basename "$cwd")
  fi
fi

# Default context to 0 if not yet available
if [ -z "$used" ]; then
  used=0
fi

parts=""

if [ -n "$model" ]; then
  parts=$(printf '\033[0;36m%s\033[0m' "$model")
fi

if [ -n "$repo" ]; then
  [ -n "$parts" ] && parts="$parts $(printf '\033[0;33m|\033[0m')"
  parts="$parts $(printf '\033[0;32m%s\033[0m' "$repo")"
fi

if [ -n "$branch" ]; then
  [ -n "$parts" ] && parts="$parts $(printf '\033[0;33m|\033[0m')"
  parts="$parts $(printf '\033[0;35m%s\033[0m' "$branch")"
fi

used_int=$(printf '%.0f' "$used")
[ -n "$parts" ] && parts="$parts $(printf '\033[0;33m|\033[0m')"
parts="$parts $(printf '\033[0;31mctx:%s%%\033[0m' "$used_int")"

printf '%s' "$parts"
