import unittest
from os.path import dirname
from pathlib import Path

from nayvy.projects.modules.loader import SyntacticModuleLoader
from nayvy.projects.modules.models import (
    Class,
    Function,
    FuncDeclType
)


class TestSyntacticModuleLoader(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_project_path = (
            Path(dirname(__file__)) /
            '..' /
            '..' /
            '_resources' /
            'sample_project'
        )

    def test_load_module_from_path(self) -> None:
        # -------------------------------------
        # Simple file loading
        # -------------------------------------
        module_path = (
            self.sample_project_path /
            'package/main.py'
        )
        loader = SyntacticModuleLoader()
        module = loader.load_module_from_path(str(module_path))

        assert module is not None

        # Assertion of top level functions
        assert (
            module.function_map['top_level_function1'] ==
            Function(
                'top_level_function1',
                '',
                1,
                3,
                FuncDeclType.TOP_LEVEL,
                [
                    'def top_level_function1() -> None:',
                ],
            )
        )

        # Assertion of class methods
        assert (
            vars(module.class_map['TopLevelClass1']) ==
            vars(Class(
                'TopLevelClass1',
                5,
                19,
                {
                    'instance_method1': Function(
                        'instance_method1',
                        '',
                        10,
                        12,
                        FuncDeclType.INSTANCE,
                        [
                            'def instance_method1(self) -> None:',
                        ],
                    ),
                    'class_method1': Function(
                        'class_method1',
                        '',
                        14,
                        16,
                        FuncDeclType.CLASS,
                        [
                            'def class_method1(cls) -> None:',
                        ],
                    ),
                    'instance_method2': Function(
                        'instance_method2',
                        '',
                        17,
                        19,
                        FuncDeclType.INSTANCE,
                        [
                            'def instance_method2(self) -> None:',
                        ],
                    ),
                },
                [
                    'class TopLevelClass1:',
                ]
            ))
        )

        assert (
            module.class_map['TopLevelClass2'] ==
            Class(
                'TopLevelClass2',
                25,
                39,
                {
                    'instance_method3': Function(
                        'instance_method3',
                        '',
                        30,
                        32,
                        FuncDeclType.INSTANCE,
                        [
                            'def instance_method3(self) -> None:',
                        ],
                    ),
                    'class_method2': Function(
                        'class_method2',
                        '',
                        34,
                        36,
                        FuncDeclType.CLASS,
                        [
                            'def class_method2(cls) -> None:',
                        ],
                    ),
                    'instance_method4': Function(
                        'instance_method4',
                        '',
                        37,
                        39,
                        FuncDeclType.INSTANCE,
                        [
                            'def instance_method4(self) -> None:',
                        ],
                    ),
                },
                [
                    'class TopLevelClass2:',
                ]
            )
        )

        # -------------------------------------
        # Complex file loading
        # -------------------------------------
        module_path = (
            self.sample_project_path /
            'package/subpackage/sub_main.py'
        )
        loader = SyntacticModuleLoader()
        module = loader.load_module_from_path(str(module_path))

        assert module is not None

        # Assertion of top level functions
        assert (
            module.function_map['sub_top_level_function1'] ==
            Function(
                'sub_top_level_function1',
                'Top level function.\nsignature is multilined.\n',
                2,
                11,
                FuncDeclType.TOP_LEVEL,
                [
                    'def sub_top_level_function1(',
                    '    hoge: int,',
                    '    fuga: str,',
                    ') -> None:',
                    '    """ Top level function.',
                    '',
                    '    signature is multilined.',
                    '    """',
                ]
            )
        )

        # Assertion of class methods
        assert (
            vars(module.class_map['SubTopLevelClass1']) ==
            vars(Class(
                'SubTopLevelClass1',
                13,
                32,
                {
                    'instance_method1': Function(
                        'instance_method1',
                        'Instance method.\nsignature is multilined.\n',
                        24,
                        32,
                        FuncDeclType.INSTANCE,
                        [
                            'def instance_method1(',
                            '    self, hoge: int,',
                            ') -> None:',
                            '    """ Instance method.',
                            '',
                            '    signature is multilined.',
                            '    """',
                        ],
                    ),
                },
                [
                    'class SubTopLevelClass1:'
                ]
            ))
        )

        # Assertion of class with docstring
        assert (
            vars(module.class_map['SubTopLevelClass2']) ==
            vars(Class(
                'SubTopLevelClass2',
                34,
                41,
                {},
                [
                    'class SubTopLevelClass2:',
                    '    """',
                    '    Multiline docstring top level class.',
                    '',
                    '    This should be captured.',
                    '    """',
                ],
            ))
        )
        return
