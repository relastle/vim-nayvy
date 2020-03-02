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
    return i + 1


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
            ...
            ]
    '''
    res = []
    in_block = False
    start_index = -1
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
            start_index = -1
    if start_index >= 0:
        res.append((start_index, i + 1))
    return res


def find_target_line_num(level: int, lines: List[str]) -> int:
    '''
    Find next line index to
    last import sentence of gien block level.
    In other words, this function returns
    where another additional import sentence to be appneded.
    '''
    if not (0 <= level and level <= 2):
        return -1
    import_block_indices = get_import_block_indices(lines)
    if len(import_block_indices) >= level + 1:
        # already exits target import block
        return import_block_indices[level][1]
    elif len(import_block_indices) == 0:
        # if Any target block does not exist.
        # new import should be added to first line
        target_line = get_first_line_num(lines)
        if len(lines) >= target_line + 1 and lines[target_line] != '':
            lines[target_line:target_line] = ['']
        return target_line
    else:
        # New import block is needed.
        # So create new block and add new import sentence
        target_line = import_block_indices[-1][1]
        lines[target_line:target_line] = ['']
        return target_line + 1
