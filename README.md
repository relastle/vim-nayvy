<h1 align="center">vim-nayvy</h1>

<p align="center">Enriching python coding.</p>

<p align="center">
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/v/nayvy?color=%23032794"/></a>
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/pyversions/nayvy?color=032794"/></a>
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/l/nayvy?color=032794"/></a>
</p>

<p align="center">
<a href="https://github.com/relastle/vim-nayvy/actions"><img src="https://github.com/relastle/vim-nayvy/workflows/pythontests/badge.svg"/></a>
</p>


## 1. Installation

Using [vim-plug](https://github.com/junegunn/vim-plug)

```vim
Plug 'relastle/vim-nayvy'
```

## 2. Usage

### 2.1 Commands

Please refer [doc](./doc/vim-nayvy.txt) for full documentation.
Some demonstrations are shown here.


#### NayvyImports

![nayvy_imports](https://user-images.githubusercontent.com/6816040/76696704-9576a480-66d1-11ea-9561-b08914e263f4.gif)

#### NayvyImportFZF

![nayvy_import_fzf](https://user-images.githubusercontent.com/6816040/76696705-9ad3ef00-66d1-11ea-9d7c-cf62b7f597c0.gif)

#### NayvyTestGenerate & NayvyTestGenerateFZF

![nayvy_test_generate](https://user-images.githubusercontent.com/6816040/76715742-f608ee80-6770-11ea-9f8e-d156292c48d6.gif)

### 2.2 Use with other plugin.

#### 2.2.1 [ALE](https://github.com/dense-analysis/ale)

[ALE](https://github.com/dense-analysis/ale), Asynchronous Lint Engine, is one of the SOTA plugins of Vim.
Even though LSP is becoming more and more popular, the plugin provides brilliant features,
including great abstraction against code fixer.

Thus, vim-nayvy provides code fixer funciton `nayvy#ale_ficer`.

Vim script Below is a example of using `nayvy#ale_fixer` with
[autopep8](https://github.com/hhatto/autopep8) and [isort](https://github.com/timothycrosley/isort).

```vim
let g:ale_fixers = {
      \ 'python': ['nayvy#ale_fixer', 'autopep8', 'isort'],
      \ }

" or if you already defined `g:ale_fixer`, write
let g:ale_fixers['python'] = ['nayvy#ale_fixer', 'autopep8', 'isort']
```

And here is demonstrations.

![ale_fixer](https://user-images.githubusercontent.com/6816040/76823820-ac93ce80-6858-11ea-9a76-9c3b81b1b4e0.gif)

#### 2.2.2 [ultisnips](https://github.com/SirVer/ultisnips)


`vim-nayvy` provides `auto_import` function used with UltiSnips' snippet.
UltiSnips provides `post_expand` trigger for each single snippet,
which executes prerefined command when the snippet is expanded.

The snippet fragment below import `auto_import` function from `nayvy`,
and defines pretty print post fix completion that add import statement
`from pprint import pprint as pp` if not exists.

```
global !p
from nayvy_vim_if.ultisnips import (
	auto_import,
)
endglobal

post_expand "auto_import(snip, 'from pprint import pprint as pp', 0)"
snippet '((\S|\.)+)\.pp' "pprint postfix completion" r
`!p
var_name = match.group(1)
snip.rv = "pp(" + var_name + ")"
`
endsnippet
```
(The sample snippet is [here](./UltiSnips/python.snippets) and tested with a [vader script](./tests/test_ultisnips.vader))

Note that three arguments of `auto_import` are
- Snip object of UltiSnips. you should always pass `snip`
- Import statement string
- The import level
    - 0: Standard library imports.
    - 1: Related third party imports.
    - 2: Local application/library specific imports.

(cf. https://www.python.org/dev/peps/pep-0008/#imports)

And here is demonstrations.

![ultisnips_demo](https://user-images.githubusercontent.com/6816040/76824986-00ec7d80-685c-11ea-8945-d7386b3f620f.gif)

## 3. Feature roadmap

- [x] Auto imports (add and remove) based on pre-defined rules.
- [x] Importing multiple modules using [fzf](https://github.com/junegunn/fzf).
- [x] Touching or jumping to test script.
- [x] Auto generating or jump to test function.
- [x] Generating test functions using [fzf](https://github.com/junegunn/fzf).
- [x] Providing some domain objects useful in creating [ultisnips](https://github.com/SirVer/ultisnips) snippets.

## 4. Philosophy

Most python code parsing algorithms of `vim-nayvy` is not strict, and it contains some heuristics
( In other words, it is not based on AST, or hierarchical module structure).
However, it is intentional. I personally think the heuristics works well for most real-world usecases,
and has benefit in terms of performance.
The strategy is also robust against partially broken codes.
Some code actions (such as implementing test function and jumping) should be executable
when python code in current buffer is incomplete (cannot parsed via AST, or unimportable by `importlib`).

Now, it is the era of [LSP](https://microsoft.github.io/language-server-protocol).
I do not think prividing aid for code completion via non-LSP plugin is demanded,
as I personally think code completion is one of the most powerful and stable features privided by LSP.
Thus, the main aim of `vim-nayvy` is providing a little bit utility functions :smile:


## 5. Note

#### :construction:

- Please note that any destructive change (backward incompatible) can be done without any announcement.
- This plugin is in a very early stage of development. Feel free to report problemcs and feature requests, or make PRs.

## 6. [LICENSE](./LICENSE)

MIT
