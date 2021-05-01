# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH

case $- in
    *i*)
        export PATH=$PATH:/snap/bin
        ;;
    *) ;;
esac

# alias tmux='TERM=xterm-88color tmux'
# alias tmux='export TERM_PROGRAM && tmux'

# TMUX
if [[ "$TERMINAL_EMULATOR" != "JetBrains-JediTerm" ]] && which tmux >/dev/null 2>&1 ; then
    #if not inside a tmux session, and if no session is started, start a new session
    # test -z "$TMUX" && (tmux attach || tmux new-session)
    # test -z "$TMUX" && (tmux)
	if [ -z "$TMUX" ]; then
		attach_session=$(tmux 2> /dev/null ls -F \
			'#{session_attached} #{?#{==:#{session_last_attached},},1,#{session_last_attached}} #{session_id}' |
			awk '/^0/ { if ($2 > t) { t = $2; s = $3 } }; END { if (s) printf "%s", s }')

		if [ -n "$attach_session" ]; then
			tmux attach -t "$attach_session"
		else
			tmux
		fi
	fi
fi

bindkey -v
# Use vim cli mode
# bindkey '^P' up-history
# bindkey '^N' down-history

# backspace and ^h working even after
# returning from command mode
bindkey '^?' backward-delete-char
bindkey '^h' backward-delete-char

# ctrl-w removed word backwards
bindkey '^w' backward-kill-word

# ctrl-r starts searching history backward
# bindkey '^r' history-incremental-search-backward

# Path to your oh-my-zsh installation.
export ZSH="/home/deoliveira/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
# ZSH_THEME="robbyrussell"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in ~/.oh-my-zsh/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to automatically update without prompting.
# DISABLE_UPDATE_PROMPT="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS=true

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
COMPLETION_WAITING_DOTS="true"

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
HIST_STAMPS="yyyy-mm-dd"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in ~/.oh-my-zsh/plugins/*
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
    bgnotify
    command-not-found
    docker
    docker-compose
    git
    git-extras
    jira
    mvn
    ubuntu
    yarn
    zsh-vim-mode
    fzf # (needs to be after vim-mode)
)

# Use fd (https://github.com/sharkdp/fd) instead of the default find
# command for listing path candidates.
# - The first argument to the function ($1) is the base path to start traversal
# - See the source code (completion.{bash,zsh}) for the details.
_fzf_compgen_path() {
  fdfind --hidden --follow --exclude ".git" . "$1"
}

# Use fd to generate the list for directory completion
_fzf_compgen_dir() {
  fdfind --type d --hidden --follow --exclude ".git" . "$1"
}

zstyle ':completion:*:*:docker:*' option-stacking yes
zstyle ':completion:*:*:docker-*:*' option-stacking yes

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

#setopt menucomplete

HISTFILE=~/.zsh_history
HISTSIZE=1000000
SAVEHIST=1000000
setopt appendhistory

source ~/.bash_aliases


ZSH_HIGHLIGHT_HIGHLIGHTERS=(main brackets)
export ZSH_HIGHLIGHT_MAXLENGTH=256
typeset -A ZSH_HIGHLIGHT_STYLES

# Override default styles to bright variation.
: ${ZSH_HIGHLIGHT_STYLES[reserved-word]:=fg=11}
: ${ZSH_HIGHLIGHT_STYLES[suffix-alias]:=fg=10,underline}
: ${ZSH_HIGHLIGHT_STYLES[precommand]:=fg=10,underline}
: ${ZSH_HIGHLIGHT_STYLES[globbing]:=fg=12}
: ${ZSH_HIGHLIGHT_STYLES[history-expansion]:=fg=12}
: ${ZSH_HIGHLIGHT_STYLES[command-substitution-delimiter]:=fg=13}
: ${ZSH_HIGHLIGHT_STYLES[process-substitution-delimiter]:=fg=13}
: ${ZSH_HIGHLIGHT_STYLES[back-quoted-argument-delimiter]:=fg=13}
: ${ZSH_HIGHLIGHT_STYLES[single-quoted-argument]:=fg=11}
: ${ZSH_HIGHLIGHT_STYLES[double-quoted-argument]:=fg=11}
: ${ZSH_HIGHLIGHT_STYLES[dollar-quoted-argument]:=fg=11}
: ${ZSH_HIGHLIGHT_STYLES[rc-quote]:=fg=14}
: ${ZSH_HIGHLIGHT_STYLES[dollar-double-quoted-argument]:=fg=14}
: ${ZSH_HIGHLIGHT_STYLES[back-double-quoted-argument]:=fg=14}
: ${ZSH_HIGHLIGHT_STYLES[back-dollar-quoted-argument]:=fg=14}
: ${ZSH_HIGHLIGHT_STYLES[arg0]:=fg=10}

ZSH_HIGHLIGHT_STYLES[alias]='fg=14'
ZSH_HIGHLIGHT_STYLES[path]='underline,fg=14'

hless () { highlight --out-format=ansi -s leo $@ | less -RN; }

setopt prompt_subst
PS1_L1="%F{10}%n@%M%f:%F{14}%~%f"
PS1_L2='${MODE_INDICATOR_PROMPT} %# '
if [[ -e /usr/lib/git-core/git-sh-prompt ]]; then
	source /usr/lib/git-core/git-sh-prompt
fi
GIT_PS1_SHOWCOLORHINTS=1
GIT_PS1_SHOWDIRTYSTATE=1
#GIT_PS1_SHOWUNTRACKEDFILES=1 # <- lento
GIT_PS1_SHOWUPSTREAM="verbose"
precmd () {
    DATEPROMPT=`date --rfc-3339=seconds`
    __git_ps1 "" " $DATEPROMPT" && RPROMPT="$PS1"
    PS1="$PS1_L1 
${PS1_L2}"
}

MODE_INDICATOR_VIINS='(ins)'
MODE_INDICATOR_VICMD='%B%F{11}(NRM)%b%f'
MODE_INDICATOR_REPLACE='%B%F{9}(RPL)%b%f'
MODE_INDICATOR_SEARCH='%B%F{13}(SCH)%b%f'
MODE_INDICATOR_VISUAL='%B%F{14}(VIS)%b%f'
MODE_INDICATOR_VLINE='%B%F{14}(VLI)%b%f'

MODE_CURSOR_VICMD="blinking block"
if [ "$TERM_PROGRAM" != 'vscode' ]; then
    MODE_CURSOR_VIINS="blinking bar"
else
    MODE_CURSOR_VIINS="blinking block"
fi
MODE_CURSOR_SEARCH="blinking underline"
export KEYTIMEOUT=20
bindkey -ra s

# Set colors for less. Borrowed from https://wiki.archlinux.org/index.php/Color_output_in_console#less .
# export LESS=-R
export LESS_TERMCAP_mb=$(tput blink; tput setaf 1)  # begin blink
export LESS_TERMCAP_md=$(tput bold;  tput setaf 6)  # begin bold
export LESS_TERMCAP_me=$(tput sgr0)                 # reset bold/blink
export LESS_TERMCAP_so=$(tput smso)                 # begin reverse video
export LESS_TERMCAP_se=$(tput rmso)                 # reset reverse video
export LESS_TERMCAP_us=$(tput smul; tput setaf 10)  # begin underline
export LESS_TERMCAP_ue=$(tput rmul; tput sgr0)      # reset underline

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias zgrep='zgrep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

alias -g G='| grep --color=always'
alias -g L="| less"

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
export SDKMAN_DIR="/home/deoliveira/.sdkman"
[[ -s "/home/deoliveira/.sdkman/bin/sdkman-init.sh" ]] && source "/home/deoliveira/.sdkman/bin/sdkman-init.sh"


export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libgtk3-nocsd.so.0

source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

