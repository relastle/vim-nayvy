python3 << EOF
import vim
from nayvy_vim_if import *
EOF

let s:nayvy_coc_enabled = get(g:, 'nayvy_coc_enabled', 1)
if !s:nayvy_coc_enabled || &compatible
    finish
endif
let s:nayvy_coc_completion_icon = get(g:, 'nayvy_coc_completion_icon', 'nayvy')

function! coc#source#nayvy#init() abort
  return {
        \ 'priority': 10,
        \ 'shortcut': s:nayvy_coc_completion_icon,
        \ 'filetypes': ['python'],
        \ 'triggerCharacters': []
        \}
endfunction

function s:nayvy_single_import_to_item(single_import) abort
  return {
        \ 'word': a:single_import['name'],
        \ 'menu': '(' . a:single_import['statement'] . ')',
        \ 'info': a:single_import['statement'],
        \ 'statement': a:single_import['statement'],
        \ 'level': a:single_import['level'],
        \ }
endfunction

function s:get_items() abort
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
  echom 'a:item: ' . string(a:item)
  call py3eval(printf(
        \ 'nayvy_import_stmt(%s, %s)',
        \ printf('"%s"', a:item['statement']),
        \ a:item['level'],
        \ ))
endfunction
