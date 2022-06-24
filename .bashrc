# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples


# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

################   LIQUID PROMPT #################
#source ~/liquidprompt/liquidprompt

set enable-bracketed-paste on

## FZF
# Setting fd as the default source for fzf
export FZF_DEFAULT_COMMAND='fdfind --type f'
# To apply the command to CTRL-T as well
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

stty -ixon
shopt -s autocd

LIGHT_BLUE='\e[1;34m'

LIGHT_GREEN='\e[1;32m'

NC='\e[0m' # No Color

export GIT_PS1_SHOWCOLORHINTS=1

export GIT_PS1_SHOWDIRTYSTATE=1

# export GIT_PS1_SHOWUNTRACKEDFILES=1 # <- lento

# Allow the user to set the title.
function title {
   echo -ne "\033]0;$1 (@$HOSTNAME)\007"
}

export PROMPT_COMMAND='__git_ps1 "${debian_chroot:+($debian_chroot)}$LIGHT_GREEN\u@\h$NC:$LIGHT_CYAN\w$NC" "\n$ "; title $(dirs +0)'

######## MOST #############
#export PAGER="most"


#############
alias g=git
alias faustop='htop'
alias topper='htop'
alias topperson='htop'
alias topzera='htop'
alias info='info --vi-keys'
alias ccat='highlight --out-format=ansi'
alias vpncompsis='netExtender --username=deoliveira --domain=intranet.local --auto-reconnect --dns-only-local 189.127.15.34:4433'


# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoredups

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=
HISTFILESIZE=

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
#case "$TERM" in
#xterm*|rxvt*)
    #PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    #;;
#*)
    #;;
#esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi



# [ "$DISPLAY" ] && xset b 50 20000 1

shopt -s cdspell

[ -s "/home/denis/.dnx/dnvm/dnvm.sh" ] && . "/home/denis/.dnx/dnvm/dnvm.sh" # Load dnvm

# added by Miniconda2 4.1.11 installer
export PATH="/home/denis/miniconda2/bin:$PATH"

export TWITTER_CONSUMER_KEY="EMS50BQBYXJ4j2zgrF82Nmcl6"
export TWITTER_CONSUMER_SECRET="vdi5Oa3JpogxCpuJfrQ5Yy5n4nuyAwgnKatmddd7G6kJRIkjty"
export TWITTER_ACCESS_TOKEN="11019442-xH2cidSPIMh1dOFRcURvENT9V9YDx1J1rH1t66MdU"
export TWITTER_ACCESS_TOKEN_SECRET="0bFQZytd4NKk4De2cKxfaPWzlY25rbC4RRPH8py7cJmFu"


# fzf
set -o vi
source /usr/share/doc/fzf/examples/key-bindings.bash
source /usr/share/doc/fzf/examples/completion.bash

export LESS="--ignore-case --status-column --LONG-PROMPT --HILITE-UNREAD --RAW-CONTROL-CHARS"


# termcap terminfo
# ----------------------------------------------------
# mb      blink     start blink
# md      bold      start bold
#
# so      smso      start standout (reverse video)
# se      rmso      stop standout
#
# us      smul      start underline
# ue      rmul      stop underline
#
# me      sgr0      turn off bold, blink and underline


# 1 -> red
# 2 -> green
# 3 -> yellow
man() {
    LESS_TERMCAP_md=$(tput bold; tput setaf 1) \
    LESS_TERMCAP_me=$(tput sgr0) \
    \
    LESS_TERMCAP_us=$(tput smul; tput setaf 2) \
    LESS_TERMCAP_ue=$(tput rmul; tput sgr0) \
    \
    LESS_TERMCAP_so=$(tput smso; tput setaf 3) \
    LESS_TERMCAP_se=$(tput rmso; tput sgr0) \
    command man "$@"
}

export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libgtk3-nocsd.so.0

# add laravel to path
export PATH="/home/denis/.config/composer/vendor/bin:$PATH"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/denis/Downloads/.miniconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/denis/Downloads/.miniconda/etc/profile.d/conda.sh" ]; then
        . "/home/denis/Downloads/.miniconda/etc/profile.d/conda.sh"
    else
        export PATH="/home/denis/Downloads/.miniconda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

