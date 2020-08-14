<h1 align="center">vim-nayvy</h1>

<p align="center">Enriching python coding.</p>

<p align="center">
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/v/nayvy?color=%23032794"/></a>
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/pyversions/nayvy?color=032794"/></a>
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/l/nayvy?color=032794"/></a>
<a href="https://github.com/relastle/vim-nayvy/releases"><img src="https://img.shields.io/github/v/tag/relastle/vim-nayvy?color=032794"/></a>
</p>

<p align="center">
<a href="https://github.com/relastle/vim-nayvy/actions"><img src="https://github.com/relastle/vim-nayvy/workflows/pythontests/badge.svg"/></a>
<a href="https://codecov.io/gh/relastle/vim-nayvy"><img src="https://codecov.io/gh/relastle/vim-nayvy/branch/master/graph/badge.svg" /></a>
</p>


## 1. Installation

Using [vim-plug](https://github.com/junegunn/vim-plug)

```vim
Plug 'relastle/vim-nayvy'
```

## 2. Usage

### 2.1 Commands

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

Thus, vim-nayvy provides code fixer funciton `nayvy#ale_fixer`.

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

#### 2.2.3 [coc.nvim](https://github.com/neoclide/coc.nvim)

This plugins also provide auto-completion of importable items, follewd by auto-importing of the completed items.
This is thanks to coc's ability to easily creating new coc sources
[Create custom source · neoclide/coc.nvim Wiki](https://github.com/neoclide/coc.nvim/wiki/Create-custom-source).

![nayvy_coc](https://user-images.githubusercontent.com/6816040/89722514-38371300-da25-11ea-8af3-7b93643d8a46.gif)


You should bundle `neoclide/coc.nvim` as well as `relastle/vim-nayvy`.

```vim
Plug 'neoclide/coc.nvim', {'branch': 'release'}
Plug 'relastle/vim-nayvy'
```

The automatic import in completion is conducted by the item-selected event.
By default, the event is fired by <kbd>Ctrl</kbd> + <kbd>y</kbd> (when the item is focused in pmenu).

If you use the following settings described [here](https://github.com/neoclide/coc.nvim#example-vim-configuration),

```vim
" Use <cr> to confirm completion, `<C-g>u` means break undo chain at current
" position. Coc only does snippet and additional edit on confirm.
" <cr> could be remapped by other vim plugin, try `:verbose imap <CR>`.
if exists('*complete_info')
  inoremap <expr> <cr> complete_info()["selected"] != "-1" ? "\<C-y>" : "\<C-g>u\<CR>"
else
  inoremap <expr> <cr> pumvisible() ? "\<C-y>" : "\<C-g>u\<CR>"
endif
```

the completion event can be trigger by just <kbd>Enter</kbd> (, which I personally recommend 👍).


## 3. Configurations

### 3.1 Configuration with vim `g:` variable or environment variable.

All configurable settings can be configured through vim script variables and environment variables.

This is because you may set some project-specific settings different from your global vim settings.
Thus, the priority of load settings is as follows.

```
Environment variable -> Vim script variable -> Default variable
```

| Vim Script variable name         | Environment variable name       | Description                                                                                   |
| ---                              | ---                             | ---                                                                                           |
| `g:nayvy_import_path_format`     | `$NAYVY_IMPORT_PATH_FORMAT`     | Define the import statement format when importing the class/function inside the same package. |
| `g:nayvy_linter_for_fix`         | `$NAYVY_LINTER_FOR_FIX`         | Define the linter to use when autofixing the missing imports or unused imports.               |
| `g:nayvy_pyproject_root_markers` | `$NAYVY_PYPROJECT_ROOT_MARKERS` | Define marker (filenames) indicating the python project root directory.                       |
| `g:nayvy_import_config_path`     | `$NAYVY_IMPORT_CONFIG_PATH`     | Define the file path containing your own import statement lines.                              |
| `g:nayvy_coc_enabled`            | `$NAYVY_COC_ENABLED`            | Define whether coc is enabled (1) or not (0).                                                 |
| `g:nayvy_coc_completion_icon`    | `$NAYVY_COC_COMPLETION_ICON`    | Define icon rendered in the completion item fron nayvy coc sources.                           |
| `g:nayvy_coc_menu_max_width`     | `$NAYVY_COC_MENU_MAX_WIDTH`     | Define max length of menu represented in completion menu by the coc source.                   |

#### g:nayvy_import_path_format ($NAYVY_IMPORT_PATH_FORMAT)

- `all_absolute` (Prefer all project classes/functions are imported with ***absolute*** path.)
- `all_relative` (Prefer all project classes/functions are imported with ***relative*** path.)
- `under_relative` (Prefer sub-package classes/functions are imported with ***relative*** path and ther other with ***absolute*** path)

#### g:nayvy_linter_for_fix ($NAYVY_LINTER_FOR_FIX)

- `pyflakes`
- `flake8`

#### g:nayvy_pyproject_root_markers ($NAYVY_PYPROJECT_ROOT_MARKERS)

Example of vim

```vim
let g:nayvy_pyproject_root_markers = [
  \ 'pyproject.toml',
  \ 'setup.py',
  \ 'setup.cfg',
  \ 'requirements.txt',
\ ]
```

Example of environment variable

```bash
export NAYVY_PYPROJECT_ROOT_MARKERS='pyproject.toml,setup.py'  # comma-separated format
```

#### g:nayvy_import_config_path ($NAYVY_IMPORT_CONFIG_PATH)

see the section below (3.2 Import configration).

#### g:nayvy_coc_enabled ($NAYVY_COC_ENABLED)

- 1: enabled
- 0: disabled

#### g:nayvy_coc_completion_icon ($NAYVY_COC_COMPLETION_ICON)

![nayvy_coc_completion_icon](https://user-images.githubusercontent.com/6816040/90264644-5ae58380-de8c-11ea-917b-c1cc24daa1d0.png)

Please set any string as you like 😄.

#### g:nayvy_coc_menu_max_width ($NAYVY_COC_MENU_MAX_WIDTH)

If the completion menu gets too wide, it may bother you.
So you can specify the max length of whole import statement.
If the statement length gets longer than the value, the `from` part of import statement(, which typically tends to be longer) will be trimmed.

![nayvy_coc_completion_menu](https://user-images.githubusercontent.com/6816040/90264634-57ea9300-de8c-11ea-90da-768ada57d660.png)

### 3.2 Importing configuration

Nayvy detects import statement should be used by looking into
`$XDG_CONFIG_PATH/nayvy/import_config.nayvy`.
(if $XDG_CONFIG_PATH is not set, `~/.config/nayvy/import_config.nayvy`)

If you set `g:nayvy_import_config_path` or `$NAYVY_IMPORT_CONFIG_PATH`, the file will be used.

You can use environment variable in the path like,

```vim
let g:nayvy_import_config_path = '$HOME/nayvy.py'
```

In the file, you can write any python import statements like this.

```python
from typing import List, Optional
from pprint import pprint as pp
import sys
import os

import numpy as np

from .hoge import HogeHogeHoge as hoge
```

Line breaks seperating python import blocks are important,
cause nayvy determines the line where a statement inserted by it.

My own setting is [here](https://gist.github.com/relastle/130f942699f8270c9fec587acbf80f30).
Feel free to copy and paste and use it.


## 4. Feature roadmap

- [x] Auto imports (add and remove) based on pre-defined rules.
- [x] Importing multiple modules using [fzf](https://github.com/junegunn/fzf).
- [x] Touching or jumping to test script.
- [x] Auto generating or jump to test function.
- [x] Generating test functions using [fzf](https://github.com/junegunn/fzf).
- [x] Providing some domain objects useful in creating [ultisnips](https://github.com/SirVer/ultisnips) snippets.
- [x] Providing coc custom source which can insert import statement automatically.
- [ ] Make auto generated Test template configurable. (Now unittest, standard library, is supported)
- [ ] Utility function of converting function arguments to docstring (for UltiSnips).

## 5. Philosophy

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


## 6. Note

#### :construction:

- Please note that any destructive change (backward incompatible) can be done without any announcement.
- This plugin is in a very early stage of development.  Feel free to report problems or submit feature requests in [Issues](https://github.com/relastle/vim-nayvy/issues), or make [PRs](https://github.com/relastle/vim-nayvy/pulls).

## 7. [LICENSE](./LICENSE)

MIT
