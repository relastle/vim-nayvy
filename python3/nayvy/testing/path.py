import glob
from typing import Optional
from os.path import abspath, relpath, basename
from pathlib import Path


def is_test_path(filepath: str) -> bool:
    """ Check if a given filepath is a test one.
    """
    return basename(filepath).startswith('test_')


def impl_path_to_test_path(impl_path: str, pyproject_root: str) -> Optional[str]:
    """
    Convert implementation module path
    into test path
    """
    impl_abspath = abspath(impl_path)
    rel_path = Path(relpath(impl_abspath, pyproject_root))

    # test path
    test_path = (
        Path(pyproject_root) /
        'tests' /
        str(Path(*rel_path.parts[1:-1])) /
        ('test_' + rel_path.parts[-1])
    )

    return str(test_path)


def test_path_to_impl_path(test_path: str, pyproject_root: str) -> Optional[str]:
    """
    Convert test module path
    into implementation module path
    """
    test_abspath = abspath(test_path)
    rel_path = Path(relpath(test_abspath, pyproject_root))

    # flov path where implementation test script will be put.
    impl_glob_path = (
        Path(pyproject_root) /
        '*' /
        Path(*rel_path.parts[1:-1]) /
        (rel_path.parts[-1].lstrip('test_'))
    )

    paths = glob.glob(str(impl_glob_path))
    if not paths:
        return None
    return str(paths[0])
