from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict


class FuncDeclType(Enum):

    TOP_LEVEL = auto()
    CLASS = auto()
    INSTANCE = auto()


@dataclass
class Function:
    """ Function represents one function
    """

    name: str
    line_begin: int
    line_end: int
    ft: FuncDeclType


@dataclass
class Class:
    """ Class represents one class
    """
    function_map: Dict[str, Function]


@dataclass
class Module:
    """ Module represents one module(file)
    """

    cls_map: Dict[str, Class]
    function_map: Dict[str, Function]
