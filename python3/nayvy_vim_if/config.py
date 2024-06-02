
from typing import List, TypeVar

import vim  # noqa
from nayvy.importing.fixer import LinterForFix
from nayvy.projects.path import ImportPathFormat
from pivmy import BaseConfig

T = TypeVar('T')


class Config(BaseConfig):

    import_path_format: ImportPathFormat = ImportPathFormat.ALL_RELATIVE
    linter_for_fix: LinterForFix = LinterForFix.RUFF
    pyproject_root_markers: List[str] = ['pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt']  # noqa
    import_config_path: str = ''
    # coc.nvim
    coc_enabled: int = 1
    cmp_enabled: int = 0
    coc_completion_icon: str = ' nayvy'
    coc_menu_max_width: int = -1


CONFIG = Config.new('nayvy')
