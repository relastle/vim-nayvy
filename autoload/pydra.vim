if exists('b:did_autoload_pydra')
    finish
endif
let b:did_autoload_pydra = 1

python3 << EOF
import vim
from pydra_vim import (
    pydra_auto_imports,
    pydra_fix_lines,
    pydra_import,
    pydra_list_imports,
  )
EOF

" Automatically resolve current buffer's
" - Unused imports
" - undefine names
" warned by linters such as `flake` and `pyflakes`
function! pydra#imports() abort
  py3 pydra_auto_imports()
endfunction

function! pydra#ale_fixer(buffer) abort
  let l:py_expr = 'pydra_fix_lines(' . string(a:buffer) . ')'
  return py3eval(l:py_expr)
endfunction

" sink function for multiple selected import sentence
function! pydra#sink_multiple_imports(list) abort
  echom 'a:list: ' . string(a:list)
  let l:names = map(a:list, {index, line -> split(line, ":")[0]})
  echom 'l:names: ' . string(l:names)
  let l:py_expr = 'pydra_import(' . string(l:names) . ')'
  echom 'l:py_expr: ' . string(l:py_expr)
  call py3eval(l:py_expr)
endfunction

" list all available imports by calling python API
function! pydra#pydra_list_imports() abort
  return py3eval('pydra_list_imports()')
endfunction

" Import using fzf interface
function! pydra#import_fzf() abort
  let l:import_lst = pydra#pydra_list_imports()
  call fzf#run(extend({
        \ 'source': l:import_lst,
        \ 'sink*': function('pydra#sink_multiple_imports'),
        \ 'options': '-m',
        \ }, get(g:, 'fzf_layout', {})))
endfunction
