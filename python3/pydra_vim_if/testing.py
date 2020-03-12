import sys

import vim  # noqa
from pydra.testing.autogen import AutoGenerator
from pydra.projects.modules.loader import SyntacticModuleLoader


def pydra_auto_touch_test(filepath: str) -> None:
    auto_generator = AutoGenerator(SyntacticModuleLoader())
    test_path = auto_generator.touch_test_file(filepath)
    if test_path is None:
        print(
            'Please check if your python project is created correcty',
            file=sys.stderr,
        )
        return
    vim.command(f'vs {test_path}')
    return


def pydra_jump_to_test_or_generate(
    filepath: str,
    func_name: str,
) -> None:
    auto_generator = AutoGenerator(SyntacticModuleLoader())
    test_path = auto_generator.touch_test_file(filepath)
    if test_path is None:
        print(
            'Please check if your python project is created correcty',
            file=sys.stderr,
        )
        return

    with open(filepath) as f:
        impl_module_lines = f.readlines()

    with open(test_path) as f:
        test_module_lines = f.readlines()

    lines = auto_generator.get_added_test_lines(
        func_name,
        impl_module_lines,
        test_module_lines,
    )

    # open test in split buffer
    vim.command(f'vs {test_path}')

    if lines is None:
        return None

    # change lines
    vim.current.buffer[:] = lines

    # search lines
    row: int
    column: int
    for i, line in enumerate(lines):
        needle = f'def test_{func_name}'
        if needle in line:
            vim.current.window.cursor = (
                i + 1,
                line.index(needle),
            )
    return
