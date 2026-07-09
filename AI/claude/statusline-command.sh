#!/bin/sh
input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // empty')
effort=$(echo "$input" | jq -r '.effort.level // empty')
repo=$(echo "$input" | jq -r '.workspace.repo | if . then .name else empty end')
branch=$(echo "$input" | jq -r 'if .worktree.branch then .worktree.branch elif .workspace.git_worktree then .workspace.git_worktree else empty end')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
five_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_resets=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
week_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
week_resets=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')
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

parts=""

if [ -n "$model" ]; then
  if [ -n "$effort" ]; then
    parts=$(printf '\033[0;36m%s (%s)\033[0m' "$model" "$effort")
  else
    parts=$(printf '\033[0;36m%s\033[0m' "$model")
  fi
fi

if [ -n "$repo" ]; then
  [ -n "$parts" ] && parts="$parts $(printf '\033[0;33m|\033[0m')"
  parts="$parts $(printf '\033[0;32m%s\033[0m' "$repo")"
fi

if [ -n "$branch" ]; then
  [ -n "$parts" ] && parts="$parts $(printf '\033[0;33m|\033[0m')"
  parts="$parts $(printf '\033[0;35m%s\033[0m' "$branch")"
fi

if [ -n "$used" ]; then
  used_int=$(printf '%.0f' "$used")
  [ -n "$parts" ] && parts="$parts $(printf '\033[0;33m|\033[0m')"
  parts="$parts $(printf '\033[0;31mctx:%s%%\033[0m' "$used_int")"
fi

if [ -n "$five_pct" ]; then
  five_remaining=$(printf '%.0f' "$(echo "$five_pct" | awk '{print 100 - $1}')")
  if [ -n "$five_resets" ]; then
    reset_at=$(date -r "$five_resets" "+%-I:%M%p" 2>/dev/null | tr 'APM' 'apm')
    five_label=$(printf '5h:%s%% left (reset %s)' "$five_remaining" "$reset_at")
  else
    five_label=$(printf '5h:%s%% left' "$five_remaining")
  fi
  [ -n "$parts" ] && parts="$parts $(printf '\033[0;33m|\033[0m')"
  parts="$parts $(printf '\033[0;33m%s\033[0m' "$five_label")"
fi

if [ -n "$week_pct" ]; then
  week_remaining=$(printf '%.0f' "$(echo "$week_pct" | awk '{print 100 - $1}')")
  if [ -n "$week_resets" ]; then
    week_reset_at=$(date -r "$week_resets" "+%b %-d" 2>/dev/null)
    week_label=$(printf '7d:%s%% left (reset %s)' "$week_remaining" "$week_reset_at")
  else
    week_label=$(printf '7d:%s%% left' "$week_remaining")
  fi
  [ -n "$parts" ] && parts="$parts $(printf '\033[0;33m|\033[0m')"
  parts="$parts $(printf '\033[0;34m%s\033[0m' "$week_label")"
fi

printf '%s' "$parts"
