import shutil
import unittest
from os.path import dirname
from pathlib import Path

from pydra.projects import get_git_root


class TestClass(unittest.TestCase):

    def setUp(self) -> None:
        self.work_dir = dirname(__file__) + '/test_workdir'
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)
        return

    def tearDown(self) -> None:
        shutil.rmtree(self.work_dir)
        return

    def test_get_git_root(self) -> None:
        Path(self.work_dir + '/a/b/c').mkdir(parents=True, exist_ok=True)
        assert get_git_root(
            self.work_dir + '/a/b/c',
            parents_max_lookup_n=3,
        ) is None

        Path(self.work_dir + '/a/.git').touch()
        assert get_git_root(
            self.work_dir + '/a/b/c',
            parents_max_lookup_n=1,
        ) is None

        assert get_git_root(
            self.work_dir + '/a/b/c',
            parents_max_lookup_n=2,
        ) == self.work_dir + '/a'
