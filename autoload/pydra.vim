" if exists('b:did_autoload_pydra')
"     finish
" endif
" let b:did_autoload_pydra = 1

" Also import vim as we expect it to be imported in many places.
py3 import vim
py3 from pydra_vim import pydra_import


function! pydra#imports() abort
  py3 pydra_import()
endfunction
