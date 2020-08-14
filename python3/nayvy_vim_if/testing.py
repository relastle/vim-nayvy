from typing import List, Tuple, Optional
from os.path import exists, abspath
from dataclasses import dataclass

import vim  # noqa
from nayvy.testing.path import (
    is_test_path,
    impl_path_to_test_path,
    test_path_to_impl_path
)
from nayvy.projects.modules.loader import SyntacticModuleLoader
from nayvy.testing.autogen import AutoGenerator
from nayvy.projects import get_pyproject_root
from .utils import info, error
from .config import CONFIG


@dataclass(frozen=True)
class VimWin:

    tabnr: int
    winnr: int
    bufnr: int
    abs_path: str

    def get_lines(self) -> List[str]:
        return vim.buffers[self.bufnr][:]  # type: ignore

    @classmethod
    def get_list(cls) -> List['VimWin']:
        wins = vim.eval('getwininfo()')
        return [
            VimWin(
                int(win['tabnr']),
                int(win['winnr']),
                int(win['bufnr']),
                vim.eval('expand("{}{}{}")'.format(
                    '#',
                    win['bufnr'],
                    ':p',
                ))
            ) for win in wins
        ]

    @classmethod
    def find_win(cls, filepath: str) -> Optional['VimWin']:
        wins = cls.get_list()
        win_d = {win.abs_path: win for win in wins}
        return win_d.get(filepath, None)


def get_impl_and_test_paths(filepath: str) -> Optional[Tuple[str, str]]:
    """ check if filepath is a test script and return `impl` and `test` path
    """
    abs_filepath = abspath(filepath)
    pyproject_root = get_pyproject_root(abs_filepath, CONFIG.pyproject_root_markers)
    if pyproject_root is None:
        return None
    if is_test_path(filepath):
        test_path = abspath(filepath)
        maybe_impl_path = test_path_to_impl_path(filepath, pyproject_root)
        if maybe_impl_path is None:
            return None
        return (
            maybe_impl_path,
            test_path,
        )
    else:
        impl_path = abspath(filepath)
        maybe_test_path = impl_path_to_test_path(filepath, pyproject_root)
        if maybe_test_path is None:
            return None
        return (
            impl_path,
            maybe_test_path,
        )


def get_latest_lines(filepath: str) -> List[str]:
    """
    If `filepath` is opend, return content of buffer,
    or read filepath.
    """
    win = VimWin.find_win(filepath)
    if not win:
        if not exists(filepath):
            return []
        with open(filepath) as f:
            lines = [
                line.strip('\n') for line in f.readlines()
            ]
        return lines
    else:
        return win.get_lines()


def nayvy_auto_touch_test() -> None:
    """ Vim interface for touch unittest script.
    """
    filepath = vim.eval('expand("%")')
    if is_test_path(filepath):
        error('You are already in test script.')
        return
    auto_generator = AutoGenerator(
        SyntacticModuleLoader(),
        CONFIG.pyproject_root_markers,
    )
    test_path = auto_generator.touch_test_file(filepath)
    if test_path is None:
        error('Please check if your python project is created correcty')
        return
    vim.command(f'vs {test_path}')
    return


def nayvy_test_generate_multiple(fzf_selected_lines: List[str]) -> None:
    func_names = [
        line.split('::')[1].strip().lstrip('test_')
        for line in fzf_selected_lines
    ]
    return nayvy_test_generate(func_names)


def nayvy_test_generate(func_names: List[str] = []) -> None:
    """ Vim interface for jumping or generating unittest.
    """
    loader = SyntacticModuleLoader()
    auto_generator = AutoGenerator(
        loader,
        CONFIG.pyproject_root_markers,
    )
    filepath = vim.eval('expand("%")')
    if not func_names and is_test_path(filepath):
        # Nothing should be done when already in a test buffer
        # and function names were not provided.
        error('You are already in test script.')
        return
    impl_test_paths = get_impl_and_test_paths(filepath)
    if impl_test_paths is None:
        error('Please check if your python project is created correcty')
        return

    impl_path, test_path = impl_test_paths
    auto_generator.touch_test_file(impl_path)
    impl_module_lines = get_latest_lines(impl_path)
    test_module_lines = get_latest_lines(test_path)

    if func_names == []:
        impl_mod = loader.load_module_from_lines(impl_module_lines)
        if impl_mod is None:
            error('Please check the current buffer is valid')
            return
        # if `func_names` is not given, infer it as nearest function
        func = impl_mod.get_nearest_function(vim.current.window.cursor[0] - 1)
        if func is None:
            error('The cursor is probably outside the function.')
            return
        func_names = [func.name]

    updated_test_module_lines = test_module_lines
    for func_name in func_names:
        may_updated_test_module_lines = auto_generator.get_added_test_lines(
            func_name,
            impl_module_lines,
            updated_test_module_lines,
        )
        if may_updated_test_module_lines:
            updated_test_module_lines = may_updated_test_module_lines

    test_win = VimWin.find_win(test_path)
    # open test script
    if not test_win:
        vim.command(f'vs {test_path}')
    else:
        vim.command('{} tabnext'.format(
            test_win.tabnr
        ))
        vim.command('{} wincmd w'.format(
            test_win.winnr
        ))

    if updated_test_module_lines is not None:
        # change lines
        vim.current.buffer[:] = updated_test_module_lines
    else:
        info('Test function already exists')

    # search lines
    row: int
    column: int
    for i, line in enumerate(test_module_lines):
        needle = f'def test_{func_name}'
        if needle in line:
            vim.current.window.cursor = (
                i + 1,
                line.index(needle),
            )
    return


def nayvy_list_tested_and_untested_functions() -> Optional[Tuple[List[str], List[str]]]:
    """ Vim interface for listing up
    - Already tested function
    - Non-tested function
    """
    filepath = vim.eval('expand("%")')
    loader = SyntacticModuleLoader()
    impl_test_paths = get_impl_and_test_paths(filepath)
    if impl_test_paths is None:
        error('Please check if your python project is created correcty')
        return ([], [])

    impl_path, test_path = impl_test_paths
    # get lines
    impl_module_lines = get_latest_lines(impl_path)
    test_module_lines = get_latest_lines(test_path)

    # create module objects
    impl_mod = loader.load_module_from_lines(impl_module_lines)
    test_mod = loader.load_module_from_lines(test_module_lines)
    if impl_mod is None or test_mod is None:
        error('Loading python scripts failed.')
        return ([], [])
    intersection = impl_mod.to_test().intersect(test_mod)
    subtraction = impl_mod.to_test().sub(test_mod)
    return (
        intersection.to_func_list_lines(),
        subtraction.to_func_list_lines(),
    )
