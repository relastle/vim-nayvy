from typing import List, Tuple, Optional
from os.path import basename
from dataclasses import dataclass

import vim  # noqa
from nayvy.testing.path import is_test_path, test_path_to_impl_path
from nayvy.testing.autogen import AutoGenerator
from nayvy.projects.modules.loader import SyntacticModuleLoader
from .utils import error


@dataclass(frozen=True)
class VimWin:

    tabnr: int
    winnr: int
    bufnr: int
    abs_path: str

    def get_lines(self) -> List[str]:
        return vim.buffers[self.bufnr][:]

    @classmethod
    def get_list(cls) -> List['VimWin']:
        wins = vim.eval('getwininfo()')
        return [
            VimWin(
                win['tabnr'],
                win['winnr'],
                win['bufnr'],
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


def nayvy_auto_touch_test() -> None:
    """ Vim interface for touch unittest script.
    """
    filepath = vim.eval('expand("%")')
    if is_test_path(filepath):
        error('You are already in test script.')
        return
    auto_generator = AutoGenerator(SyntacticModuleLoader())
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
    filepath = vim.eval('expand("%")')
    if not func_names and is_test_path(filepath):
        # Nothing should be done when already in a test buffer
        # and function names were not provided.
        error('You are already in test script.')
        return
    loader = SyntacticModuleLoader()
    auto_generator = AutoGenerator(loader)
    if is_test_path(filepath):
        # if current buffer is test file
        test_path = filepath
        impl_path = test_path_to_impl_path(test_path)
        if impl_path is None:
            error('Please check if your python project is created correcty')
            return
    else:
        # if current buffer is impl file
        impl_path = filepath
        test_path = auto_generator.touch_test_file(filepath)
        if test_path is None:
            error('Please check if your python project is created correcty')
            return
        impl_module_lines = vim.current.buffer[:]
        impl_mod = loader.load_module_from_lines(impl_module_lines)
        if impl_mod is None:
            error('Please check the current buffer is valid')
            return

        if func_names == []:
            # if `func_names` is not given, infer it as nearest function
            func_name = impl_mod.get_nearest_function(
                vim.current.window.cursor[0]-1)
            if func_name is None:
                error('The cursor is probably outside the function.')
                return
            func_names = [func_name]

        # load test file lines.
        test_win = VimWin.find_win(test_path)
        if not test_win:
            with open(test_path) as f:
                test_module_lines = [
                    line.strip('\n') for line in f.readlines()
                ]
        else:
            test_module_lines = test_win.get_lines()

        for func_name in func_names:
            tmp = auto_generator.get_added_test_lines(
                func_name,
                impl_module_lines,
                test_module_lines,
            )
            if tmp is not None:
                test_module_lines = tmp

        # open test script
        if not test_win:
            vim.command(f'vs {test_path}')
        else:
            vim.execute('{} tabnext'.format(
                test_win.tabnr
            ))
            vim.execute('{} wincmd w'.format(
                test_win.winnr
            ))

        if test_module_lines is not None:
            # change lines
            vim.current.buffer[:] = test_module_lines
        else:
            print('Test function already exists')

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
    if basename(filepath).startswith('test_'):
        error('You are already in test script.')
        return None
    lines = vim.current.buffer[:]
    loader = SyntacticModuleLoader()
    auto_generator = AutoGenerator(loader)
    test_path = auto_generator.touch_test_file(filepath)
    if test_path is None:
        error('Please check if your python project is created correcty')
        return ([], [])

    impl_mod = loader.load_module_from_lines(lines)
    test_mod = loader.load_module_from_path(test_path)
    if impl_mod is None or test_mod is None:
        error('Loading python scripts failed.')
        return ([], [])
    intersection = impl_mod.to_test().intersect(test_mod)
    subtraction = impl_mod.to_test().sub(test_mod)
    return (
        intersection.to_func_list_lines(),
        subtraction.to_func_list_lines(),
    )
