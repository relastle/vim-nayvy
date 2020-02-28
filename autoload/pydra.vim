" if exists('b:did_autoload_pydra')
"     finish
" endif
" let b:did_autoload_pydra = 1

" Also import vim as we expect it to be imported in many places.
py3 import vim
py3 from pydra.models.imprt import ImportSentence
py3 from pydra.pydra_vim import test_function


function! pydra#imports() abort
  let l:res = py3eval('test_function()')
  echom 'l:res: ' . string(l:res)
endfunction
