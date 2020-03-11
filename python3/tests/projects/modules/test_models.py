import unittest
from os.path import dirname
from pathlib import Path

from pydra.projects.attrs import (
    ClassAttrs,
    get_attrs,
    AttrResult,
    TopLevelFunctionAttrs,
)


class TestClassAttrs(unittest.TestCase):

    def test_to_test(self) -> None:
        class_attrs = ClassAttrs(
            ['cm1', 'cm2'],
            ['im1', 'im2', 'im3'],
        )
        actual = class_attrs.to_test()
        assert vars(actual) == vars(ClassAttrs(
            [],
            [
                'test_cm1',
                'test_cm2',
                'test_im1',
                'test_im2',
                'test_im3',
            ],
        ))


class TestAttrResult(unittest.TestCase):

    def test_to_test(self) -> None:
        ar = AttrResult(
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
        actual = ar.to_test()
        assert actual == AttrResult(
            class_attrs_d={
                'TestHoge': ClassAttrs(
                    [],
                    ['test_cm1', 'test_cm2', 'test_im1'],
                ),
                'TestFuga': ClassAttrs(
                    [],
                    ['test_cm1', 'test_cm2', 'test_im2'],
                ),
                'Test': ClassAttrs(
                    [],
                    ['test_tf1', 'test_tf2'],
                ),
            },
            top_level_function_attrs=TopLevelFunctionAttrs([]),
        )

    def test_sub(self) -> None:
        ar_self = AttrResult(
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

        ar_target = AttrResult(
            class_attrs_d={
                'Hoge': ClassAttrs(
                    ['cm1'],
                    ['im1'],
                ),
            },
            top_level_function_attrs=TopLevelFunctionAttrs(
                [],
            )
        )

        actual = ar_self.sub(ar_target)

        assert vars(actual) == vars(AttrResult(
            class_attrs_d={
                'Hoge': ClassAttrs(
                    ['cm2'],
                    [],
                ),
                'Fuga': ClassAttrs(
                    ['cm1', 'cm2'],
                    ['im2'],
                ),
            },
            top_level_function_attrs=TopLevelFunctionAttrs(
                ['tf1', 'tf2'],
            )
        ))


class Test(unittest.TestCase):

    def test_get_attrs(self) -> None:
        module_path = Path(dirname(__file__)) / 'resources/sample.py'
        res = get_attrs(str(module_path))

        assert res is not None

        # Assertion of class methods
        assert (
            res.class_attrs_d['TopLevelClass1'].class_method_names ==
            ['class_method1']
        )
        assert (
            res.class_attrs_d['TopLevelClass1'].instance_method_names ==
            ['instance_method1', 'instance_method2']
        )

        assert (
            res.class_attrs_d['TopLevelClass2'].class_method_names ==
            ['class_method2']
        )
        assert (
            res.class_attrs_d['TopLevelClass2'].instance_method_names ==
            ['instance_method3', 'instance_method4']
        )

        # Assertion of top level functions
        assert (
            res.top_level_function_attrs.function_names ==
            ['top_level_function1', 'top_level_function2']
        )
        return
