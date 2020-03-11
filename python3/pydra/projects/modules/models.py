"""
`Module` for organizing attiributes defined in a module
"""
from abc import ABCMeta, abstractmethod
import sys
import types
import importlib.util
from typing import Any, List, Tuple, Optional, Generator, Dict
from os.path import basename
from dataclasses import dataclass
from importlib.abc import Loader
import itertools


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


@dataclass(frozen=True)
class ClassAttrs:

    class_method_names: List[str]
    instance_method_names: List[str]

    def sub(self, target: 'ClassAttrs') -> 'ClassAttrs':
        return ClassAttrs(
            class_method_names=[
                name for name in self.class_method_names
                if name not in target.class_method_names
            ],
            instance_method_names=[
                name for name in self.instance_method_names
                if name not in target.instance_method_names
            ],
        )

    def __sub__(self, target: 'ClassAttrs') -> 'ClassAttrs':
        return self.sub(target)

    def to_test(self) -> 'ClassAttrs':
        return ClassAttrs(
            [],
            (
                [f'test_{name}' for name in self.class_method_names] +
                [f'test_{name}' for name in self.instance_method_names]
            ),
        )

    @property
    def names(self) -> List[str]:
        return (
            self.class_method_names +
            self.instance_method_names
        )

    @classmethod
    def of_empty(cls) -> 'ClassAttrs':
        return ClassAttrs([], [])


@dataclass(frozen=True)
class TopLevelFunctionAttrs:

    function_names: List[str]

    def sub(self, target: 'TopLevelFunctionAttrs') -> 'TopLevelFunctionAttrs':
        return TopLevelFunctionAttrs(
            function_names=[
                name for name in self.function_names
                if name not in target.function_names
            ],
        )

    def __sub__(
        self,
        target: 'TopLevelFunctionAttrs',
    ) -> 'TopLevelFunctionAttrs':
        return self.sub(target)

    @classmethod
    def of_empty(cls) -> 'TopLevelFunctionAttrs':
        return TopLevelFunctionAttrs([])


@dataclass(frozen=True)
class AttrResult:
    """ Result of attributes obtained from a single module file
    """

    class_attrs_d: Dict[str, ClassAttrs]
    top_level_function_attrs: TopLevelFunctionAttrs

    def sub(self, target: 'AttrResult') -> 'AttrResult':
        return AttrResult(
            {
                k: v - target.class_attrs_d.get(
                    k,
                    ClassAttrs.of_empty(),
                )
                for k, v in self.class_attrs_d.items()
            },
            (
                self.top_level_function_attrs -
                target.top_level_function_attrs
            ),
        )

    def __sub__(self, target: 'AttrResult') -> 'AttrResult':
        return self.sub(target)

    def get_defined_class_name(self, func_name: str) -> Optional[str]:
        for class_name, class_attr in self.class_attrs_d.items():
            if func_name in class_attr.names:
                return class_name
        return None

    def get_all_func_names(self) -> List[str]:
        """ Get all function names defined in this AttrResult
        """
        return list(itertools.chain(*[
            class_attr.class_method_names + class_attr.instance_method_names
            for class_attr in self.class_attrs_d.values()
        ])) + self.top_level_function_attrs.function_names

    def to_test(self) -> 'AttrResult':
        """ Get expected attributes for test module for self.
        """
        return AttrResult(
            {
                **{
                    f'Test{k}': v.to_test()
                    for k, v in self.class_attrs_d.items()
                },
                **{
                    'Test': ClassAttrs(
                        [],
                        [
                            f'test_{name}' for name in
                            self.top_level_function_attrs.function_names
                        ]
                    ),
                }
            },
            TopLevelFunctionAttrs.of_empty(),
        )


class ModulePresenter(metaclass=ABCMeta):

    @abstractmethod
    def get_attrs_from_path(
        self,
        module_filepath: str,
    ) -> Optional[AttrResult]:
        raise NotImplementedError

    @abstractmethod
    def get_attrs_from_lines(self, lines: List[str]) -> Optional[AttrResult]:
        raise NotImplementedError


def _get_function_names(attr: Any) -> List[str]:
    return [
        top_level_attr_name
        for top_level_attr_name, top_level_attr in attr_iter(attr)
        if isinstance(top_level_attr, types.FunctionType)
    ]


def _get_class_names(attr: Any) -> List[str]:
    return [
        top_level_attr_name
        for top_level_attr_name, top_level_attr in attr_iter(attr)
        if isinstance(top_level_attr, type)
    ]


def _get_instance_method_names(class_attr: Any) -> List[str]:
    return [
        inner_attr_name
        for inner_attr_name, inner_attr in attr_iter(class_attr)
        if isinstance(inner_attr, types.FunctionType)
    ]


def _get_class_method_names(class_attr: Any) -> List[str]:
    return [
        inner_attr_name
        for inner_attr_name, inner_attr in attr_iter(class_attr)
        if isinstance(inner_attr, types.MethodType)
    ]


def get_attrs(module_filepath: str) -> Optional[AttrResult]:
    """ Get attributes from a given module path

    Especially for function or classes that should be
    explicitly covered by unittesting.
    """
    module_name = basename(module_filepath)
    spec = importlib.util.spec_from_file_location(
        module_name,
        module_filepath,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    if not isinstance(spec.loader, Loader):
        return None
    spec.loader.exec_module(module)

    top_level_function_attrs = TopLevelFunctionAttrs(
        _get_function_names(module)
    )

    class_attrs_lst = {
        class_name: ClassAttrs(
            _get_class_method_names(class_attr),
            _get_instance_method_names(class_attr),
        ) for class_name, class_attr in [
            (class_name, getattr(module, class_name))
            for class_name in _get_class_names(module)
        ]
    }

    return AttrResult(
        class_attrs_lst,
        top_level_function_attrs,
    )
