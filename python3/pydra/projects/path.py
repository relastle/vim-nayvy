
from typing import Optional
from dataclasses import dataclass

from .modules.models import Module


@dataclass(frozen=True)
class ModulePath:
    """ Represent one module.

    - Content of module
    - Path within python project
    """

    mod_path: str
    mod: Module

    @classmethod
    def of_filepath(cls, filepath: str) -> Optional['ModulePath']:
        pass
