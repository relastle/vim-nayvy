from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict


@dataclass
class Class:
    function_map: Dict[str, Function]


@dataclass
class Module:
    """ Module represents one module(file)
    """

    cls_map: Dict[str, Class]
    function_map: Dict[str, Function]
