from typing import Optional, List
from os.path import abspath, relpath
from pathlib import Path

from pydra.projects import get_pyproject_root
from pydra.projects.attrs import (
    get_attrs,
)


class TestModule:

    @classmethod
    def class_lines(
        cls,
        class_name: str,
    ) -> List[str]:
        return [
            '',
            '',
            f'class Test{class_name}(unittest.TestCase):',
            '',
        ]

    @classmethod
    def function_lines(
        cls,
        class_name: str,
        func_name: str,
    ) -> List[str]:
        return [
            f'    def test_{func_name}(self) -> None:',
            '        pass',
        ]

    @classmethod
    def add_func(
        cls,
        lines: List[str],
        class_name: str,
        func_name: str,
    ) -> List[str]:
        class_index = -1
        for i, line in enumerate(lines):
            if f'class Test{class_name}' in line:
                class_index = i
        if class_index < 0:
            # there is no class yet.
            return (
                lines +
                cls.class_lines(class_name) +
                cls.function_lines(class_name, func_name)
            )
        # there already exists class.
        return (
            lines[:class_index+1] +
            cls.function_lines(class_name, func_name) +
            [''] +
            lines[class_index+1:]
        )


class AutoGenerator:

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
        imple_module_path: str,
        test_module_path: str,
    ) -> Optional[List[str]]:
        """ Add testing attribute for a given `func_name`.

        If target testing function is already defined,
        it returns None.
        """
        impl_ar = get_attrs(imple_module_path)
        if impl_ar is None:
            return None

        test_ar = get_attrs(test_module_path)
        if test_ar is None:
            return None

        # calculate additional attributes for testing
        additional_ar = impl_ar.to_test() - test_ar

        if (f'test_{func_name}' not in additional_ar.get_all_func_names()):
            # already defined or
            # not propername as tested attribute.
            return None

        class_name = impl_ar.get_defined_class_name(func_name)
        with open(test_module_path) as f:
            test_module_lines = f.readlines()
        if class_name is None:
            # creation of test method for top level function
            return TestModule.add_func(
                test_module_lines,
                '',
                func_name,
            )

        else:
            # creation of test method for class-or-instance method
            return TestModule.add_func(
                test_module_lines,
                class_name,
                func_name,
            )
