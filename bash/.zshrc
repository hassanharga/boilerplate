# >>> ghost-complete initialize >>>
# !! Contents within this block are managed by 'ghost-complete install' !!
if [[ -f '/Users/hharga/.config/ghost-complete/shell/init.zsh' ]]; then
  builtin source '/Users/hharga/.config/ghost-complete/shell/init.zsh'
else
  echo "ghost-complete: init script missing: "'/Users/hharga/.config/ghost-complete/shell/init.zsh' >&2
  echo "ghost-complete: run 'ghost-complete install' to restore it" >&2
fi
# <<< ghost-complete initialize <<<
# Amazon Q pre block. Keep at the top of this file.
[[ -f "${HOME}/Library/Application Support/amazon-q/shell/zshrc.pre.zsh" ]] && builtin source "${HOME}/Library/Application Support/amazon-q/shell/zshrc.pre.zsh"
# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="robbyrussell"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
# zsh-autosuggestions
plugins=(git zsh-syntax-highlighting)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi
# Open editor-launching CLIs (git commit, fc, kubectl edit…) in VS Code.
export EDITOR="code --wait"
export VISUAL="code --wait"

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

export PATH=$HOME/.gem/bin:$PATH

export PATH=$HOME/development/flutter/bin:$PATH

export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home

# export PATH="${HOME}/Library/Android/sdk/build-tools:${HOME}/Library/Android/sdk/platform-tools:${PATH}"
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/build-tools

# Amazon Q post block. Keep at the bottom of this file.
[[ -f "${HOME}/Library/Application Support/amazon-q/shell/zshrc.post.zsh" ]] && builtin source "${HOME}/Library/Application Support/amazon-q/shell/zshrc.post.zsh"
[[ "$TERM_PROGRAM" == "vscode" ]] && . "$(code --locate-shell-integration-path zsh)"


export PATH=$(go env GOPATH)/bin:$PATH

# pnpm
export PNPM_HOME="/Users/hharga/Library/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME/bin:"*) ;;
  *) export PATH="$PNPM_HOME/bin:$PATH" ;;
esac
# pnpm end

alias python=python3

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/hharga/Downloads/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/hharga/Downloads/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/hharga/Downloads/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/hharga/Downloads/google-cloud-sdk/completion.zsh.inc'; fi

# Added by Antigravity
export PATH="/Users/hharga/.antigravity/antigravity/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"

# Claude Code with GLM-5
# function claude() {
# 	if [ "$1" = "glm" ]; then
# 		export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
# 		export ANTHROPIC_AUTH_TOKEN="253fe2d86e8243749c23654d8c4bbe1f.dQyIHmSns9Xj1gMN"
# 		export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-5"
# 		export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5"
# 		export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-5"
#     export API_TIMEOUT_MS="3000000"
# 		echo "⚡️ Mode: GLM-5 (z.ai API) - 90% cheaper, Sonnet+ quality"
# 		shift
# 	fi
# 	command claude "$@"
# }

alias oc='opencode'

# Open the current folder (or a given path) in VS Code.
c() { code "${1:-.}"; }

alias cc='claude'
# alias ccp='claude --dangerously-skip-permissions'
alias ccr='claude --resume'
alias cci='CLAUDE_CODE_NEW_INIT=1 claude'

# Run Claude Code inside tmux (alt-screen) so Warp doesn't balloon RAM on
# heavy multi-subagent runs. Usage: cct [claude args...]
cct() {
  command -v tmux >/dev/null 2>&1 || { echo "tmux not installed (brew install tmux)"; return 1; }
  tmux new-session -s "cc-${PWD:t}-$$" claude "$@"
}

# export CLAUDE_CODE_NEW_INIT=1
# >>> ghost-complete shell integration >>>
# !! Contents within this block are managed by 'ghost-complete install' !!
source '/Users/hharga/.config/ghost-complete/shell/ghost-complete.zsh'
# <<< ghost-complete shell integration <<<

# Show system info on new interactive shells (skip inside tmux/SSH/agents).
if [[ -o interactive && -z "$TMUX" && -z "$SSH_CONNECTION" ]] && command -v fastfetch >/dev/null 2>&1; then
  fastfetch
fi

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

# Starship prompt (overrides the oh-my-zsh theme). Keep this last.
command -v starship >/dev/null 2>&1 && eval "$(starship init zsh)"
