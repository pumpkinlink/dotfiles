set clipboard=unnamed
set showcmd
set backupdir=~/.local/share/nvim/backup
"let g:loaded_matchparen = 1
let g:matchparen_timeout = 2
let g:matchparen_insert_timeout = 2


" Map the leader key to SPACE
noremap <Space> <Nop>
let mapleader="\<Space>"
nnoremap <Leader>n :nohlsearch<Enter>

set ignorecase
set smartcase
set magic
set showmatch
set tabstop=4
if exists('g:vscode')
    nnoremap <Leader>s          :Write<Enter>
    nnoremap <Leader>q          :Quit<Enter>
    nnoremap <Leader><Tab>      :<C-u>call VSCodeNotify('workbench.action.focusNextGroup')<CR>
    nmap <Down> gj
    nmap <Up> gk
else
    nnoremap <silent> <leader>      :<c-u>WhichKey '<Space>'<CR>
    nnoremap <Leader>s          :write<Enter>
    nnoremap <Leader>q          :quit<Enter>
    nnoremap <Leader><Tab>      <C-w>w

    nmap <C-P> :FZF<CR>
    let $FZF_DEFAULT_COMMAND = 'fdfind --type f'

    autocmd InsertLeave,CompleteDone * if pumvisible() == 0 | pclose | endif
    filetype plugin indent on
    set background=dark

    set colorcolumn=81,121
    highlight ColorColumn ctermbg=234
    set number
    set mouse=a

    autocmd BufNewFile,BufRead /usr/share/X11/xkb/* set syntax=xkb

    set relativenumber
    set numberwidth=3
    highlight LineNr cterm=bold ctermbg=234
    highlight CursorLineNr cterm=reverse
    set fillchars+=vert:│
    highlight VertSplit cterm=NONE
    highlight Special ctermfg=217

    set autoread
    set nobackup
    set wildmenu

    "Don't ask to save when changing buffers (i.e. when jumping to a type definition)
    set hidden


    " :W sudo saves the file
    " (useful for handling the permission-denied error)
    command! W write !sudo tee % > /dev/null

    " Disable Ex mode combo
    :map Q <Nop>

    syntax enable
    set backspace=eol,start,indent
    set whichwrap+=<,>,h,l
    set hlsearch
    set incsearch
    set lazyredraw

    set cursorline
    highlight CursorLine cterm=NONE ctermbg=233
    set ffs=unix,dos,mac

    set expandtab
    set smarttab
    set shiftwidth=4
    set autoindent

    set title
    set laststatus=2

    set scrolloff=3
    set sidescroll=5
    highlight ModeMsg cterm=reverse,bold
    set ruler

endif
"------------------------ PLUG ---------------
call plug#begin('~/.config/nvim/plugged')
    Plug 'tpope/vim-surround'
    Plug 'bronson/vim-visual-star-search'

    if exists('g:vscode')

    else
        "Plug 'vimpostor/vim-tpipeline'
        "let g:tpipeline_cursormoved = 1
        "set guicursor=
        "set updatetime=300
        "set noswapfile
        "set stl=%!tpipeline#stl#line()


		"Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
		Plug 'junegunn/fzf.vim'
		"Plug 'airblade/vim-rooter'

        Plug 'yyq123/vim-syntax-logfile'
        Plug 'glacambre/firenvim', { 'do': { _ -> firenvim#install(0) } }

        Plug 'liuchengxu/vim-which-key'
        Plug 'liuchengxu/vim-which-key', { 'on': ['WhichKey', 'WhichKey!'] }

        "Plug 'shime/vim-livedown'
        Plug 'powerman/vim-plugin-AnsiEsc'
        Plug 'bronson/vim-trailing-whitespace'
        "Plug 'Valloric/MatchTagAlways',{'for': ['html', 'xhtml', 'xml', 'jinja']}
        Plug 'airblade/vim-gitgutter'
        let g:gitgutter_override_sign_column_highlight = 0
        highlight SignColumn cterm=bold ctermbg=NONE
        let g:gitgutter_sign_added = '➕'
        let g:gitgutter_sign_modified = '∼'
        let g:gitgutter_sign_removed = '＿'
        let g:gitgutter_sign_removed_first_line = '￣'
        let g:gitgutter_sign_modified_removed = '∼_'
    endif
call plug#end()
