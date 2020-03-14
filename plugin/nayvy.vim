" plugin/nayvy.vim
" Copyright (c) 2020 Hiroki Konishi <relastle@gmail.com>
"
" Permission is hereby granted, free of charge, to any person obtaining a copy
" of this software and associated documentation files (the "Software"), to deal
" in the Software without restriction, including without limitation the rights
" to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
" copies of the Software, and to permit persons to whom the Software is
" furnished to do so, subject to the following conditions:
"
" The above copyright notice and this permission notice shall be included in
" all copies or substantial portions of the Software.
"
" THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
" IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
" FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
" AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
" LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
" OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
" SOFTWARE.

if exists('loaded_plugin_vim_nayvy') || &compatible
    finish
endif
let loaded_plugin_vim_nayvy=1

"---------------------------------------
" Imports
"---------------------------------------
command! NayvyImports call nayvy#imports()

"---------------------------------------
" Testing
"---------------------------------------
command! NayvyImportFZF call nayvy#import_fzf()
command! NayvyTouchUnitTestFile call nayvy#touch_unittest_file()
command! NayvyJumpToTestOrGenerate call nayvy#jump_to_test_or_generate()
command! NayvyMakeUnitTestFZF call nayvy#make_unittest_fzf()
