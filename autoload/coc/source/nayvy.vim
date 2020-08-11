python3 << EOF
import vim
from nayvy_vim_if import *
from nayvy_vim_if.config import CONFIG
EOF

let s:nayvy_coc_enabled = py3eval('CONFIG.coc_enabled')
let s:nayvy_coc_completion_icon = py3eval('CONFIG.coc_completion_icon')

if !s:nayvy_coc_enabled || &compatible
  finish
endif

function! coc#source#nayvy#init() abort
  return {
        \ 'priority': 10,
        \ 'shortcut': s:nayvy_coc_completion_icon,
        \ 'filetypes': ['python'],
        \ 'triggerCharacters': []
        \}
endfunction

function! s:nayvy_single_import_to_item(single_import) abort
  return
        \ {
          \ 'word': a:single_import['name'],
          \ 'menu': '(' . a:single_import['statement'] . ')',
          \ 'filterText': a:single_import['statement'],
          \ 'statement': a:single_import['statement'],
          \ 'level': a:single_import['level'],
          \ 'documentation': [{
            \ 'filetype': 'markdown',
            \ 'content': "```python\n" . a:single_import['statement'] . "\n```",
          \ }],
        \ }
endfunction

function! s:get_items() abort
  let l:single_imports = py3eval('nayvy_list_imports()')
  let l:items = map(
        \ l:single_imports,
        \ {_, single_import -> s:nayvy_single_import_to_item(single_import)},
        \ )
  return l:items
endfunction

" Main source candidate functions
" which provide NON-imported statements.
function! coc#source#nayvy#complete(opt, cb) abort
  call a:cb(s:get_items())
endfunction

" When completed, import statement should be appended.
function! coc#source#nayvy#on_complete(item) abort
  call py3eval(printf(
        \ 'nayvy_import_stmt(%s, %s)',
        \ printf('"%s"', a:item['statement']),
        \ a:item['level'],
        \ ))
endfunction
