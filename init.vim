"autocmd FileType javascript setlocal omnifunc=tern#Complete
augroup reload_vimrc " {
    autocmd!
    autocmd BufWritePost $MYVIMRC source $MYVIMRC
    autocmd BufWritePost "~/.nvimrc" source "~/.nvimrc"
augroup END " }

autocmd InsertLeave,CompleteDone * if pumvisible() == 0 | pclose | endif
filetype plugin indent on
set background=dark
set colorcolumn=81,121
highlight ColorColumn ctermbg=234
set number
set relativenumber
set numberwidth=3
highlight LineNr cterm=bold ctermbg=234
highlight CursorLineNr cterm=reverse
set fillchars+=vert:│
highlight VertSplit cterm=NONE
highlight Special ctermfg=217

set autoread
set nobackup
set hidden
set wildmenu

" :W sudo saves the file
" (useful for handling the permission-denied error)
command! W write !sudo tee % > /dev/null
function! StandardFormat()
    write
    !standard-format -w %
    Neomake
endfunction
command! Sformat silent call StandardFormat()

" Use ; for commands.
nnoremap ; :

inoremap jj <Esc>

" Map the leader key to SPACE
let mapleader="\<SPACE>"

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

set cursorline
highlight CursorLine cterm=NONE ctermbg=233
set ffs=unix,dos,mac

set expandtab
set smarttab
set shiftwidth=4
set tabstop=4
set autoindent

set title
set laststatus=0

set sidescroll=5
set showcmd
highlight ModeMsg cterm=reverse,bold
set ruler

call plug#begin('~/.config/nvim/plugged')
Plug 'tpope/vim-dispatch', {'for': 'cs'}
Plug 'OmniSharp/Omnisharp-vim', {'do': 'git submodule update --init --recursive && cd omnisharp-roslyn && ./build.sh', 'for': 'cs'}
Plug 'Shougo/unite.vim'
"Plug 'valloric/youcompleteme', {'do': 'git submodule update --init --recursive && ./install.py --tern-completer'}
"autocmd! User YouCompleteMe if !has('neovim_starting') | call youcompleteme#Enable() | endif
"let g:ycm_autoclose_preview_window_after_insertion = 1
"Plug 'ternjs/tern_for_vim', { 'do': 'npm install' }
Plug 'Shougo/deoplete.nvim' | Plug 'carlitux/deoplete-ternjs',{'for': 'javascript'}
Plug 'astralhpi/deoplete-omnisharp', {'for': 'cs'}
let g:deoplete#enable_at_startup = 1
inoremap <silent><expr> <Nul> deoplete#mappings#manual_complete()
inoremap <silent> <expr> <Tab> pumvisible()
            \ ? "<C-n>"
            \ : '<Tab>'
inoremap <silent> <expr> <S-Tab> pumvisible()
            \ ? "<C-p>"
            \ : '<S-Tab>'
let g:tern_request_timeout = 1
Plug 'Shougo/neco-vim', {'for': 'vim'}
Plug 'Shougo/vimproc.vim', {'do': 'make'} | Plug 'Shougo/vimshell.vim'
Plug 'zchee/deoplete-jedi', {'for': 'python'}

Plug 'sirver/ultisnips'|Plug 'honza/vim-snippets'|Plug 'jordwalke/JSDocSnippets'
let g:UltiSnipsExpandTrigger="<C-L>"
let g:JSDocSnippetsMapping='<C-D>'

Plug 'powerman/vim-plugin-AnsiEsc'
Plug 'pangloss/vim-javascript'
Plug 'bronson/vim-trailing-whitespace'
Plug 'severin-lemaignan/vim-minimap'
Plug 'nathanaelkane/vim-indent-guides'
let g:indent_guides_auto_colors = 0
highlight IndentGuidesOdd  ctermbg=233
highlight IndentGuidesEven ctermbg=235

Plug 'Valloric/MatchTagAlways',{'for': ['html', 'xhtml', 'xml', 'jinja']}

Plug 'benekastah/neomake'
let g:neomake_verbose=0
let g:neomake_javascript_enabled_makers = ['standard']
"jQuery global variable
let g:neomake_javascript_standard_maker = {'args':['--global', '$','--global', 'angular']}
let g:neomake_cs_enabled_makers = ['mcs']
let g:neomake_open_list = 2
autocmd! BufWritePost * silent Neomake

Plug 'airblade/vim-gitgutter'
let g:gitgutter_override_sign_column_highlight = 0
highlight SignColumn cterm=bold ctermbg=NONE
let g:gitgutter_sign_added = '➕'
let g:gitgutter_sign_modified = '∼'
let g:gitgutter_sign_removed = '＿'
let g:gitgutter_sign_removed_first_line = '￣'
let g:gitgutter_sign_modified_removed = '∼_'

call plug#end()
"Set the type lookup function to use the preview window instead of the status line
"let g:OmniSharp_typeLookupInPreview = 1

"Timeout in seconds to wait for a response from the server
let g:OmniSharp_timeout = 1

"Showmatch significantly slows down omnicomplete
"when the first match contains parentheses.
set noshowmatch

"don't autoselect first item in omnicomplete, show if only one item (for preview)
"remove preview if you don't want to see any documentation whatsoever.
set completeopt=longest,menuone,preview
" Fetch full documentation during omnicomplete requests.
" There is a performance penalty with this (especially on Mono)
" By default, only Type/Method signatures are fetched. Full documentation can still be fetched when
" you need it with the :OmniSharpDocumentation command.
" let g:omnicomplete_fetch_documentation=1

"Move the preview window (code documentation) to the bottom of the screen, so it doesn't move the code!
"You might also want to look at the echodoc plugin
"set splitbelow

" If you are using the omnisharp-roslyn backend, use the following
" let g:syntastic_cs_checkers = ['code_checker']
 "let g:OmniSharp_server_type = 'roslyn'
let g:OmniSharp_start_without_solution=1

augroup omnisharp_commands
    autocmd!

    "Set autocomplete function to OmniSharp (if not using YouCompleteMe completion plugin)
    autocmd FileType cs setlocal omnifunc=OmniSharp#Complete

    " Synchronous build (blocks Vim)
    "autocmd FileType cs nnoremap <F5> :wa!<cr>:OmniSharpBuild<cr>
    " Builds can also run asynchronously with vim-dispatch installed
    autocmd FileType cs nnoremap <leader>b :wa!<cr>:OmniSharpBuildAsync<cr>
    " automatic syntax check on events (TextChanged requires Vim 7.4)
    "autocmd BufEnter,TextChanged,InsertLeave *.cs SyntasticCheck

    " Automatically add new cs files to the nearest project on save
    autocmd BufWritePost *.cs call OmniSharp#AddToProject()

    "show type information automatically when the cursor stops moving
    autocmd CursorHold *.cs call OmniSharp#TypeLookupWithoutDocumentation()

    "The following commands are contextual, based on the current cursor position.

    autocmd FileType cs nnoremap         gd :OmniSharpGotoDefinition<cr>
    autocmd FileType cs nnoremap <leader>fi :OmniSharpFindImplementations<cr>
    autocmd FileType cs nnoremap <leader>ft :OmniSharpFindType<cr>
    autocmd FileType cs nnoremap <leader>fs :OmniSharpFindSymbol<cr>
    autocmd FileType cs nnoremap <leader>fu :OmniSharpFindUsages<cr>
    "finds members in the current buffer
    autocmd FileType cs nnoremap <leader>fm :OmniSharpFindMembers<cr>
    " cursor can be anywhere on the line containing an issue
    autocmd FileType cs nnoremap <leader>x  :OmniSharpFixIssue<cr>
    autocmd FileType cs nnoremap <leader>fx :OmniSharpFixUsings<cr>
    autocmd FileType cs nnoremap <leader>tt :OmniSharpTypeLookup<cr>
    autocmd FileType cs nnoremap <leader>dc :OmniSharpDocumentation<cr>
    "navigate up by method/property/field
    autocmd FileType cs nnoremap <C-K> :OmniSharpNavigateUp<cr>
    "navigate down by method/property/field
    autocmd FileType cs nnoremap <C-J> :OmniSharpNavigateDown<cr>

augroup END


" this setting controls how long to wait (in ms) before fetching type / symbol information.
set updatetime=1500
" Remove 'Press Enter to continue' message when type information is longer than one line.
"set cmdheight=2

" Contextual code actions (requires CtrlP or unite.vim)
nnoremap <leader><space> :OmniSharpGetCodeActions<cr>
" Run code actions with text selected in visual mode to extract method
vnoremap <leader><space> :call OmniSharp#GetCodeActions('visual')<cr>

" rename with dialog
nnoremap <leader>nm :OmniSharpRename<cr>
nnoremap <F2> :OmniSharpRename<cr>
" rename without dialog - with cursor on the symbol to rename... ':Rename newname'
command! -nargs=1 Rename :call OmniSharp#RenameTo("<args>")

" Force OmniSharp to reload the solution. Useful when switching branches etc.
nnoremap <leader>rl :OmniSharpReloadSolution<cr>
nnoremap <leader>cf :OmniSharpCodeFormat<cr>
" Load the current .cs file to the nearest project
nnoremap <leader>tp :OmniSharpAddToProject<cr>

" (Experimental - uses vim-dispatch or vimproc plugin) - Start the omnisharp server for the current solution
nnoremap <leader>ss :OmniSharpStartServer<cr>
nnoremap <leader>sp :OmniSharpStopServer<cr>

" Add syntax highlighting for types and interfaces
nnoremap <leader>th :OmniSharpHighlightTypes<cr>
"Don't ask to save when changing buffers (i.e. when jumping to a type definition)
set hidden
let g:OmniSharp_selector_ui = 'unite'  " Use unite.vim
