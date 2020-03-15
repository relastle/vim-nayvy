# vim-nayvy

Enriching python coding.

<p align="center">
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/v/nayvy?color=%23032794"/></a>
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/l/nayvy?color=032794"/></a>
<a href="https://pypi.org/project/nayvy/"><img src="https://img.shields.io/pypi/pyversions/nayvy?color=032794"/></a>
</p>

<p align="center">
<a href="https://github.com/relastle/vim-nayvy/actions"><img src="https://github.com/relastle/vim-nayvy/workflows/pythontests/badge.svg"/></a>
</p>


## Installation

Using [vim-plug](https://github.com/junegunn/vim-plug)

```vim
Plug 'relastle/vim-nayvy'
```

## Usage

Please refer [doc](./doc/vim-nayvy.txt) for full documentation.
Some demonstrations are shown here.


### NayvyImports

![nayvy_imports](https://user-images.githubusercontent.com/6816040/76696704-9576a480-66d1-11ea-9561-b08914e263f4.gif)

### NayvyImportFZF

![nayvy_import_fzf](https://user-images.githubusercontent.com/6816040/76696705-9ad3ef00-66d1-11ea-9d7c-cf62b7f597c0.gif)

### NayvyTestGenerate

:construction:

### NayvyTestGenerateFZF

:construction:

## Feature roadmap

- [x] Auto imports (add and remove) based on pre-defined rules.
- [x] Importing multiple modules using [fzf](https://github.com/junegunn/fzf).
- [x] Touching or jumping to test script.
- [x] Auto generating or jump to test function.
- [x] Generating test functions using [fzf](https://github.com/junegunn/fzf).
- [x] Providing some domain objects useful in creating [ultisnips](https://github.com/SirVer/ultisnips) snippets.

## Philosophy

Most python code parsing algorithms of `vim-nayvy` is not strict, and it contains some heuristics
( In other words, it is not based on AST, or hierarchical module structure).
However, it is intentional. I personally think the heuristics works well for most real-world usecases,
and has benefit in terms of performance.
The strategy is also robust against partially broken codes.
Some code actions (such as implementing test function and jumping) should be executable
when python code in current buffer is incomplete (cannot parsed via AST, or unimportable by `importlib`).

Now, it is the era of [LSP](https://microsoft.github.io/language-server-protocol).
I do not think prividing aid for code completioon is demanded, cause I personally think code completion
is one of the most powerful and stable features privided by LSP.
Thus, the main aim of `vim-nayvy` is providing a little bit utility functions :smile:


## Note

:construction: Please note that any destructive change (backward incompatible) can be done without any announcement.

## [LICENSE](./LICENSE)

MIT
