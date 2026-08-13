# Ghostty Terminal — Team Setup Guide (macOS)

A complete, copy-paste setup for **Ghostty**: a fast, native, GPU-accelerated
terminal that stays light on memory — plus the shell tooling that makes it a
pleasant daily driver.

> **Why move off Warp?** Warp renders every command as a rich, structured
> "block" kept in RAM. Under heavy streaming output (e.g. running AI coding
> agents with many parallel subagents), that scrollback can balloon to **tens
> of GB and freeze the machine**. Ghostty stores scrollback as a cheap cell
> grid with a bounded limit, so memory stays flat regardless of output volume.

---

## TL;DR (fast path)

```bash
# 1. Terminal + font
brew install --cask ghostty
brew install --cask font-jetbrains-mono-nerd-font

# 2. CLI tooling
brew install fzf zoxide eza bat fastfetch tmux starship

# 3. Drop in the config (see "Ghostty config" section), then add the
#    shell block (see "Shell integration") to ~/.zshrc and reload.
```

Then open Ghostty and reload config with **⌘ + Shift + ,**.

---

## Prerequisites

- macOS (Apple Silicon or Intel)
- [Homebrew](https://brew.sh) installed
- Zsh as your shell (default on modern macOS)

---

## 1. Install Ghostty

```bash
brew install --cask ghostty
```

Launch it once from `/Applications` so macOS clears the Gatekeeper prompt.

Verify:

```bash
ghostty --version
```

---

## 2. Install a Nerd Font

Icons in `eza`, `fastfetch`, and most prompts need a **Nerd Font** (a font
patched with extra glyphs). We standardize on JetBrainsMono:

```bash
brew install --cask font-jetbrains-mono-nerd-font
```

The config below references it as `JetBrainsMono Nerd Font Mono`.

---

## 3. Install CLI tooling

```bash
brew install fzf zoxide eza bat fastfetch tmux starship
```

| Tool        | Replaces / adds                                              |
|-------------|-------------------------------------------------------------|
| `fzf`       | Fuzzy finder — **Ctrl-R** history search, **Ctrl-T** files  |
| `zoxide`    | Smarter `cd` — `z <partial>` jumps to known dirs            |
| `eza`       | Modern `ls` with icons + git status                         |
| `bat`       | `cat` with syntax highlighting                              |
| `fastfetch` | System-info splash on terminal launch                       |
| `tmux`      | Terminal multiplexer (for heavy AI-agent sessions, §7)      |
| `starship`  | Fast, informative shell prompt (full path + git + versions) |

---

## 4. Ghostty config

Create `~/.config/ghostty/config`:

```bash
mkdir -p ~/.config/ghostty
```

Paste the following into `~/.config/ghostty/config`:

```ini
# Ghostty config — see `ghostty +show-config --default --docs` for every option.
# Reload after editing: Cmd+Shift+, (or quit and reopen).

# ── Theme ──────────────────────────────────────────────────────────
# Ayu ships built into Ghostty. Browse all 463: `ghostty +list-themes`.
theme = Ayu

# ── Font ───────────────────────────────────────────────────────────
# JetBrainsMono Nerd Font — JetBrains Mono + icon glyphs for eza/prompts.
font-family = JetBrainsMono Nerd Font Mono
font-size = 14
# Slightly bolder glyphs on macOS Retina.
font-thicken = true
# A touch more line breathing room.
adjust-cell-height = 12%

# ── Window / chrome ────────────────────────────────────────────────
# Subtle translucency + blur. Set opacity to 1.0 if you prefer solid.
background-opacity = 0.96
background-blur = 20
window-padding-x = 14
window-padding-y = 12
window-padding-balance = true
# Native tabs that match the theme.
macos-titlebar-style = tabs
# Restore windows/tabs and working dirs on relaunch.
window-save-state = always
window-colorspace = display-p3
# Don't quit the app when the last window closes (keeps it in the dock).
quit-after-last-window-closed = false

# ── Cursor ─────────────────────────────────────────────────────────
cursor-style = block
cursor-style-blink = true
mouse-hide-while-typing = true

# ── Keyboard ───────────────────────────────────────────────────────
# Make the macOS Option key behave as Alt/Meta so word-wise motions
# (Alt+←/→, Alt+Backspace) work in zsh.
macos-option-as-alt = true

# ── Shell integration ──────────────────────────────────────────────
# Auto-detected for zsh; this enables the niceties explicitly.
shell-integration = zsh
shell-integration-features = cursor,sudo,title

# ── Scrollback ─────────────────────────────────────────────────────
# Bytes. 10MB default is plenty even for heavy agent output, and Ghostty
# stores it cheaply (this is what spares you Warp's RAM blowup).
scrollback-limit = 10000000

# ── Safety ─────────────────────────────────────────────────────────
# Only warn on close if a process is still running (no nag on idle tabs).
confirm-close-surface = false

# ── Quick terminal (drop-down) ─────────────────────────────────────
# A global hotkey terminal that slides down over any app.
keybind = global:cmd+grave_accent=toggle_quick_terminal
quick-terminal-position = top
quick-terminal-animation-duration = 0.12
```

Validate it:

```bash
ghostty +validate-config   # prints nothing if all good
```

**Tweak to taste:**
- Bigger/smaller text → `font-size`.
- Solid background → set `background-opacity = 1.0` and remove `background-blur`.
- Different theme → `ghostty +list-themes` (interactive live preview), then set
  `theme = <name>`. For auto light/dark: `theme = dark:Ayu Mirage,light:Ayu Light`.

---

## 5. Shell integration (`~/.zshrc`)

Append this block to the **end** of `~/.zshrc`:

```bash
# ── Modern CLI tooling ─────────────────────────────────────────────
# fzf: Ctrl-R fuzzy history search, Ctrl-T file picker, **<Tab> completion.
command -v fzf >/dev/null 2>&1 && source <(fzf --zsh)
# zoxide: smarter cd — `z <partial>` jumps to a known dir, `zi` picks interactively.
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init zsh)"
# eza: modern ls with icons + git status.
if command -v eza >/dev/null 2>&1; then
  alias ls='eza --icons --group-directories-first'
  alias ll='eza -lah --icons --group-directories-first --git'
  alias la='eza -a --icons --group-directories-first'
  alias lt='eza --tree --level=2 --icons'
fi
# bat: cat with syntax highlighting (no pager, so it behaves like cat).
command -v bat >/dev/null 2>&1 && alias cat='bat --style=plain --paging=never'

# Show system info on new interactive shells (skip inside tmux/SSH/agents).
if [[ -o interactive && -z "$TMUX" && -z "$SSH_CONNECTION" ]] && command -v fastfetch >/dev/null 2>&1; then
  fastfetch
fi

# Starship prompt (overrides the oh-my-zsh theme). Keep this last.
command -v starship >/dev/null 2>&1 && eval "$(starship init zsh)"
```

Reload:

```bash
source ~/.zshrc        # or just open a new Ghostty window
zsh -n ~/.zshrc        # optional: syntax-check
```

> The `command -v ... &&` guards mean the block is safe even if a tool isn't
> installed — nothing errors. The `cat → bat` alias only applies interactively;
> use `command cat` or `\cat` for the raw original.

### Prompt (Starship)

The default oh-my-zsh `robbyrussell` theme shows only the current folder name
and no git info. The `starship init` line in the block above replaces it with a
fast, informative prompt. Create `~/.config/starship.toml`:

```toml
# Starship prompt — https://starship.rs/config
# Two-line prompt: path + git + language versions on top, input caret below.

add_newline = true

format = """
$directory$git_branch$git_status\
$nodejs$python$golang$rust$java$docker_context$package\
$cmd_duration
$character"""

[directory]
truncation_length = 0       # show the full path (no shortening)
truncate_to_repo = false    # don't collapse to the repo root
style = "bold cyan"
read_only = " 󰌾"

[git_branch]
symbol = " "
style = "bold purple"

[git_status]
style = "bold yellow"

[cmd_duration]
min_time = 2000
format = "took [$duration]($style) "
style = "dimmed white"

[character]
success_symbol = "[❯](bold green)"
error_symbol = "[❯](bold red)"
```

Result (in a Node project on a git branch):

```
~/Work/yassir/repos/mob-dispatch-service on  feat/my-branch [!]  v24.16.0
❯
```

**Tweaks:**
- **Shorter path:** set `truncation_length = 3` (shows the last 3 dirs) or
  `truncate_to_repo = true` (path relative to the repo root).
- **Preset themes:** `starship preset --list`, then e.g.
  `starship preset nerd-font-symbols -o ~/.config/starship.toml` (overwrites
  the file — back it up first).
- Language modules (`$nodejs`, `$python`, …) only render inside a relevant
  project, so the prompt stays clean elsewhere.

---

## 6. fastfetch splash (optional customization)

The `~/.zshrc` block above already runs `fastfetch` on each new interactive
shell. To customize what it shows:

```bash
fastfetch --gen-config           # writes ~/.config/fastfetch/config.jsonc
fastfetch --list-logos           # browse alternative logos
fastfetch --logo <name>          # try one
```

It's gated to skip inside tmux, SSH sessions, and non-interactive shells so it
never pollutes scripts or remote logins.

---

## 7. tmux for heavy AI-agent sessions (optional but recommended)

When running AI coding agents that stream a lot of output (many parallel
subagents), run them **inside tmux**. tmux uses the terminal's *alternate
screen*, so the host terminal only ever renders one screenful — keeping memory
flat. tmux holds the scrollback in its own cheap buffer.

Create `~/.tmux.conf`:

```tmux
# Bounded scrollback: 50k lines/pane is generous but caps tmux's own memory.
set -g history-limit 50000
# Trackpad / mouse scroll.
set -g mouse on
# Better color + responsiveness.
set -g default-terminal "tmux-256color"
set -sg escape-time 10
set -g remain-on-exit off
```

Add a launcher to `~/.zshrc` (example for Claude Code — adapt the command for
your agent):

```bash
# Run an AI agent inside tmux (alt-screen) so the terminal doesn't balloon RAM.
# Usage: cct [args...]
cct() {
  command -v tmux >/dev/null 2>&1 || { echo "tmux not installed (brew install tmux)"; return 1; }
  tmux new-session -s "cc-${PWD:t}-$$" claude "$@"
}
```

tmux basics:
- Scroll: trackpad, or `Ctrl-b [` then arrows (`q` to exit scroll mode).
- Detach (leave it running): `Ctrl-b d` — reattach with `tmux attach`.
- Copy text: hold **Option** while selecting (mouse mode changes selection).

---

## 8. Migrating command history from Warp (optional)

Warp stores history in its own SQLite DB, not `~/.zsh_history`. To bring your
Warp history into Ghostty (which uses standard Zsh history):

```bash
# 1. Back up first
cp ~/.zsh_history ~/.zsh_history.bak

# 2. Locate Warp's DB
DB="$HOME/Library/Group Containers/2BBY89MBSN.dev.warp/Library/Application Support/dev.warp.Warp-Stable/warp.sqlite"

# 3. Append Warp commands in Zsh extended-history format, then dedupe.
#    (Run in a scratch dir; review before replacing ~/.zsh_history.)
sqlite3 -noheader "$DB" \
  "select '0' || cast(strftime('%s', start_ts) as integer) || ':0;' || command
   from commands where command is not null and trim(command) <> ''" \
| sed 's/^0/: /' >> ~/.zsh_history
```

For a clean merge (sorted by time, multi-line commands handled, exact
duplicates collapsed), use a small script instead of the one-liner — ask the
team's tooling channel for the `merge-history.mjs` helper. Verify with:

```bash
zsh -ic 'fc -R ~/.zsh_history; fc -l -5'
```

---

## 9. Verification checklist

```bash
ghostty +validate-config                       # config OK (no output)
ghostty +show-config | grep -E 'theme|font'    # theme + font applied
zsh -n ~/.zshrc                                 # zshrc valid
# In a NEW window, confirm integrations:
bindkey '^R' | grep -q fzf  && echo 'fzf ok'
whence -w z >/dev/null       && echo 'zoxide ok'
alias ls | grep -q eza       && echo 'eza ok'
alias cat | grep -q bat      && echo 'bat ok'
```

---

## Cheat sheet

### Ghostty keybindings
| Shortcut          | Action                          |
|-------------------|---------------------------------|
| ⌘ T               | New tab                         |
| ⌘ D               | Split right                     |
| ⌘ Shift D         | Split down                      |
| ⌘ + / ⌘ -         | Font size up / down             |
| ⌘ Shift ,         | Reload config                   |
| ⌘ ` (backtick)    | Toggle drop-down quick terminal |

### Shell
| Command / key | Does                                        |
|---------------|---------------------------------------------|
| `Ctrl-R`      | Fuzzy-search command history (fzf)          |
| `Ctrl-T`      | Fuzzy-pick a file path (fzf)                |
| `z <name>`    | Jump to a frequently-used directory         |
| `zi`          | Interactive directory jump                  |
| `ll` / `la`   | Detailed / all-files listing with icons     |
| `lt`          | Tree view (2 levels)                        |
| `cat <file>`  | Syntax-highlighted view (bat)               |

---

## Troubleshooting

- **Icons show as boxes (□):** Ghostty isn't using the Nerd Font. Confirm
  `font-family = JetBrainsMono Nerd Font Mono` and that the cask installed
  (`ls ~/Library/Fonts | grep -i jetbrains`). Reload with ⌘ Shift ,.
- **Config change didn't apply:** Reload with ⌘ Shift , — some options
  (e.g. `window-save-state`, `macos-titlebar-style`) need a brand-new window.
- **`fzf --zsh` errors:** Needs fzf ≥ 0.48. `brew upgrade fzf`.
- **Old history missing:** Ghostty reads `~/.zsh_history`; see §8 to import
  from Warp.

---

## Security note

**Never hardcode secrets (API keys, tokens) in `~/.zshrc`** — it's plaintext
and easily leaked. Use the macOS Keychain instead:

```bash
# store once (value is not echoed):
security add-generic-password -a "$USER" -s MY_TOKEN -w
# read it in ~/.zshrc:
export MY_TOKEN="$(security find-generic-password -a "$USER" -s MY_TOKEN -w 2>/dev/null)"
```

Note that `gh` (GitHub CLI) and `git` (`credential.helper osxkeychain`) already
manage their own credentials — you usually don't need a token env var at all.

---

## References

- Ghostty docs: https://ghostty.org/docs
- Ghostty config reference: `ghostty +show-config --default --docs`
- Starship: https://starship.rs/config
- fzf: https://github.com/junegunn/fzf
- zoxide: https://github.com/ajeetdsouza/zoxide
- eza: https://eza.rocks
- bat: https://github.com/sharkdp/bat
- fastfetch: https://github.com/fastfetch-cli/fastfetch
