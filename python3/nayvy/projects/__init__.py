from typing import List, Optional
from os.path import exists, dirname, abspath


def _get_root(
    indicators: List[str],
    filepath: str,
    parents_max_lookup_n: int = 100,
) -> Optional[str]:
    """ get project root defined by `indicator`
    for a given file (directory) path
    """
    tmp_path = abspath(filepath)
    lookup_n = 0
    while (tmp_path):
        if parents_max_lookup_n and lookup_n > parents_max_lookup_n:
            break

        if any([
                exists(f'{tmp_path}/{indicator}')
                for indicator in indicators
        ]):
            return tmp_path
        tmp_path = dirname(tmp_path)
        lookup_n += 1
    return None


def get_git_root(
    filepath: str,
    parents_max_lookup_n: int = 100,
) -> Optional[str]:
    """ get git project root
    """
    return _get_root(
        ['.git'],
        filepath,
        parents_max_lookup_n,
    )


def get_pyproject_root(
    filepath: str,
    parents_max_lookup_n: int = 100,
) -> Optional[str]:
    """ Get python project root
    """
    return _get_root(
        ['setup.py', 'pyproject.toml'],
        filepath,
        parents_max_lookup_n,
    )
