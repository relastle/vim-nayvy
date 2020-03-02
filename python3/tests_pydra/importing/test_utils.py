import unittest

from pydra.importing.utils import get_import_block_indices


class TestUtils(unittest.TestCase):

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
