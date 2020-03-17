"""
Utility function for ultisnips
"""

from typing import Iterable, List, Any

from nayvy.importing.utils import (
    already_exists,
    find_target_line_num,
)


def buf2lines(buf: Iterable[str]) -> List[str]:
    """
    Hacky functions for Ultisnips lines into normal list of str.
    """
    lines = []
    try:
        for i, line in enumerate(buf):
            lines.append(line)
    except Exception:
        return lines
    return lines


def auto_import(snip: Any, sentence: str, level: int) -> None:
    """ Hookable funciton for auto-importing when snippet expansion
    """
    lines = buf2lines(snip.buffer)
    # すでにimportされているかチェックする
    if already_exists(sentence, lines):
        return
    target_line = find_target_line_num(level, lines)

    # どこにimport文を挿入するべきかわからなかった場合は何もしない
    if target_line < 0:
        return
    snip.buffer[target_line:target_line] = [sentence]
    return
