import unittest

from pydra.importing.utils import (
    get_first_line_num,
    get_import_block_indices,
    find_target_line_num,
)


class Test(unittest.TestCase):

    def test_get_first_line_num(self) -> None:
        given = [
            '#!/usr/bin/env python3',
            "''' one line docstring surrounded by single quotes",
            "'''",
            '',
        ]

        assert get_first_line_num(given) == 3

        given = [
            '#!/usr/bin/env python3',
            '"""',
            'Multi line docstring surrounded by double quotes',
            '"""',
            '',
        ]

        assert get_first_line_num(given) == 4
        return

    def test_get_import_block_indices(self) -> None:
        # -------------------------------------
        # natural three blocks
        # -------------------------------------
        input_lines = [
            '#!/usr/bin/env python3',
            'from typing import List',
            '',
            'import numpy as np',
            '',
            'from .hoge import Hoge'
        ]
        begin_end_indices = get_import_block_indices(input_lines)
        assert len(begin_end_indices) == 3
        assert begin_end_indices[0] == (1, 2)
        assert begin_end_indices[1] == (3, 4)
        assert begin_end_indices[2] == (5, 6)

        # -------------------------------------
        # docstring ignored
        # -------------------------------------
        input_lines = [
            '#!/usr/bin/env python3',
            "'''",
            'this is a docstring',
            "'''",
            'from typing import List',
            'from typing import Dict',
            ''
        ]
        begin_end_indices = get_import_block_indices(input_lines)
        assert len(begin_end_indices) == 1
        assert begin_end_indices[0] == (4, 6)

        # -------------------------------------
        # Non new-line seperated block and codes
        # -------------------------------------
        input_lines = [
            '#!/usr/bin/env python3',
            'from typing import List',
            'def main() -> None:',
            '    pass',
        ]
        begin_end_indices = get_import_block_indices(input_lines)
        assert len(begin_end_indices) == 1
        assert begin_end_indices[0] == (1, 2)
        return

    def test_find_target_line_num(self) -> None:
        given = [
            '#!/usr/bin/env python3',
            '""" some docstring',
            '"""',
            '',
            'import os',
            'import sys',
            '',
            'import numpy as np',
            '',
        ]

        assert find_target_line_num(0, given) == 6
        assert find_target_line_num(1, given) == 8
        assert find_target_line_num(2, given) == 9
        return
