
from typing import Optional
from os.path import abspath, relpath
from dataclasses import dataclass

from . import get_pyproject_root
from .modules.loader import ModuleLoader
from .modules.models import Module


@dataclass(frozen=True)
class ModulePath:
    """ Represent one module.

    - Content of module
    - Path within python project
    """

    mod_path: str
    mod: Module

    def get_import(self, name: str) -> Optional[str]:
        """ Get import statement string.
        """
        if (
            name not in self.mod.function_map and
            name not in self.mod.class_map
        ):
            return None
        return f'from {self.mod_path} import {name}'

    @classmethod
    def of_filepath(
        cls,
        loader: ModuleLoader,
        filepath: str,
    ) -> Optional['ModulePath']:
        """ Constructing ModulePath object from script filepath.
        """
        mod = loader.load_module_from_path(filepath)
        if mod is None:
            return None

        pyproject_root = get_pyproject_root(filepath)
        if pyproject_root is None:
            return None

        rel_path = relpath(
            abspath(filepath),
            abspath(pyproject_root),
        )
        return ModulePath(
            rel_path.replace('/', '.').rstrip('.py'),
            mod,
        )
