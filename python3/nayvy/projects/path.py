import glob
import shutil
import subprocess as sp
from enum import Enum
from typing import Any, Dict, List, Tuple, Optional, Generator
from os.path import abspath, dirname, relpath
from dataclasses import dataclass

from nayvy.projects import get_pyproject_root
from nayvy.importing.fixer import ImportStatementMap
from nayvy.projects.modules.loader import ModuleLoader
from nayvy.projects.modules.models import Class, Module, Function
from nayvy.importing.import_statement import SingleImport


class ImportPathFormat(Enum):
    ALL_ABSOLUTE = 'all_absolute'
    ALL_RELATIVE = 'all_relative'
    UNDER_RELATIVE = 'under_relative'


def get_pyproject_root_wrapper(
    filepath: str,
    pyproject_root_markers: List[str],
    requires_in_pyproject: bool = True,
) -> Optional[str]:
    pyproject_root = get_pyproject_root(filepath, pyproject_root_markers)
    if pyproject_root is None:
        if requires_in_pyproject:
            return None
        else:
            pyproject_root = dirname(abspath(filepath))
    return pyproject_root


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
        pyproject_root: str,
    ) -> Optional['ModulePath']:
        """ Constructing ModulePath object from script filepath.
        """
        mod = loader.load_module_from_path(filepath)
        if mod is None:
            return None

        rel_path = relpath(
            abspath(filepath),
            abspath(pyproject_root),
        )
        return ModulePath(
            rel_path.replace('/', '.').rstrip('.py'),
            mod,
        )


def mod_relpath(
    target_modpath: str,
    base_modpath: str,
    import_path_format: ImportPathFormat,
) -> str:
    """ Get relative path to `target_modpath` from `base_modpath`

    i.g.
        Args:
            `target_modpath`: nayvy.importing.import_statement
            `base_modpath`: nayvy.projects.path
        Returns:
            ..importing.import_statement
    """
    if import_path_format == ImportPathFormat.ALL_ABSOLUTE:
        return target_modpath

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
    if (
        (len(base_path_elms) - common_elm_num) >= 2 and
        import_path_format == ImportPathFormat.UNDER_RELATIVE
    ):
        return target_modpath

    return (
        '.' * (len(base_path_elms) - common_elm_num) +
        '.'.join(target_path_elms[common_elm_num:])
    )


def find_all_pythno_paths(root: str) -> List[str]:
    """
    Get all '.py' suffixed paths under `root`.
    The strategy is as follows
    - `fd`
    - `rg --files`
    - `python's glob.glob function`
    """
    # fd
    fd_executable = shutil.which('fd')
    if fd_executable:
        output = sp.run(
            f'{fd_executable} .py$ {root}',
            shell=True,
            stdout=sp.PIPE,
        ).stdout.decode('utf-8')
        return output.split('\n')

    # rg
    rg_executable = shutil.which('rg')
    if rg_executable:
        output = sp.run(
            f'{rg_executable} --files {root} | grep -e .py$',
            shell=True,
            stdout=sp.PIPE,
        ).stdout.decode('utf-8')
        return output.split('\n')

    all_python_script_paths = glob.glob(
        '{}/**/*.py'.format(root),
        recursive=True,
    )
    return all_python_script_paths


@dataclass
class ProjectImportHelper(ImportStatementMap):
    """ Importing helper that providing import within project.
    """

    _import_stmt_map: Dict[str, SingleImport]

    # Override
    def __getitem__(self, name: str) -> Optional[SingleImport]:
        return self._import_stmt_map.get(name, None)

    # Override
    def items(self) -> Generator[Tuple[str, SingleImport], Any, Any]:
        return (
            (k, v) for k, v in self._import_stmt_map.items()
        )


@dataclass(frozen=True)
class ProjectImportHelperBuilder:

    current_filepath: str
    loader: ModuleLoader
    import_path_format: ImportPathFormat
    pyproject_root_markers: List[str]
    requires_in_pyproject: bool

    def make_stmt_relative(
        self,
        modpath: ModulePath,
        modpath_target: ModulePath,
    ) -> str:
        return mod_relpath(
            modpath_target.mod_path,
            modpath.mod_path,
            self.import_path_format,
        )

    def _add_stmt(
        self,
        stmt_map: Dict[str, SingleImport],
        current_modpath: ModulePath,
        modpath: ModulePath,
        name: str,
        func: Optional[Function],
        klass: Optional[Class],
    ) -> None:
        stmt_map[name] = SingleImport(
            name,
            'from {} import {}'.format(
                self.make_stmt_relative(current_modpath, modpath),
                name,
            ),
            2,  # project level
            func,
            klass,
        )

    def make_map(
        self,
        current_modpath: ModulePath,
        all_modpaths: List[ModulePath],
    ) -> Dict[str, SingleImport]:
        import_stmt_map: Dict[str, SingleImport] = {}
        for modpath in all_modpaths:
            for name, func in modpath.mod.function_map.items():
                self._add_stmt(import_stmt_map, current_modpath,
                               modpath, name, func, None)
            for name, klass in modpath.mod.class_map.items():
                self._add_stmt(import_stmt_map, current_modpath,
                               modpath, name, None, klass)
        return import_stmt_map

    def build(self) -> Optional[ProjectImportHelper]:
        # Python project detection
        pyproject_root = get_pyproject_root_wrapper(
            self.current_filepath,
            self.pyproject_root_markers,
            self.requires_in_pyproject,
        )
        if pyproject_root is None:
            return None

        # Current module
        current_modpath = ModulePath.of_filepath(
            self.loader,
            self.current_filepath,
            pyproject_root,
        )
        if current_modpath is None:
            return None

        # Get all modules in the same python project
        all_python_script_paths = find_all_pythno_paths(pyproject_root)
        maybe_all_modpaths = [
            ModulePath.of_filepath(
                self.loader,
                _filepath,
                pyproject_root,
            ) for _filepath in all_python_script_paths
        ]
        # Filter out None and self.
        all_modpaths: List[ModulePath] = []
        for modpath in maybe_all_modpaths:
            if modpath is None:
                continue
            if modpath.mod_path == current_modpath.mod_path:
                continue
            all_modpaths.append(modpath)
        stmt_map = self.make_map(current_modpath, all_modpaths)

        return ProjectImportHelper(stmt_map)
