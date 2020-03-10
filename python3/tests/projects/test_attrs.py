import unittest
from os.path import dirname
from pathlib import Path

from pydra.projects.attrs import get_attrs


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
