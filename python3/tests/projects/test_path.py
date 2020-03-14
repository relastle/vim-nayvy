import unittest
from os.path import dirname
from pathlib import Path

from pydra.projects.path import ModulePath
from pydra.projects.modules.models import Module, Function, Class
from pydra.projects.modules.loader import SyntacticModuleLoader


class TestModulePath(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_project_path = (
            Path(dirname(__file__)) /
            '..' /
            '_resources' /
            'sample_project'
        )
        return

    def test_of_filepath(self) -> None:
        given = str(
            self.sample_project_path /
            'package/subpackage/sub_main.py'
        )
        actual = ModulePath.of_filepath(
            SyntacticModuleLoader(),
            given,
        )
        assert actual is not None
        assert actual.mod_path == 'package.subpackage.sub_main'
        return

    def test_get_import(self) -> None:
        module_path = ModulePath(
            'package.subpackage.module',
            Module(
                function_map={
                    'f1': Function.of_name('f1'),
                    'f2': Function.of_name('f2'),
                },
                class_map={
                    'c1': Class(
                        name='c1',
                        line_begin=-1,
                        line_end=-1,
                        function_map={
                            'f1': Function.of_name('f1'),
                            'f2': Function.of_name('f2'),
                        },
                    ),
                },
            )
        )

        assert (
            module_path.get_import('f1') ==
            'from package.subpackage.module import f1'
        )

        assert (
            module_path.get_import('c1') ==
            'from package.subpackage.module import c1'
        )

        assert (
            module_path.get_import('f3') is
            None
        )
