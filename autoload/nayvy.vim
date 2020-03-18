if exists('b:did_autoload_nayvy')
    finish
endif
let b:did_autoload_nayvy = 1

python3 << EOF
import vim
from nayvy_vim_if import *
EOF

"---------------------------------------
" Imports
"---------------------------------------

" Automatically resolve current buffer's
" - Unused imports
" - undefine names
" warned by linters such as `flake` and `pyflakes`
function! nayvy#imports() abort
  py3 nayvy_auto_imports()
endfunction

function! nayvy#ale_fixer(buffer) abort
  let l:py_expr = 'nayvy_get_fixed_lines(' . string(a:buffer) . ')'
  let l:res = py3eval(l:py_expr)
  if empty(l:res)
    return 0
  endif
  return l:res
endfunction

" sink function for multiple selected import statement
function! nayvy#sink_multiple_imports(list) abort
  let l:names = map(a:list, {index, line -> split(line, " : ")[0]})
  let l:py_expr = 'nayvy_import(' . string(l:names) . ')'
  call py3eval(l:py_expr)
endfunction

" list all available imports by calling python API
function! nayvy#nayvy_list_imports() abort
  return py3eval('nayvy_list_imports()')
endfunction

" Import using fzf interface
function! nayvy#import_fzf() abort
  let l:import_lst = nayvy#nayvy_list_imports()
  call fzf#run(extend({
        \ 'source': l:import_lst,
        \ 'sink*': function('nayvy#sink_multiple_imports'),
        \ 'options': '-m',
        \ }, get(g:, 'fzf_layout', {})))
endfunction

"---------------------------------------
" Testing
"---------------------------------------
function! nayvy#test_generate() abort
  let l:py_expr = 'nayvy_test_generate()'
  call py3eval(l:py_expr)
endfunction

" sink function for multiple selected untested functions
function! nayvy#sink_multiple_functions(list) abort
  let l:py_expr = 'nayvy_test_generate_multiple(' . string(a:list) .')'
  call py3eval(l:py_expr)
endfunction

" list all functions that are not tested in a `test_{}` manner
function! nayvy#nayvy_list_tested_and_untested_functions() abort
  return py3eval('nayvy_list_tested_and_untested_functions()')
endfunction

function! nayvy#test_generate_fzf() abort
  let l:function_lsts = nayvy#nayvy_list_tested_and_untested_functions()
  let l:tested_functions = l:function_lsts[0]
  let l:untedted_functions = l:function_lsts[1]
  call fzf#run(extend({
        \ 'source': l:tested_functions + l:untedted_functions,
        \ 'sink*': function('nayvy#sink_multiple_functions'),
        \ 'options': printf('-m --header-lines=%d', len(l:tested_functions)),
        \ }, get(g:, 'fzf_layout', {})))
endfunction
