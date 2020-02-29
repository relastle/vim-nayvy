import unittest

from pydra.importing.fixer import Fixer, Flake8Result
from pydra.importing.import_config import ImportConfig, SingleImport


class TestFlake8Result(unittest.TestCase):

    def test_of_line(self) -> None:
        # init of F401
        res = Flake8Result.of_line(
            "tmp.py:1:1: F401 'pprint.pprint as pp' imported but unused"
        )
        assert res is not None
        assert res.error_msg == "'pprint.pprint as pp' imported but unused"
        assert res.get_unused_import() == 'pprint.pprint as pp'
        assert res.get_undefined_name() is None

        # init of 821
        res = Flake8Result.of_line(
            "tmp.py:4:1: F821 undefined name 'sp'"
        )
        assert res is not None
        assert res.error_msg == "undefined name 'sp'"
        assert res.get_unused_import() is None
        assert res.get_undefined_name() == 'sp'
        return


class TestFixer(unittest.TestCase):

    def test_fix_lines(self) -> None:
        config = ImportConfig(
            {
                'pp': SingleImport(
                    'pp',
                    'from pprint import pprint as pp',
                    0,
                ),
                'np': SingleImport(
                    'np',
                    'import numpy as np',
                    1,
                ),
            },
        )
        fixer = Fixer(config)

        # There are three import blocks
        target_lines = [
            '#!/usr/bin/env python3',
            'import os',
            'import sys',
            '',
            'import numpy as np',
            'import pandas as pd',
            '',
            'from .hoge import hoge',
            '',
            '',
            'print("Hello, world!")'
        ]
        fixed_lines = fixer.fix_lines(
            target_lines,
            [
                'sys',
                'pandas as pd',
            ],
            [
                'pp',
            ],
        )
        expected_lines = [
            '#!/usr/bin/env python3',
            'import os',
            'from pprint import pprint as pp',
            '',
            'import numpy as np',
            '',
            'from .hoge import hoge',
            '',
            '',
            'print("Hello, world!")'
        ]
        assert fixed_lines == expected_lines

        # There are NO imports
        target_lines = [
            '#!/usr/bin/env python3',
            'pp("Hello, world!")',
        ]
        fixed_lines = fixer.fix_lines(
            target_lines,
            [],
            [
                'pp',
            ],
        )
        expected_lines = [
            '#!/usr/bin/env python3',
            'from pprint import pprint as pp',
            'pp("Hello, world!")'
        ]
        assert fixed_lines == expected_lines

        # There are already import block
        target_lines = [
            '#!/usr/bin/env python3',
            'from pprint import pprint as pp',
            '',
            '',
            'pp("Hello, world!")',
            'a = np.ndarray([1, 2])',
        ]
        fixed_lines = fixer.fix_lines(
            target_lines,
            [],
            [
                'np',
            ],
        )
        expected_lines = [
            '#!/usr/bin/env python3',
            'from pprint import pprint as pp',
            '',
            'import numpy as np',
            '',
            '',
            'pp("Hello, world!")'
        ]
        return
