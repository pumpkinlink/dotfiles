augroup reload_vimrc " {
    autocmd!
    autocmd BufWritePost $MYVIMRC source $MYVIMRC
augroup END " }

filetype plugin on
filetype indent on

set colorcolumn=81
set number
highlight CursorLineNr cterm=bold ctermbg=11 ctermfg=0
"set cursorline
set relativenumber
highlight LineNr cterm=bold

set autoread
set wildmenu

" :W sudo saves the file
" (useful for handling the permission-denied error)
command! W w !sudo tee % > /dev/null

syntax enable

set backspace=eol,start,indent
set whichwrap+=<,>,h,l
set ignorecase
set smartcase
set hlsearch
set incsearch
set lazyredraw
set magic
set showmatch

if &term == "linux"
    set t_Co=8
elseif &term == "screen" || &term == "xterm"
    set t_Co=16
endif
set background=dark
set ffs=unix,dos,mac

set expandtab
set smarttab
set shiftwidth=4
set tabstop=4
set autoindent
set wrap

set statusline=2
set showcmd

map 0 ^

call plug#begin('~/.vim/plugged')
Plug 'valloric/youcompleteme', {'do': 'git submodule update --init --recursive && ./install.py'}
autocmd! User YouCompleteMe if !has('vim_starting') | call youcompleteme#Enable() | endif
call plug#end()
