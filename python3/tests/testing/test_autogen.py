import shutil
import unittest
from typing import List
from os.path import dirname
from pathlib import Path

from pydra.testing.autogen import AutoGenerator


class TestAutoGenerator(unittest.TestCase):

    def __generate_files(self, filepaths: List[str]) -> None:
        for filepath in filepaths:
            target_path = (Path(self.work_dir) / filepath)
            target_path.parents[0].mkdir(parents=True, exist_ok=True)
            target_path.touch()
        return

    def setUp(self) -> None:
        self.work_dir = f'{dirname(__file__)}/test_workdir'
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)
        self.__generate_files([
            'setup.py',
            'package/a.py',
            'package/sub_package/b.py',
            'package/sub_package/sub_sub_package/c.py',
        ])
        return

    def tearDown(self) -> None:
        shutil.rmtree(self.work_dir)
        return

    def test_touch_test_file(self) -> None:
        assert AutoGenerator.touch_test_file(
            f'{self.work_dir}/package/a.py',
        )
        assert AutoGenerator.touch_test_file(
            f'{self.work_dir}/package/sub_package/b.py',
        )
        assert AutoGenerator.touch_test_file(
            f'{self.work_dir}/package/sub_sub_package/c.py',
        )

        assert Path(
            f'{self.work_dir}/tests/test_a.py',
        ).exists()
        assert Path(
            f'{self.work_dir}/tests/sub_package/test_b.py',
        ).exists()
        assert Path(
            f'{self.work_dir}/tests/sub_sub_package/test_c.py',
        ).exists()
        return
