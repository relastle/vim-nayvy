if exists('b:did_autoload_prussian')
    finish
endif
let b:did_autoload_prussian = 1

python3 << EOF
import vim
from prussian_vim_if import *
EOF

"---------------------------------------
" Imports
"---------------------------------------

" Automatically resolve current buffer's
" - Unused imports
" - undefine names
" warned by linters such as `flake` and `pyflakes`
function! prussian#imports() abort
  py3 prussian_auto_imports()
endfunction

function! prussian#ale_fixer(buffer) abort
  let l:py_expr = 'prussian_get_fixed_lines(' . string(a:buffer) . ')'
  return py3eval(l:py_expr)
endfunction

" sink function for multiple selected import statement
function! prussian#sink_multiple_imports(list) abort
  let l:names = map(a:list, {index, line -> split(line, ":")[0]})
  let l:py_expr = 'prussian_import(' . string(l:names) . ')'
  call py3eval(l:py_expr)
endfunction

" list all available imports by calling python API
function! prussian#prussian_list_imports() abort
  return py3eval('prussian_list_imports()')
endfunction

" Import using fzf interface
function! prussian#import_fzf() abort
  let l:import_lst = prussian#prussian_list_imports()
  call fzf#run(extend({
        \ 'source': l:import_lst,
        \ 'sink*': function('prussian#sink_multiple_imports'),
        \ 'options': '-m',
        \ }, get(g:, 'fzf_layout', {})))
endfunction

"---------------------------------------
" Testing
"---------------------------------------
function! prussian#touch_unittest_file() abort
  let l:py_expr = 'prussian_auto_touch_test("' . expand('%') . '")'
  call py3eval(l:py_expr)
endfunction


function! prussian#jump_to_test_or_generate() abort
  let l:py_expr = 'prussian_jump_to_test_or_generate("' . expand('%') . '", "' . expand('<cword>') . '")'
  call py3eval(l:py_expr)
endfunction

" sink function for multiple selected untested functions
function! prussian#sink_multiple_functions(list) abort
  " TODO:
endfunction

" list all functions that are not tested in a `test_{}` manner
function! prussian#prussian_list_untested_functions() abort
  return py3eval('prussian_list_untested_functions()')
endfunction

function! prussian#make_unittest_fzf() abort
  let l:function_lst = prussian#prussian_list_untested_functions()
  call fzf#run(extend({
        \ 'source': l:function_lst,
        \ 'sink*': function('prussian#sink_multiple_functions'),
        \ 'options': '-m',
        \ }, get(g:, 'fzf_layout', {})))
endfunction
