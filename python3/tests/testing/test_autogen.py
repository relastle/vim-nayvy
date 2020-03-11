import shutil
import unittest
from typing import List
from os.path import dirname
from pathlib import Path

from pydra.testing.autogen import (
    TestModule,
    AutoGenerator,
)


class TestTestModule(unittest.TestCase):

    def test_add_func(self) -> None:
        given = [
            'import unittest',
            '',
            'class TestClass1(unittest.TestCase):',
            '    def test_func1(self) -> None:',
            '        pass',
        ]

        actual = TestModule.add_func(
            given,
            'Class2',
            'func1',
        )

        expected = [
            'import unittest',
            '',
            'class TestClass1(unittest.TestCase):',
            '    def test_func1(self) -> None:',
            '        pass',
            '',
            '',
            'class TestClass2(unittest.TestCase):',
            '',
            '    def test_func1(self) -> None:',
            '        pass',
        ]

        assert actual == expected

        actual = TestModule.add_func(
            given,
            'Class1',
            'func2',
        )

        assert actual == [
            'import unittest',
            '',
            'class TestClass1(unittest.TestCase):',
            '    def test_func2(self) -> None:',
            '        pass',
            '',
            '    def test_func1(self) -> None:',
            '        pass',
        ]


class TestAutoGenerator(unittest.TestCase):

    def __generate_files(self, filepaths: List[str]) -> None:
        for filepath in filepaths:
            target_path = (Path(self.work_dir) / filepath)
            target_path.parents[0].mkdir(parents=True, exist_ok=True)
            target_path.touch()
        return

    def setUp(self) -> None:
        self.target = AutoGenerator()
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
        assert self.target.touch_test_file(
            f'{self.work_dir}/package/a.py',
        )
        assert self.target.touch_test_file(
            f'{self.work_dir}/package/sub_package/b.py',
        )
        assert self.target.touch_test_file(
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
