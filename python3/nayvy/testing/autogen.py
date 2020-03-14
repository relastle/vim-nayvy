from typing import List, Optional
from os.path import dirname
from pathlib import Path
from dataclasses import dataclass

from nayvy.projects.modules.loader import ModuleLoader
from nayvy.projects.modules.models import Module
from .path import impl_path_to_test_path


@dataclass
class ReactiveTestModule:
    """ ReactiveTestModule is reactive module for testing.

    In that it automatiaclly updated its module
    when lines are changed, it is reactivetest.
    """

    mod: Module
    lines: List[str]

    _loader: ModuleLoader

    def __refresh(self) -> None:
        mod = self._loader.load_module_from_lines(self.lines)
        if mod is not None:
            self.mod = mod
        return

    @classmethod
    def of(
        cls,
        loader: ModuleLoader,
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

    module_loader: ModuleLoader

    def touch_test_file(self, module_filepath: str) -> Optional[str]:
        """ touch the unittest file for module located in `module_filepath`

        Touched test file path will be retunred if succeeded.
        """
        test_path = impl_path_to_test_path(module_filepath)
        if test_path is None:
            return None
        test_dir = Path(dirname(test_path))
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / '__init__.py').touch()
        Path(test_path).touch()
        return str(test_path)

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

        if not defined_class_name:
            # Maybe already exists.
            return None

        react_test_mod.add_func(
            defined_class_name,
            f'test_{func_name}',
        )
        return react_test_mod.lines
