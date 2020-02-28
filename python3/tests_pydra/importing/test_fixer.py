import unittest

from pydra.importing.fixer import Fixer
from pydra.importing.import_config import (
    ImportConfig,
    SingleImport,
)


class TestClass(unittest.TestCase):

    def test_fix_lines(self) -> None:
        config = ImportConfig(
            {
                'pp': SingleImport(
                    'pp',
                    'from pprint import pprint as pp',
                    0,
                ),
            },
        )
        fixer = Fixer(config)
        target_lines = [
            'import os',
            'import sys',
            '',
            'import numpy as np',
            'import pandas as pd',
            '',
            'from .hoge import hoge',
            '',
            '',
            'print("Hello world!")'
        ]
        fixed_lines = fixer.fix_lines(
            target_lines,
            [
                'sys',
                'pd',
            ],
            [
                'pp',
            ],
        )
        expected_lines = [
            'import os',
            'from pprint import pprint as pp',
            '',
            'import numpy as np',
            '',
            'from .hoge import hoge',
            '',
            '',
            'print("Hello world!")'
        ]
        assert fixed_lines == expected_lines
        return
