
from typing import List, TypeVar

import vim  # noqa
from pivmy import BaseConfig
from nayvy.projects.path import ImportPathFormat
from nayvy.importing.fixer import LinterForFix

T = TypeVar('T')


class Config(BaseConfig):

    import_path_format: ImportPathFormat = ImportPathFormat.ALL_RELATIVE
    linter_for_fix: LinterForFix = LinterForFix.PYFLAKES
    pyproject_root_markers: List[str] = ['pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt']  # noqa


CONFIG = Config.new('nayvy')
