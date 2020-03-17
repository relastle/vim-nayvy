#!/usr/bin/env bash
if [[ ! -e ./vader.vim ]]; then
    git clone https://github.com/junegunn/_vader.vim
fi

if [[ ! -e ./ultisnips ]]; then
    git clone https://github.com/SirVer/_ultisnips
fi

XDG_CONFIG_HOME="$(pwd)/configs"

vim -Nu <(cat << EOF
filetype off
set rtp+=$(pwd)/_vader.vim
set rtp+=$(pwd)/_ultisnips
set rtp+=$(pwd)
filetype plugin indent on
syntax enable
EOF
) +'Vader! tests/*'
