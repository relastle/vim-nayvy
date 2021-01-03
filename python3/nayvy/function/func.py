"""
utility for functions
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from nayvy.function.arg import Arg


@dataclass
class Func:
    name: str
    args: List[Arg]
    return_type: str
    indent: int


FUNC_REG_EXP = re.compile(r'(?P<indent>{})(?P<async>{})(?P<def>{})(?P<function_name>{})(?P<args>{})(?P<return_arrow>{})(?P<return_type>{}):'.format(  # noqa
    r' *',
    r'(async +){0,1}',
    r'def +',
    r'\w+ *',
    r'\((?P<args_str>.*)\) *',
    r'-\> *',
    r'.* *',
))


def parse_function_line(line: str) -> Optional[Func]:
    m = FUNC_REG_EXP.match(line)
    if not m:
        return None

    name = m.group('function_name')
    args = Arg.parse_args(m.group('args_str'))
    return_type = m.group('return_type')
    indent = len(m.group('indent'))

    return Func(name, args, return_type, indent)


def is_func_decl_start_line(line: str) -> bool:
    return re.match(r'(?P<indent> *)((async +){0,1})def \w+ *\(.*', line) is not None


def get_current_func(lines: List[str], current_line_index: int) -> Optional[Func]:
    """
    Get Func objects of the current focused function.

    Strategy overview:
        start of a function         : `line that starts with def .*`
        end of argument declaration : `matched parentheses: ()`
        start of return type        : `->`
        end of function             : `line that starts with :`
    """

    # find the start of function
    line_index = current_line_index
    function_start_index = None
    while (0 <= line_index < len(lines)):
        line = lines[line_index]
        if is_func_decl_start_line(line):
            function_start_index = line_index
            break
        line_index -= 1
    if function_start_index is None:
        return None

    func_str = ''
    for line in lines[function_start_index:]:
        line = line.rstrip()
        func_str += line
        if line.endswith(':'):
            break

    return parse_function_line(func_str)
