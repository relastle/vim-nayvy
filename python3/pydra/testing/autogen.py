from os.path import abspath, relpath
from pathlib import Path

from pydra.projects import get_pyproject_root


class AutoGenerator:

    @classmethod
    def touch_test_file(cls, module_filepath: str) -> bool:
        """ touch the unittest file for module located in `module_filepath`
        """
        module_abspath = abspath(module_filepath)
        pyproject_root = get_pyproject_root(module_abspath)
        if pyproject_root is None:
            return False

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
        return True
