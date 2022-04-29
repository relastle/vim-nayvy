#!/usr/bin/env bash
if [[ ! -e ./_vader.vim ]]; then
    git clone https://github.com/junegunn/vader.vim ./_vader.vim
fi

if [[ ! -e ./_ultisnips ]]; then
    git clone https://github.com/SirVer/ultisnips ./_ultisnips
fi

export XDG_CONFIG_HOME="$(pwd)/configs"

nvim -Es -u <(cat << EOF
filetype off
set runtimepath+=$(pwd)/_vader.vim
set runtimepath+=$(pwd)/_ultisnips
set runtimepath+=$(pwd)
let g:UltiSnipsSnippetDirectories = ['__UltiSnips']
filetype plugin indent on
syntax enable
EOF
) -c 'Vader! tests/*'
