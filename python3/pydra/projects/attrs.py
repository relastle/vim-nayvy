"""
`Module` for organizing attiributes defined in a module
"""
import sys
import types
import importlib.util
from typing import Any, List, Tuple, Optional, Generator, Dict
from os.path import basename
from dataclasses import dataclass
from importlib.abc import Loader


def __is_dunder(function_name: str) -> bool:
    return (
        function_name.startswith('__') and
        function_name.endswith('__')
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
