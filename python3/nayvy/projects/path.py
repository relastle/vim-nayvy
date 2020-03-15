from typing import List, Optional, Generator, Tuple, Any
from os.path import abspath, relpath
from dataclasses import dataclass
import glob

from . import get_pyproject_root
from .modules.loader import ModuleLoader
from .modules.models import Module
from ..importing.fixer import ImportStatementMap
from ..importing.import_statement import SingleImport


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


def mod_relpath(target_modpath: str, base_modpath: str) -> str:
    """ get relative path to `target_modpath` from `base_modpath`

    i.g.
        Args:
            `target_modpath`: nayvy.importing.import_statement
            `base_modpath`: nayvy.projects.path
        Returns:
            ..importing.import_statement
    """
    if target_modpath == base_modpath:
        return '.'

    target_path_elms = target_modpath.split('.')
    base_path_elms = base_modpath.split('.')
    if target_path_elms[0] != base_path_elms[0]:
        return target_modpath
    common_elm_num = 0
    for target_elm, base_elm in zip(target_path_elms, base_path_elms):
        if target_elm != base_elm:
            break
        common_elm_num += 1
    return (
        '.' * (len(base_path_elms) - common_elm_num) +
        '.'.join(target_path_elms[common_elm_num:])
    )


@dataclass
class ProjectImportHelper(ImportStatementMap):
    """ Importing helper that providing import within project.
    """

    current_modpath: ModulePath
    all_modpaths: List[ModulePath]

    def _make_stmt_relative(self, modpath_target: ModulePath) -> str:
        return mod_relpath(
            modpath_target.mod_path,
            self.current_modpath.mod_path,
        )

    def __getitem__(self, name: str) -> Optional[SingleImport]:
        for modpath in self.all_modpaths:
            stmt = modpath.get_import(name)
            if stmt is not None:
                return SingleImport(
                    name,
                    'from {} import {}'.format(
                        self._make_stmt_relative(modpath),
                        name,
                    ),
                    2,  # project level
                )
        return None

    def items(self) -> Generator[Tuple[str, SingleImport], Any, Any]:
        for modpath in self.all_modpaths:
            for name in modpath.mod.function_map.keys():
                single_import = self[name]
                if single_import is None:
                    continue
                else:
                    yield (name, single_import)

            for name in modpath.mod.class_map.keys():
                single_import = self[name]
                if single_import is None:
                    continue
                else:
                    yield (name, single_import)

    @classmethod
    def of_filepath(
        cls,
        loader: ModuleLoader,
        filepath: str,
    ) -> Optional['ProjectImportHelper']:
        current_modpath = ModulePath.of_filepath(
            loader,
            filepath,
        )
        if current_modpath is None:
            return None
        pyproject_root = get_pyproject_root(filepath)
        assert pyproject_root is not None
        all_python_script_paths = glob.glob(
            '{}/**/*.py'.format(pyproject_root),
            recursive=True,
        )
        maybe_all_modpaths = [
            ModulePath.of_filepath(
                loader,
                _filepath,
            ) for _filepath in all_python_script_paths
        ]
        all_modpaths: List[ModulePath] = []
        for modpath in maybe_all_modpaths:
            if modpath is None:
                continue
            if modpath.mod_path == current_modpath.mod_path:
                continue
            all_modpaths.append(modpath)

        return ProjectImportHelper(
            current_modpath,
            all_modpaths,
        )
