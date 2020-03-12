import sys
from typing import List, Optional

import vim  # noqa
from pydra.importing.fixer import Fixer
from pydra.importing.pyflakes import PyflakesEngine
from pydra.importing.import_config import ImportConfig


def init_config() -> Optional[ImportConfig]:
    config = ImportConfig.init()
    if config is None:
        print('cannot load pydra config file', file=sys.stderr)
        return None
    return config


def pydra_fix_lines(lines: List[str]) -> List[str]:
    config = init_config()
    if config is None:
        return lines
    fixer = Fixer(config, PyflakesEngine())
    fixed_lines = fixer.fix_lines(lines)
    return fixed_lines


def pydra_auto_imports() -> None:
    '''
    Automatically
    - import for undefined names
    - remove unused imports
    '''
    lines = vim.current.buffer[:]
    fixed_lines = pydra_fix_lines(lines)
    vim.current.buffer[:] = fixed_lines
    return


def pydra_get_fixed_lines(buffer_nr: int) -> List[str]:
    lines = vim.buffers[buffer_nr][:]
    return pydra_fix_lines(lines)


def pydra_import(names: List[str]) -> None:
    config = init_config()
    if config is None:
        return None
    fixer = Fixer(config, PyflakesEngine())
    lines = vim.current.buffer[:]
    fixed_lines = fixer.add_imports(lines, names)
    vim.current.buffer[:] = fixed_lines
    return


def pydra_list_imports() -> List[str]:
    ''' List all available imports
    '''
    config = init_config()
    if config is None:
        return []
    return [
        '{}:{}'.format(
            single_import.name,
            single_import.sentence,
        ) for name, single_import in config.import_d.items()
    ]