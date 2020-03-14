import unittest
from typing import List, Tuple

from nayvy.importing.fixer import Fixer, LintEngine
from nayvy.importing.import_config import ImportConfig, SingleImport


class LintEngineMock(LintEngine):

    def get_cmd_piped(self) -> str:
        return 'hoge'

    def get_cmd_filepath(self, file_path: str) -> str:
        return 'hoge'

    def parse_output(self, output: str) -> Tuple[List[str], List[str]]:
        return ([], [])


class TestFixer(unittest.TestCase):

    def test__fix_lines(self) -> None:
        config = ImportConfig(
            {
                'os': SingleImport(
                    'os',
                    'import os',
                    0,
                ),
                'sys': SingleImport(
                    'sys',
                    'import sys',
                    0,
                ),
                'Dict': SingleImport(
                    'Dict',
                    'from typing import Dict',
                    0,
                ),
                'List': SingleImport(
                    'Dict',
                    'from typing import List',
                    0,
                ),
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
        fixer = Fixer(config, LintEngineMock())

        target_lines = [
            '#!/usr/bin/env python3',
            'import os',
            '',
            'import numpy as np',
            'import pandas as pd',
            '',
            'from .hoge import hoge',
            '',
            '',
            'print("Hello, world!")'
        ]
        fixed_lines = fixer._fix_lines(
            target_lines,
            [
                'pandas as pd',
            ],
            [
                'pp',
                'sys',
            ],
        )
        expected_lines = [
            '#!/usr/bin/env python3',
            'import os',
            'from pprint import pprint as pp',
            'import sys',
            '',
            'import numpy as np',
            '',
            'from .hoge import hoge',
            '',
            '',
            'print("Hello, world!")'
        ]
        assert fixed_lines == expected_lines

        # -------------------------------------
        # There are NO imports
        # -------------------------------------
        target_lines = [
            '#!/usr/bin/env python3',
            '',
            'pp("Hello, world!")',
        ]
        fixed_lines = fixer._fix_lines(
            target_lines,
            [],
            [
                'pp',
            ],
        )
        expected_lines = [
            '#!/usr/bin/env python3',
            'from pprint import pprint as pp',
            '',
            'pp("Hello, world!")'
        ]
        assert fixed_lines == expected_lines

        # -------------------------------------
        # There are already import block
        # -------------------------------------
        target_lines = [
            '#!/usr/bin/env python3',
            'from pprint import pprint as pp',
            '',
            '',
            'pp("Hello, world!")',
            'a = np.ndarray([1, 2])',
        ]
        fixed_lines = fixer._fix_lines(
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
            'pp("Hello, world!")',
            'a = np.ndarray([1, 2])',
        ]
        assert fixed_lines == expected_lines

        # -------------------------------------
        # There are two import which belong to the same `from`
        # -------------------------------------
        target_lines = [
            '#!/usr/bin/env python3',
        ]
        fixed_lines = fixer._fix_lines(
            target_lines,
            [],
            [
                'List',
                'Dict',
            ],
        )
        expected_lines = [
            '#!/usr/bin/env python3',
            'from typing import Dict, List',
        ]
        assert fixed_lines == expected_lines

        # -------------------------------------
        # There are tailing comments
        # -------------------------------------
        target_lines = [
            '#!/usr/bin/env python3',
            'from typing import (',
            '    List,  # inline comment 1',
            '    Dict,  # inline comment 2',
            ')',
        ]
        fixed_lines = fixer._fix_lines(
            target_lines,
            [],
            [],
        )
        expected_lines = [
            '#!/usr/bin/env python3',
            'from typing import Dict  # inline comment 2',
            'from typing import List  # inline comment 1',
        ]
        assert fixed_lines == expected_lines

        return
