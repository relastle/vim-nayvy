#!/usr/bin/env bash
if [[ ! -e ./_vader.vim ]]; then
    git clone https://github.com/junegunn/vader.vim ./_vader.vim
fi

if [[ ! -e ./_ultisnips ]]; then
    git clone https://github.com/SirVer/ultisnips ./_ultisnips
fi

export XDG_CONFIG_HOME="$(pwd)/configs"

vim -Nu <(cat << EOF
filetype off
set rtp+=$(pwd)/_vader.vim
set rtp+=$(pwd)/_ultisnips
set rtp+=$(pwd)
let g:UltiSnipsSnippetDirectories = ['__UltiSnips']
filetype plugin indent on
syntax enable
EOF
) +'Vader! tests/*'
