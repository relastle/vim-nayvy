#!/usr/bin/env bash
if [[ ! -e ./_vader.vim ]]; then
    git clone https://github.com/junegunn/vader.vim ./ _vader.vim
fi

if [[ ! -e ./_ultisnips ]]; then
    git clone https://github.com/SirVer/ultisnips ./_ultisnips
fi

XDG_CONFIG_HOME="$(pwd)/configs"

nvim -Es -u <(cat << EOF
filetype off
set rtp+=$(pwd)/_vader.vim
set rtp+=$(pwd)/_ultisnips
set rtp+=$(pwd)
filetype plugin indent on
syntax enable
EOF
) -c 'Vader! tests/*'
