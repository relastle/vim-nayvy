import unittest
from os.path import dirname
from pathlib import Path
from dataclasses import dataclass

from prussian.projects.path import (
    ModulePath,
    ProjectImportHelper,
    mod_relpath
)
from prussian.projects.modules.loader import SyntacticModuleLoader
from prussian.projects.modules.models import Class, Module, Function
from prussian.importing.import_statement import SingleImport


class Test(unittest.TestCase):

    def test_mod_relpath(self) -> None:

        @dataclass
        class Case:
            description: str
            target_modpath: str
            base_modpath: str
            expected: str

        for case in [
            Case(
                description='same mod path',
                target_modpath='package.module',
                base_modpath='package.module',
                expected='.',
            ),
            Case(
                description='mod in the same package',
                target_modpath='package.module1',
                base_modpath='package.module2',
                expected='.module1',
            ),
            Case(
                description='subpackage mod path',
                target_modpath='package.subpackage.module',
                base_modpath='package.module',
                expected='.subpackage.module',
            ),
            Case(
                description='different package ',
                target_modpath='package.subpackage1.module',
                base_modpath='package.subpackage2.module',
                expected='..subpackage1.module',
            ),
        ]:
            self.assertEqual(
                mod_relpath(case.target_modpath, case.base_modpath),
                case.expected,
                case.description,
            )


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


class TestProjectImportHelper(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_project_path = (
            Path(dirname(__file__)) /
            '..' /
            '_resources' /
            'sample_project'
        )
        return

    def test___getitem__(self) -> None:
        actual = ProjectImportHelper.of_filepath(
            SyntacticModuleLoader(),
            str(
                self.sample_project_path /
                'package' /
                'main.py'
            ))
        assert actual is not None
        # Can access to subpackage's function
        assert actual['sub_top_level_function1'] == SingleImport(
            'sub_top_level_function1',
            'from .subpackage.sub_main import sub_top_level_function1',
            2,
        )

        # Cannot access to function defined in self
        assert actual['top_level_function1'] is None
        return
