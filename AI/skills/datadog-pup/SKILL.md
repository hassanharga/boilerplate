---
name: datadog-pup
description: Use when querying, investigating, or changing anything in Datadog, including logs, metrics, monitors, dashboards, traces, incidents, and SLOs. Covers choosing the `pup` CLI over the Datadog MCP server and handling `pup` authentication failures inside an agent sandbox.
---

# Datadog with pup

- Prefer `pup` (Datadog API CLI; `/opt/homebrew/bin/pup` on this Mac) for Datadog operations instead of the Datadog MCP server. Use `--read-only` for investigations and reviews. Check its available commands and authentication before use; do not invent subcommands. If `pup` is unavailable or cannot perform the required operation, explain the limitation and use an available authorized fallback.
- If `pup` works in the user terminal but reports missing credentials or network access in an agent sandbox, use the platform approval flow to check the specific command with access to the existing credential store and network. Do not mistake a sandbox-only authentication failure for a missing login or switch to MCP before checking. Preserve credential storage and sandbox controls; never print tokens or copy them into shell configuration.
