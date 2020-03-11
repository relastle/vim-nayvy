import sys

import vim  # noqa
from pydra.testing.autogen import AutoGenerator


def pydra_auto_touch_test(filepath: str) -> None:
    auto_generator = AutoGenerator()
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
    cword: str,
) -> None:
    auto_generator = AutoGenerator()
    test_path = auto_generator.touch_test_file(filepath)
    if test_path is None:
        print(
            'Please check if your python project is created correcty',
            file=sys.stderr,
        )
        return

    lines = auto_generator.get_added_test_lines(
        cword,
        filepath,
        test_path,
    )

    if lines is None:
        print(
            'Please check any obvious error occurs in your scripts',
            file=sys.stderr,
        )
        return None
    # open test in split buffer
    vim.command(f'vs {test_path}')

    # change lines
    vim.current.buffer[:] = lines

    # search lines
    row: int
    column: int
    for i, line in enumerate(lines):
        needle = f'def test_{cword}'
        if needle in line:
            vim.current.buffer.cursor = (
                i,
                line.index(needle),
            )
    return
