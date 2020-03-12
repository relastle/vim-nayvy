import unittest
from os.path import abspath, dirname
from pathlib import Path

from pydra.testing.path import (
    impl_path_to_test_path,
    # workaround for ignoring
    test_path_to_impl_path as tst_path_to_impl_path,
)


class Test(unittest.TestCase):

    def test_impl_path_to_test_path(self) -> None:
        assert impl_path_to_test_path(str(Path(
            dirname(__file__)) /
            'sample_project' /
            'package' /
            'main.py'
        )) == abspath(str(Path(
            dirname(__file__)) /
            'sample_project' /
            'tests' /
            'test_main.py'
        ))
        return

    def test_test_path_to_imple_path(self) -> None:
        assert tst_path_to_impl_path(str(Path(
            dirname(__file__)) /
            'sample_project' /
            'tests' /
            'test_main.py'
        )) == abspath(str(Path(
            dirname(__file__)) /
            'sample_project' /
            'package' /
            'main.py'
        ))
        return
