from typing import Optional
from os.path import abspath, relpath
from pathlib import Path

from pydra.projects import get_pyproject_root
from pydra.projects.attrs import AttrResult


class AutoGenerator:

    @classmethod
    def touch_test_file(cls, module_filepath: str) -> Optional[str]:
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

    @classmethod
    def get_additional_attrs(
        cls,
        impl_ar: AttrResult,
        test_ar: AttrResult,
    ) -> AttrResult:
        """
        Calculate additional attributes defined in
        test script compared to implementation module file.
        """
        return test_ar - impl_ar

    @classmethod
    def generate_test_module(cls, test_module_path: str) -> bool:
        pass
