# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

export VISUAL=vi

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
	. "$HOME/.bashrc"
    fi
fi
alias google-chrome='google-chrome --force-dark-mode'

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi
PATH="$HOME/bin:$HOME/.local/bin:$PATH"
PATH="$HOME/.npm_modules/bin:$PATH"

#IBUS workaround for IntelliJ IDEA

#export IBUS_ENABLE_SYNC_MODE=1

# Ubuntu make installation of Android SDK
#PATH=$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$PATH

export QT_QPA_PLATFORMTHEME="qt5ct"
export MOSH_PREDICTION_DISPLAY=always

# Golang path
#export GOPATH=$HOME/golang
#export PATH=$GOPATH/bin:$PATH
# Ubuntu make installation of Ubuntu Make binary symlink
#PATH=/home/denis/.local/share/umake/bin:$PATH

#export LESS_TERMCAP_mb=$'\e[1;32m'
#NAO USAR!! causa erro no login!!!
#export LESS_TERMCAP_md=$'\e[1;32m'
#export LESS_TERMCAP_me=$'\e[0m'
#export LESS_TERMCAP_se=$'\e[0m'
#export LESS_TERMCAP_so=$'\e[01;33m'
#export LESS_TERMCAP_ue=$'\e[0m'
#export LESS_TERMCAP_us=$'\e[1;4;31m'

