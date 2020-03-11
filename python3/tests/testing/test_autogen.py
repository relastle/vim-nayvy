import shutil
import unittest
from typing import List
from os.path import dirname
from pathlib import Path

from pydra.projects.attrs import (
    AttrResult,
    ClassAttrs,
    TopLevelFunctionAttrs
)
from pydra.testing.autogen import AutoGenerator


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

    def test_get_additional_attrs(self) -> None:
        impl_ar = AttrResult(
            class_attrs_d={
                'Hoge': ClassAttrs(
                    ['cm1', 'cm2'],
                    ['im1'],
                ),
                'Fuga': ClassAttrs(
                    ['cm1', 'cm2'],
                    ['im2'],
                ),
            },
            top_level_function_attrs=TopLevelFunctionAttrs(
                ['tf1', 'tf2'],
            )
        )

        test_ar = AttrResult(
            class_attrs_d={
                'TestHoge': ClassAttrs(
                    [],
                    ['test_cm1'],
                ),
                'TestFuga': ClassAttrs(
                    [],
                    ['test_cm2', 'test_im2'],
                ),
            },
            top_level_function_attrs=TopLevelFunctionAttrs(
                [],
            )
        )

        actual = self.target.get_additional_attrs(
            impl_ar,
            test_ar,
        )

        assert vars(actual) == vars(AttrResult(
            class_attrs_d={
                'TestHoge': ClassAttrs(
                    [],
                    ['test_cm2', 'test_im1'],
                ),
                'TestFuga': ClassAttrs(
                    [],
                    ['test_cm1'],
                ),
                'Test': ClassAttrs(
                    [],
                    ['test_tf1', 'test_tf2'],
                )
            },
            top_level_function_attrs=TopLevelFunctionAttrs(
                [],
            )
        ))
