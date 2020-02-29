#!/usr/bin/env bash
if [[ ! -e ./vader.vim ]]; then
    git clone https://github.com/junegunn/vader.vim
fi

export XDG_CONFIG_HOME="$(pwd)/configs/pydra"

nvim -Es -u <(cat << EOF
filetype off
set rtp+=$(pwd)/vader.vim
set rtp+=$(pwd)
filetype plugin indent on
syntax enable
EOF) -c 'Vader! tests/*'
