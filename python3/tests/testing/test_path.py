import unittest
from os.path import abspath, dirname
from pathlib import Path

from nayvy.testing.path import (
    impl_path_to_test_path,
    # workaround for ignoring
    test_path_to_impl_path as tst_path_to_impl_path,
)


class Test(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_project_path = (
            Path(dirname(__file__)) /
            '..' /
            '_resources' /
            'sample_project'
        )

    def test_impl_path_to_test_path(self) -> None:
        assert impl_path_to_test_path(str(
            self.sample_project_path /
            'package' /
            'main.py'
        )) == abspath(str(
            self.sample_project_path /
            'tests' /
            'test_main.py'
        ))
        return

    def test_test_path_to_imple_path(self) -> None:
        assert tst_path_to_impl_path(str(
            self.sample_project_path /
            'tests' /
            'test_main.py'
        )) == abspath(str(
            self.sample_project_path /
            'package' /
            'main.py'
        ))
        return
