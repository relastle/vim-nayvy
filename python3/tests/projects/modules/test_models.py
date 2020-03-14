import unittest

from nayvy.projects.modules.models import (
    Class,
    Module,
    Function,
    FuncDeclType
)


class TestModule(unittest.TestCase):

    def test_sub(self) -> None:
        m1 = Module(
            function_map={
                'a': Function('a', -1, -1, FuncDeclType.TOP_LEVEL),
            },
            class_map={
                'C': Class('C', -1, -1, {
                    'a': Function(
                        'a',
                        -1,
                        -1,
                        FuncDeclType.INSTANCE,
                    ),
                    'b': Function(
                        'b',
                        -1,
                        -1,
                        FuncDeclType.INSTANCE,
                    )
                }),
            },
        )

        m2 = Module(
            function_map={},
            class_map={
                'C': Class('C', -1, -1, {
                    'a': Function(
                        'a',
                        -1,
                        -1,
                        FuncDeclType.INSTANCE,
                    ),
                }),
            },
        )

        subtracted = m1.sub(m2)
        assert len(subtracted.function_map) == 1
        assert len(subtracted.class_map['C'].function_map) == 1
        assert 'b' in subtracted.class_map['C'].function_map
        return

    def test_intersect(self) -> None:
        m1 = Module(
            function_map={
                'a': Function('a', -1, -1, FuncDeclType.TOP_LEVEL),
            },
            class_map={
                'C': Class('C', -1, -1, {
                    'a': Function(
                        'a',
                        -1,
                        -1,
                        FuncDeclType.INSTANCE,
                    ),
                    'b': Function(
                        'b',
                        -1,
                        -1,
                        FuncDeclType.INSTANCE,
                    ),
                }),
            },
        )

        m2 = Module(
            function_map={},
            class_map={
                'C': Class('C', -1, -1, {
                    'a': Function(
                        'a',
                        -1,
                        -1,
                        FuncDeclType.INSTANCE,
                    ),
                }),
            },
        )

        intersected = m1.intersect(m2)
        assert len(intersected.function_map) == 0
        assert len(intersected.class_map['C'].function_map) == 1
        assert 'a' in intersected.class_map['C'].function_map
        return

    def test_to_test(self) -> None:
        m = Module(
            function_map={
                'a': Function(
                    'a',
                    -1,
                    -1,
                    FuncDeclType.TOP_LEVEL,
                ),
            },
            class_map={
                'C': Class(
                    'C',
                    -1,
                    -1,
                    {
                        'a': Function(
                            'a',
                            -1,
                            -1,
                            FuncDeclType.INSTANCE,
                        ),
                        'b': Function(
                            'b',
                            -1,
                            -1,
                            FuncDeclType.CLASS,
                        ),
                    }
                ),
            },
        )

        assert vars(m.to_test()) == vars(Module(
            {},
            class_map={
                'TestC': Class(
                    'TestC',
                    -1,
                    -1,
                    {
                        'test_a': Function(
                            'test_a',
                            -1,
                            -1,
                            FuncDeclType.INSTANCE,
                        ),
                        'test_b': Function(
                            'test_b',
                            -1,
                            -1,
                            FuncDeclType.INSTANCE,
                        ),
                    }
                ),
                'Test': Class(
                    'Test',
                    -1,
                    -1,
                    {
                        'test_a': Function(
                            'test_a',
                            -1,
                            -1,
                            FuncDeclType.INSTANCE,
                        ),
                    }
                ),
            },
        ))

    def test_to_func_list_lines(self) -> None:
        m = Module(
            function_map={
                'a': Function(
                    'a',
                    -1,
                    -1,
                    FuncDeclType.TOP_LEVEL,
                ),
            },
            class_map={
                'C': Class(
                    'C',
                    -1,
                    -1,
                    {
                        'a': Function(
                            'a',
                            -1,
                            -1,
                            FuncDeclType.INSTANCE,
                        ),
                        'b': Function(
                            'b',
                            -1,
                            -1,
                            FuncDeclType.CLASS,
                        ),
                    }
                ),
            },
        )

        assert m.to_func_list_lines() == [
            'top_level::a',
            'C::a',
            'C::b',
        ]
