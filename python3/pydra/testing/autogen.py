from typing import List, Optional
from os.path import abspath, relpath
from pathlib import Path
from dataclasses import dataclass

from pydra.projects import get_pyproject_root
from pydra.projects.modules.loader import ModuluLoader
from pydra.projects.modules.models import Module


@dataclass
class ReactiveTestModule:
    """ ReactiveTestModule is reactive module for testing.

    In that it automatiaclly updated its module
    when lines are changed, it is reactivetest.
    """

    mod: Module
    lines: List[str]

    _loader: ModuluLoader

    def __refresh(self) -> None:
        self.mod = self._loader.load_module_from_lines(self.lines)
        return

    @classmethod
    def of(
        cls,
        loader: ModuluLoader,
        lines: List[str],
    ) -> Optional['ReactiveTestModule']:
        mod = loader.load_module_from_lines(lines)
        if mod is None:
            return None
        return ReactiveTestModule(
            mod=mod,
            lines=lines[:],  # copy
            _loader=loader,
        )

    def add_func(
        self,
        class_name: str,
        func_name: str,
    ) -> None:
        if class_name not in self.mod.class_map:
            self.lines += [
                '',
                '',
                f'class {class_name}(unittest.TestCase):',
                f'',
                f'    def {func_name}(self) -> None:',
                f'        return',

            ]
        else:
            target_line = self.mod.class_map[class_name].line_end
            self.lines[target_line:target_line] = [
                '',
                f'    def {func_name}(self) -> None:',
                f'        return',
            ]

        self.__refresh()
        return


@dataclass
class AutoGenerator:
    """
    AutoGenerator has functions for auto-generating
    test-related components.
    """

    module_loader: ModuluLoader

    def touch_test_file(self, module_filepath: str) -> Optional[str]:
        """ touch the unittest file for module located in `module_filepath`

        Touched test file path will be retunred if succeeded.
        """
        module_abspath = abspath(module_filepath)
        pyproject_root = get_pyproject_root(module_abspath)
        if pyproject_root is None:
            return None

        rel_path = Path(relpath(module_abspath, pyproject_root))
        # Directory path where unit test script will be put.
        target_test_dir = (
            Path(pyproject_root) /
            'tests' /
            Path(*rel_path.parts[1:-1])
        )

        # Test script path
        target_test_path: Path = (
            target_test_dir /
            ('test_' + rel_path.parts[-1])
        )

        target_test_dir.mkdir(parents=True, exist_ok=True)
        (target_test_dir / '__init__.py').touch()
        target_test_path.touch()
        return str(target_test_path)

    def get_added_test_lines(
        self,
        func_name: str,
        impl_module_lines: List[str],
        test_module_lines: List[str],
    ) -> Optional[List[str]]:
        """ Add testing attribute for a given `func_name`.

        If target testing function is already defined,
        it returns lines no-changed.
        """
        impl_mod = self.module_loader.load_module_from_lines(impl_module_lines)
        if impl_mod is None:
            raise Exception(
                'Error occurred in loading implementation script.'
            )

        react_test_mod = ReactiveTestModule.of(
            self.module_loader,
            test_module_lines,
        )
        if react_test_mod is None:
            raise Exception(
                'Error occurred in loading testing script.'
            )

        # calculate additional attributes for testing
        additional_mod = impl_mod.to_test().sub(react_test_mod.mod)

        # check where func_name is defined
        defined_class_name = ''
        for class_name, _class in additional_mod.class_map.items():
            if f'test_{func_name}' in _class.function_map:
                defined_class_name = class_name

        react_test_mod.add_func(
            defined_class_name,
            f'test_{func_name}',
        )
        return react_test_mod.lines
