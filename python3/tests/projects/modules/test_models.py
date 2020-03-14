import unittest

from nayvy.projects.modules.models import (
    Class,
    Module,
    Function,
    FuncDeclType
)


class TestModule(unittest.TestCase):

    def setUp(self) -> None:
        self.m1 = Module(
            function_map={
                'a': Function('a', 1, 10, FuncDeclType.TOP_LEVEL),
            },
            class_map={
                'C': Class('C', 12, 30, {
                    'a': Function(
                        'a',
                        13,
                        20,
                        FuncDeclType.INSTANCE,
                    ),
                    'b': Function(
                        'b',
                        21,
                        30,
                        FuncDeclType.INSTANCE,
                    )
                }),
            },
        )
        self.m2 = Module(
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
        return

    def test_sub(self) -> None:
        subtracted = self.m1.sub(self.m2)
        assert len(subtracted.function_map) == 1
        assert len(subtracted.class_map['C'].function_map) == 1
        assert 'b' in subtracted.class_map['C'].function_map
        return

    def test_intersect(self) -> None:
        intersected = self.m1.intersect(self.m2)
        assert len(intersected.function_map) == 0
        assert len(intersected.class_map['C'].function_map) == 1
        assert 'a' in intersected.class_map['C'].function_map
        return

    def test_to_test(self) -> None:
        assert vars(self.m1.to_test()) == vars(Module(
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

    def test_get_function(self) -> None:
        # begin corner case
        assert self.m1.get_function(0) is None
        assert self.m1.get_function(1) == 'a'

        # end corner case
        assert self.m1.get_function(19) == 'a'
        assert self.m1.get_function(20) is None

    def test_to_func_list_lines(self) -> None:
        assert self.m1.to_func_list_lines() == [
            'top_level::a',
            'C::a',
            'C::b',
        ]
