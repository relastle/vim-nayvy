
import os
import sys
import string
from enum import Enum
from typing import Type, TypeVar

import vim  # noqa
from nayvy.projects.path import ImportPathFormat
from nayvy.importing.fixer import LinterForFix

BASE_NAME = 'nayvy'

T = TypeVar('T')


def camel_to_snake(s: str) -> str:
    res = ''.join(
        f'_{c.lower()}' if c in string.ascii_uppercase else c
        for i, c in enumerate(s)
    ).lstrip('_')
    return res


def _from_vim_config(
    base_name: str,
    t: Type[Enum],
    default: Enum,
) -> Enum:
    # get expected name of vim/environment variable name.
    class_name = t.__name__
    snake_class_name = camel_to_snake(class_name)
    vim_variable_name = f'{base_name}_{snake_class_name}'
    env_variable_name = f'{base_name.upper()}_{snake_class_name.upper()}'

    # Environment variable check.
    env_value = os.environ.get(env_variable_name)
    if env_value:
        try:
            enum = t(env_value)
        except Exception:
            print(f'[Nayvy Error] Environment Variable {env_variable_name} should be either in {[e.value for e in t]}', file=sys.stderr)  # noqa
            return default
        return enum

    # Vim script variable check.
    vim_value = vim.vars.get(vim_variable_name)
    if vim_value:
        try:
            enum = t(vim_value)
        except Exception:
            print(f'[Nayvy Error] Global Variable g:{vim_variable_name} should be either in {[e.value for e in t]}', file=sys.stderr)  # noqa
            return default
        return enum
    return default


def from_vim_config(
    base_name: str,
    t: Type[T],
    default: T,
) -> T:
    if issubclass(t, Enum):
        return _from_vim_config(base_name, t, default)  # type: ignore
    return default


IMPORT_PATH_FORMAT = from_vim_config(
    BASE_NAME,
    ImportPathFormat,
    ImportPathFormat.ALL_RELATIVE,
)

LINTER_FOR_FIX = from_vim_config(
    BASE_NAME,
    LinterForFix,
    LinterForFix.PYFLAKES,
)
