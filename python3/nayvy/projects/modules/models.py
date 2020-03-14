"""
`Module` for organizing attiributes defined in a module
"""
import json
from enum import Enum
from typing import Any, Dict, List, Tuple, Generator, Optional
from dataclasses import asdict, dataclass, is_dataclass


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


def __is_dunder(attr_name: str) -> bool:
    """ check if a given attr_name is `double underscored` one.
    """
    return (
        attr_name.startswith('__') and
        attr_name.endswith('__')
    )


def attr_iter(attr: Any) -> Generator[Tuple[str, Any], None, None]:
    for inner_attr_name in dir(attr):
        if __is_dunder(inner_attr_name):
            continue

        inner_attr = getattr(attr, inner_attr_name)
        yield (inner_attr_name, inner_attr)


class FuncDeclType(str, Enum):

    NO_SET = 'Not set'
    TOP_LEVEL = 'Top level function'
    CLASS = 'Class method'
    INSTANCE = 'Instance method'


@dataclass(frozen=True)
class Function:
    """ Function represents one function
    """

    name: str
    line_begin: int
    line_end: int
    func_decl_type: FuncDeclType

    def to_test(self) -> 'Function':
        return Function(
            name=f'test_{self.name}',
            line_begin=-1,
            line_end=-1,
            func_decl_type=FuncDeclType.INSTANCE,
        )

    @classmethod
    def of_name(cls, name: str) -> 'Function':
        """ utility function for constructing with default values
        """
        return Function(
            name=name,
            line_begin=-1,
            line_end=-1,
            func_decl_type=FuncDeclType.NO_SET,
        )


@dataclass(frozen=True)
class Class:
    """ Class represents one class
    """

    name: str
    line_begin: int
    line_end: int
    function_map: Dict[str, Function]

    def to_test(self) -> 'Class':
        return Class(
            name=f'Test{self.name}',
            line_begin=-1,
            line_end=-1,
            function_map={
                f.name: f for f in
                (
                    f.to_test()
                    for f in self.function_map.values()
                )
            },
        )

    def sub(self, _class: 'Class') -> 'Class':
        """ Get substacted class
        """
        return Class(
            name=self.name,
            line_begin=-1,
            line_end=-1,
            function_map={
                k: v for k, v in
                self.function_map.items()
                if k not in _class.function_map
            },
        )

    def intersect(self, _class: 'Class') -> 'Class':
        """ Get intersection class
        """
        return Class(
            name=self.name,
            line_begin=-1,
            line_end=-1,
            function_map={
                k: v for k, v in
                self.function_map.items()
                if k in _class.function_map
            },
        )


@dataclass(frozen=True)
class Module:
    """ Module represents one module(file)
    """

    function_map: Dict[str, Function]
    class_map: Dict[str, Class]

    def sub(self, _module: 'Module') -> 'Module':
        """ Subtraction of module.

        It returns subtracted module which has attributes
        that are defined in self and not-defined in _module.
        """
        sub_class_map = {
            k: v.sub(_module.class_map.get(
                k,
                Class(
                    k,
                    v.line_begin,
                    v.line_begin,
                    {},
                )
            ))
            for k, v in self.class_map.items()
        }
        sub_class_map = {
            k: v for k, v in sub_class_map.items()
            if v.function_map
        }

        return Module(
            function_map={
                k: v for k, v in
                self.function_map.items()
                if k not in _module.function_map
            },
            class_map=sub_class_map,
        )

    def intersect(self, _module: 'Module') -> 'Module':
        """ Intersection of module.

        It returns intersection module which has attributes
        that are defined in self and also in _module.
        """
        sub_class_map = {
            k: v.intersect(_module.class_map.get(
                k,
                Class(
                    k,
                    v.line_begin,
                    v.line_begin,
                    {},
                )
            ))
            for k, v in self.class_map.items()
        }
        sub_class_map = {
            k: v for k, v in sub_class_map.items()
            if v.function_map
        }

        return Module(
            function_map={
                k: v for k, v in
                self.function_map.items()
                if k in _module.function_map
            },
            class_map=sub_class_map,
        )

    def to_test(self) -> 'Module':
        """ Convert self to module for test script.
        """
        return Module(
            function_map={},
            class_map={
                **{
                    c.name: c for c in
                    (
                        _class.to_test() for _class in
                        self.class_map.values()
                    )
                },
                **{
                    'Test': Class(
                        'Test',
                        -1,
                        -1,
                        {
                            f.name: f for f in
                            (
                                function.to_test() for function in
                                self.function_map.values()
                            )
                        }
                    )
                },
            },
        )

    def get_function(self, line_index: int) -> Optional[str]:
        """ Get the name offunction that is wrapping `line_index`
        """
        # Loop over top level functions.
        for f in self.function_map.values():
            if f.line_begin <= line_index < f.line_end:
                return f.name

        # Loop over class methods and instance methods.
        for c in self.class_map.values():
            for f in c.function_map.values():
                if f.line_begin <= line_index < f.line_end:
                    return f.name
        return None

    def to_func_list_lines(self) -> List[str]:
        """ Represent self as a List of functions.
        """
        res_lines: List[str] = []
        res_lines += [
            f'top_level::{f.name}' for f in self.function_map.values()
        ]
        for c in self.class_map.values():
            res_lines += [
                f'{c.name}::{f.name}' for f in c.function_map.values()
            ]
        return res_lines

    def to_json(self) -> str:
        return json.dumps(self, cls=JSONEncoder, indent=2)
