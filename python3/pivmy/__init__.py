import os
import sys
import string
import inspect
from enum import Enum
from typing import Any, List, Type, TypeVar, Optional

import vim  # noqa
from nayvy.projects.path import ImportPathFormat
from nayvy.importing.fixer import LinterForFix

T = TypeVar('T', bound='BaseConfig')


def camel_to_snake(s: str) -> str:
    res = ''.join(
        f'_{c.lower()}' if c in string.ascii_uppercase else c
        for i, c in enumerate(s)
    ).lstrip('_')
    return res


class ConfigVar:

    base_name: str
    field_name: str

    @property
    def vim_variable_name(self) -> str:
        return f'{self.base_name}_{self.field_name}'

    @property
    def vim_variable_value(self) -> Any:
        return vim.vars.get(self.vim_variable_name)  # type: ignore

    @property
    def env_variable_name(self) -> str:
        return f'{self.base_name.upper()}_{self.field_name.upper()}'

    @property
    def env_variable_value(self) -> Optional[str]:
        return os.environ.get(self.env_variable_name)

    def __init__(self, base_name: str, field_name: str) -> None:
        self.base_name = base_name
        self.field_name = field_name


def _from_vim_config_int(
    config_var: ConfigVar,
    default: int,
) -> int:
    """ env/vim -> config IF for int.
    """
    if config_var.env_variable_value:
        try:
            var = int(config_var.env_variable_value)
        except Exception:
            print(f'[Nayvy Error] Environment Variable {config_var.env_variable_name} should be interger', file=sys.stderr)  # noqa
            return default
        return var

    if config_var.vim_variable_value:
        try:
            var = int(config_var.vim_variable_value)
        except Exception:
            print(f'[Nayvy Error] Global Variable g:{config_var.vim_variable_name} should be interger', file=sys.stderr)  # noqa
            return default
        return var
    return default


def _from_vim_config_int_list(
    config_var: ConfigVar,
    default: List[int],
) -> List[int]:
    """ env/vim -> config IF for List[int].
    """
    if config_var.env_variable_value:
        try:
            var = list(map(int, config_var.env_variable_value.split(',')))
        except Exception:
            print(f'[Nayvy Error] Environment Variable {config_var.env_variable_name} should be comma separeted integer list', file=sys.stderr)  # noqa
            return default
        return var

    if config_var.vim_variable_value:
        try:
            var = config_var.vim_variable_value
            assert all(isinstance(i, int) for i in var)
        except Exception:
            print(f'[Nayvy Error] Global Variable g:{config_var.vim_variable_name} should be list of interger', file=sys.stderr)  # noqa
            return default
        return var
    return default


def _from_vim_config_str(
    config_var: ConfigVar,
    default: str,
) -> str:
    """ env/vim -> config IF for int.
    """
    if config_var.env_variable_value:
        return config_var.env_variable_value

    if config_var.vim_variable_value:
        return str(config_var.vim_variable_value)
    return default


def _from_vim_config_str_list(
    config_var: ConfigVar,
    default: List[str],
) -> List[str]:
    """ env/vim -> config IF for List[str].
    """
    if config_var.env_variable_value:
        try:
            var = list(map(str, config_var.env_variable_value.split(',')))
        except Exception:
            print(f'[Nayvy Error] Environment Variable {config_var.env_variable_name} should be comma separeted string list', file=sys.stderr)  # noqa
            return default
        return var

    if config_var.vim_variable_value:
        try:
            var = config_var.vim_variable_value
            assert isinstance(var, list)
            assert all(isinstance(s, str) for s in var)
        except Exception:
            print(f'[Nayvy Error] Global Variable g:{config_var.vim_variable_name} should be list of string', file=sys.stderr)  # noqa
            return default
        return var
    return default


def _from_vim_config_enum(
    config_var: ConfigVar,
    t: Type[Enum],
    default: Enum,
) -> Enum:
    """ env/vim -> config IF for ENUM.
    """
    if config_var.env_variable_value:
        try:
            enum = t(config_var.env_variable_value)
        except Exception:
            print(f'[Nayvy Error] Environment Variable {config_var.env_variable_name} should be either in {[e.value for e in t]}', file=sys.stderr)  # noqa
            return default
        return enum

    if config_var.vim_variable_value:
        try:
            enum = t(config_var.vim_variable_value)
        except Exception:
            print(f'[Nayvy Error] Global Variable g:{config_var.vim_variable_name} should be either in {[e.value for e in t]}', file=sys.stderr)  # noqa
            return default
        return enum
    return default


class BaseConfig:

    import_path_format: ImportPathFormat = ImportPathFormat.ALL_RELATIVE
    linter_for_fix: LinterForFix = LinterForFix.RUFF
    pyproject_root_markers: List[str] = ['pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt']  # noqa

    @classmethod
    def new(cls: Type[T], base_name: str) -> T:
        """
        Get configurable variable from

        1) Project specific environment variable (export XXX_XXX='xyz')
        2) Vim script global variable (let g:xxx_xxx='xyz')
        """
        config = cls()
        for field_name, t in cls.__annotations__.items():
            config_var = ConfigVar(
                base_name=base_name,
                field_name=field_name,
            )
            try:
                default_value = getattr(cls, field_name)
            except Exception:
                print('Failed to get default value', file=sys.stderr)
                continue
            if inspect.isclass(t):
                if t == int:
                    setattr(config, field_name, _from_vim_config_int(
                        config_var,
                        default_value,
                    ))
                elif t == str:
                    setattr(config, field_name, _from_vim_config_str(
                        config_var,
                        default_value,
                    ))
                elif issubclass(t, Enum):
                    setattr(config, field_name, _from_vim_config_enum(
                        config_var,
                        t,
                        default_value,
                    ))
            elif t == List[str]:
                setattr(config, field_name, _from_vim_config_str_list(
                    config_var,
                    default_value,
                ))
            elif t == List[int]:
                setattr(config, field_name, _from_vim_config_int_list(
                    config_var,
                    default_value,
                ))
        return config
