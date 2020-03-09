from typing import Optional
from os.path import exists, dirname


def get_git_root(
    filepath: str,
    parents_max_lookup_n: int = 0,
) -> Optional[str]:
    """ get git project root directory for
    a given file (directory) path
    """

    tmp_path = filepath
    lookup_n = 0
    while (tmp_path):
        if parents_max_lookup_n and lookup_n > parents_max_lookup_n:
            break
        if exists(f'{tmp_path}/.git'):
            return tmp_path
        tmp_path = dirname(tmp_path)
        lookup_n += 1
    return None
