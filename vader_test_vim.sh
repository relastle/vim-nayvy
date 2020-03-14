#!/usr/bin/env bash
if [[ ! -e ./vader.vim ]]; then
    git clone https://github.com/junegunn/vader.vim
fi

XDG_CONFIG_HOME="$(pwd)/configs"

vim -Nu <(cat << EOF
filetype off
set rtp+=$(pwd)/vader.vim
set rtp+=$(pwd)
filetype plugin indent on
syntax enable
EOF
) +'Vader! tests/*'
