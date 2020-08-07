from typing import Any, Dict, List, Tuple, Optional, Generator
from dataclasses import dataclass

import vim  # noqa
from nayvy.projects.path import (
    ProjectImportHelper,
    ProjectImportHelperBuilder
)
from nayvy.importing.fixer import Fixer, ImportStatementMap
from nayvy.importing.utils import (
    get_first_line_num,
    get_import_block_indices
)
from nayvy.importing.pyflakes import PyflakesEngine
from nayvy.importing.import_config import ImportConfig
from nayvy.projects.modules.loader import SyntacticModuleLoader
from nayvy.importing.import_statement import (
    SingleImport,
    ImportStatement
)
from .utils import error, warning
from .config import IMPORT_PATH_FORMAT


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
        for k, v in self.project_import_helper.items():
            yield k, v

        for k, v in self.import_config.items():
            yield k, v


def init_import_stmt_map(filepath: str) -> Optional[ImportStatementMap]:
    config = ImportConfig.init()
    if config is None:
        error('Cannot load nayvy config file')
        return None
    project_import_helper = ProjectImportHelperBuilder(
        current_filepath=filepath,
        loader=SyntacticModuleLoader(),
        import_path_format=IMPORT_PATH_FORMAT,
        requires_in_pyproject=False,
    ).build()
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


def nayvy_import_stmt(statement: str, level: int) -> None:
    lines = vim.current.buffer[:]

    # get import blocks
    begin_end_indices = get_import_block_indices(lines)

    # get import_statements for each block
    maybe_import_statements_lst = [
        ImportStatement.of_lines(lines[begin_index:end_index])
        for begin_index, end_index in begin_end_indices
    ]

    import_statements_lst = []
    for maybe in maybe_import_statements_lst:
        if maybe is not None:
            import_statements_lst.append(maybe)

    # Constructing import sentence should be added.
    import_stmt_to_add = ImportStatement.of(statement)
    if import_stmt_to_add is None:
        return None

    # constructing import import statements
    if len(import_statements_lst) <= level:
        import_statements_lst.append([import_stmt_to_add])
    else:
        import_statements_lst[level].append(import_stmt_to_add)

    # Merge the imports
    merged_import_statements = [
        ImportStatement.merge_list(import_statements)
        for import_statements in import_statements_lst
    ]

    # Make organized import blocks
    import_lines: List[str] = []
    for i, merged_import_statement in enumerate(
        merged_import_statements
    ):
        for import_statement in merged_import_statement:
            import_lines += import_statement.to_lines()
        if i < len(merged_import_statements) - 1:
            import_lines.append('')

    if not begin_end_indices:
        fitst_line_num = get_first_line_num(lines)
        vim.current.buffer[fitst_line_num:fitst_line_num] = import_lines
    else:
        block_begin_index = begin_end_indices[0][0]
        block_end_index = begin_end_indices[-1][-1]
        vim.current.buffer[block_begin_index:block_end_index] = import_lines
    return


def nayvy_list_imports() -> List[Dict[str, Any]]:
    ''' List all available imports
    '''
    filepath = vim.eval('expand("%")')
    stmt_map = init_import_stmt_map(filepath)
    if stmt_map is None:
        return []
    return [
        single_import.to_dict()
        for _, single_import in stmt_map.items()
    ]


def nayvy_list_import_lines_for_fzf() -> List[str]:
    ''' List all available import list for fzf

    The format will be
    ---
    <import name> : <import statement>

    i.g.) tf : import tensorflow as tf
    ---
    '''
    filepath = vim.eval('expand("%")')
    stmt_map = init_import_stmt_map(filepath)
    if stmt_map is None:
        return []
    return [
        single_import.to_line(color=True)
        for _, single_import in stmt_map.items()
    ]
