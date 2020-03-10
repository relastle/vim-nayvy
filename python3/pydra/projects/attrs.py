"""
`Module` for organizing attiributes defined in a module
"""
import sys
import types
import importlib.util
from typing import Any, List, Tuple, Optional, Generator
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


@dataclass(frozen=True)
class TopLevelFunctionAttrs:

    function_names: List[str]


@dataclass(frozen=True)
class AttrResult:
    """ Result of attributes obtained from a single module file
    """

    class_attrs_lst: List[ClassAttrs]
    top_level_function_attrs: TopLevelFunctionAttrs


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

    class_attrs_lst = [
        ClassAttrs(
            _get_class_method_names(class_attr),
            _get_instance_method_names(class_attr),
        ) for class_attr in [
            getattr(module, class_name)
            for class_name in _get_class_names(module)
        ]
    ]

    return AttrResult(
        class_attrs_lst,
        top_level_function_attrs,
    )
