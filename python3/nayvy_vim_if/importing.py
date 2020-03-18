from typing import List, Optional, Tuple, Any, Generator
from dataclasses import dataclass

import vim  # noqa

from .utils import error, warning
from nayvy.importing.fixer import Fixer, ImportStatementMap
from nayvy.importing.import_statement import SingleImport
from nayvy.importing.pyflakes import PyflakesEngine
from nayvy.importing.import_config import ImportConfig
from nayvy.projects.modules.loader import SyntacticModuleLoader
from nayvy.projects.path import ProjectImportHelper


@dataclass(frozen=True)
class IntegratedMap(ImportStatementMap):

    import_config: ImportConfig
    project_import_helper: ProjectImportHelper

    def __getitem__(self, name: str) -> Optional[SingleImport]:
        single_import = self.project_import_helper[name]
        if single_import is not None:
            return single_import
        single_import = self.import_config[name]
        if single_import is not None:
            return single_import
        return None

    def items(self) -> Generator[Tuple[str, SingleImport], Any, Any]:
        for k, v in self.import_config.items():
            yield k, v

        for k, v in self.project_import_helper.items():
            yield k, v


def init_import_stmt_map(filepath: str) -> Optional[ImportStatementMap]:
    config = ImportConfig.init()
    if config is None:
        error('Cannot load nayvy config file')
        return None
    project_import_helper = ProjectImportHelper.of_filepath(
        SyntacticModuleLoader(),
        filepath,
    )
    if project_import_helper is None:
        warning(
            'cannot load project. '
            '(check if the current buffer is saved correctly, '
            'or you are working in a Python project)'
        )
        return config
    return IntegratedMap(
        config,
        project_import_helper,
    )


def nayvy_fix_lines(lines: List[str]) -> Optional[List[str]]:
    filepath = vim.eval('expand("%")')
    stmt_map = init_import_stmt_map(filepath)
    if stmt_map is None:
        return lines
    fixer = Fixer(stmt_map, PyflakesEngine())
    fixed_lines = fixer.fix_lines(lines)
    return fixed_lines


def nayvy_auto_imports() -> None:
    '''
    Automatically
    - import for undefined names
    - remove unused imports
    '''
    lines = vim.current.buffer[:]
    fixed_lines = nayvy_fix_lines(lines)
    if fixed_lines:
        # update only if fixed_lines is not None
        vim.current.buffer[:] = fixed_lines
    return


def nayvy_get_fixed_lines(buffer_nr: int) -> Optional[List[str]]:
    """ Get fixed lines of importing fixed.

    Used mainly as the fixer of ALE.
    """
    lines = vim.buffers[buffer_nr][:]
    return nayvy_fix_lines(lines)


def nayvy_import(names: List[str]) -> None:
    filepath = vim.eval('expand("%")')
    stmt_map = init_import_stmt_map(filepath)
    if stmt_map is None:
        return None
    fixer = Fixer(stmt_map, PyflakesEngine())
    lines = vim.current.buffer[:]
    fixed_lines = fixer.add_imports(lines, names)
    vim.current.buffer[:] = fixed_lines
    return


def nayvy_list_imports() -> List[str]:
    ''' List all available imports
    '''
    filepath = vim.eval('expand("%")')
    stmt_map = init_import_stmt_map(filepath)
    if stmt_map is None:
        return []
    return [
        single_import.to_line(color=True)
        for _, single_import in stmt_map.items()
    ]
