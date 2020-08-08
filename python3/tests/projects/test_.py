import shutil
import unittest
from os.path import dirname
from pathlib import Path

from nayvy.projects import (
    get_git_root,
    get_pyproject_root,
)


class TestClass(unittest.TestCase):

    def setUp(self) -> None:
        self.work_dir = f'{dirname(__file__)}/test_workdir'
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)
        return

    def tearDown(self) -> None:
        shutil.rmtree(self.work_dir)
        return

    def test_get_git_root(self) -> None:
        Path(f'{self.work_dir}/a/b/c').mkdir(parents=True, exist_ok=True)
        assert get_git_root(
            f'{self.work_dir}/a/b/c',
            parents_max_lookup_n=3,
        ) is None

        Path(f'{self.work_dir}/a/.git').touch()
        assert get_git_root(
            f'{self.work_dir}/a/b/c',
            parents_max_lookup_n=1,
        ) is None

        assert get_git_root(
            f'{self.work_dir}/a/b/c',
            parents_max_lookup_n=2,
        ) == f'{self.work_dir}/a'

    def test_pyproject_root(self) -> None:
        Path(f'{self.work_dir}/a/b/c').mkdir(parents=True, exist_ok=True)
        assert get_pyproject_root(
            f'{self.work_dir}/a/b/c',
            ['setup.py', 'pyproject.toml'],
            parents_max_lookup_n=3,
        ) is None

        Path(f'{self.work_dir}/a/setup.py').touch()
        assert get_pyproject_root(
            f'{self.work_dir}/a/b/c',
            ['setup.py', 'pyproject.toml'],
            parents_max_lookup_n=2,
        ) == f'{self.work_dir}/a'

        Path(f'{self.work_dir}/a/b/pyproject.toml').touch()
        assert get_pyproject_root(
            self.work_dir + '/a/b/c',
            ['setup.py', 'pyproject.toml'],
            parents_max_lookup_n=2,
        ) == self.work_dir + '/a/b'
