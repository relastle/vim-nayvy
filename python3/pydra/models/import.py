'''
Module for manipulating import statements
generally defiend in top of the script.
'''
from typing import List, Tuple


def get_first_line_num(lines: List[str]) -> int:
    '''
    Return first python code line line line number(0-based)
    except for module DocString(__doc__)
    and shebang (#!/usr/bin/env python3)
    '''
    in_docstring = False
    try:
        for i, line in enumerate(lines):
            if in_docstring and line.startswith("'''"):
                in_docstring = False
                continue
            if (not in_docstring) and line.startswith("'''"):
                in_docstring = True
                continue
            if line.startswith('#'):
                continue
            if not in_docstring:
                return i
    except Exception:
        return 0
    return i


def already_exists(sentence: str, lines: List[str]) -> bool:
    '''
    Check if sentence is in lines
    '''
    return any(sentence in line.strip() for line in lines)


def get_import_block_indices(lines: List[str]) -> List[Tuple[int, int]]:
    '''
    Returns:
        [
            (1st block's start begin(inclusive), 1st block's end(exclusive)),
            (2nd block's start begin(inclusive), 2nd block's end(exclusive)),
            (3rd block's start begin(inclusive), 3rd block's end(exclusive)),
            ]
    '''
    res = []
    in_block = False
    try:
        for i, line in enumerate(lines):
            if (
                not in_block and
                (
                    line.startswith('import ') or
                    line.startswith('from ')
                )
            ):
                in_block = True
                start_index = i
                continue
            elif in_block and line == '':
                in_block = False
                res.append((start_index, i))
    except Exception:
        return res
    return res


def find_target_line_num(level: int, lines: List[str]) -> int:
    '''
    import文を探して、与えられたlevelのblockの最後の
    import文の次の行番号を返す(0-based-index)
    level:
        0 (標準ライブラリのimport)
        1 (third-partyライブラリのimport)
        2 (相対パスでのimportなどなど)
    '''
    if not (0 <= level and level <= 2):
        return -1
    import_block_indices = get_import_block_indices(buf)
    if len(import_block_indices) >= level + 1:
        # このときは素直に行挿入すればよい
        return import_block_indices[level][1]
    elif len(import_block_indices) == 0:
        # ブロックがそもそもないときは
        # コメントを抜かした一番上にimportするのがよい
        target_line = get_first_line_num(buf)
        if len(buf) >= target_line + 1 and buf[target_line] != '':
            buf[target_line:target_line] = ['']
        return target_line
    else:
        # 所与のブロックは見つからなかったがいくらかはあるとき
        # 存在しているブロックに空行付け加えて
        # 対処するのがよい
        target_line = import_block_indices[-1][1]
        buf[target_line:target_line] = ['']
        return target_line + 1


def auto_import(sentence, level):
    # すでにimportされているかチェックする
    if already_exists(sentence, snip.buffer):
        return
    target_line = find_target_line_num(level, snip.buffer)

    # どこにimport文を挿入するべきかわからなかった場合は何もしない
    if target_line < 0:
        return
    snip.buffer[target_line:target_line] = [sentence]
    return
