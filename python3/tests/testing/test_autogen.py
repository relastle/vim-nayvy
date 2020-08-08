import shutil
import unittest
from typing import List
from os.path import dirname
from pathlib import Path

from nayvy.testing.autogen import AutoGenerator, ReactiveTestModule
from nayvy.projects.modules.loader import SyntacticModuleLoader


class TestReactiveTestModule(unittest.TestCase):

    def test_add_func(self) -> None:
        loader = SyntacticModuleLoader()

        # --------------------------------------------
        # Test for adding function to already defined class
        # --------------------------------------------
        given = [
            'class TestClass1(unittest.TestCase):',
            '',
            '    def test_method1(self) -> None:',
            '        return',
            '',
            '    def test_method2(self) -> None:',
            '        return',
            '',
            '',
            'class TestClass2(unittest.TestCase):',
            '',
            '    def test_method1(cls) -> None:',
            '        return',
            '',
            '    def test_method2(self) -> None:',
            '        return',
        ]

        react_mod = ReactiveTestModule.of(
            loader,
            given,
        )
        assert react_mod is not None

        react_mod.add_func(
            'TestClass2',
            'added_func',
        )

        actual = react_mod.lines
        # assert that existing lines are unchanged
        assert actual[:len(given)] == given
        # assert added lines
        assert actual[len(given):] == [
            '',
            '    def added_func(self) -> None:',
            '        return',
        ]

        # --------------------------------------------
        # Test for adding function to new class
        # --------------------------------------------
        react_mod = ReactiveTestModule.of(
            loader,
            given,
        )
        assert react_mod is not None

        react_mod.add_func(
            'TopLevelClass3',
            'added_func',
        )
        # assert that existing lines are unchanged
        assert actual[:len(given)] == given
        # assert added lines
        assert react_mod.lines[len(given):] == [
            '',
            '',
            'class TopLevelClass3(unittest.TestCase):',
            '',
            '    def added_func(self) -> None:',
            '        return',
        ]


class TestAutoGenerator(unittest.TestCase):

    def __generate_files(self, filepaths: List[str]) -> None:
        for filepath in filepaths:
            target_path = (Path(self.work_dir) / filepath)
            target_path.parents[0].mkdir(parents=True, exist_ok=True)
            target_path.touch()
        return

    def setUp(self) -> None:
        loader = SyntacticModuleLoader()
        self.target = AutoGenerator(loader, ['setup.py', 'pyproject.toml'])
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

    def test_get_added_test_lines(self) -> None:
        """ Simple integration test of `get_added_test_lines`
        """
        # -------------------------------------
        # New test will be created
        # -------------------------------------
        given_impl_module_lines = [
            'class Hoge:',
            '',
            '    def hoge(self) -> None:',
            '        return',
        ]

        given_test_module_lines = [
            'class TestHoge(unittest.TestCase):',
            '',
            '    def test_fuga(self) -> None:',
            '        return',
        ]

        actual_lines = self.target.get_added_test_lines(
            'hoge',
            given_impl_module_lines,
            given_test_module_lines,
        )

        assert actual_lines == [
            'class TestHoge(unittest.TestCase):',
            '',
            '    def test_fuga(self) -> None:',
            '        return',
            '',
            '    def test_hoge(self) -> None:',
            '        return',
        ]

        # -------------------------------------
        # Nothing will happed
        # -------------------------------------
        given_impl_module_lines = [
            'class Hoge:',
            '',
            '    def hoge(self) -> None:',
            '        return',
        ]

        given_test_module_lines = [
            'class TestHoge(unittest.TestCase):',
            '',
            '    def test_hoge(self) -> None:',
            '        return',
        ]

        actual_lines = self.target.get_added_test_lines(
            'hoge',
            given_impl_module_lines,
            given_test_module_lines,
        )

        assert actual_lines is None
