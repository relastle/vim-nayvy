import sys

import vim  # noqa

from pydra.importing.fixer import (
    Fixer,
)
#  from pydra.importing.flake8 import Flake8Engine
from pydra.importing.pyflakes import PyflakesEngine
from pydra.importing.import_config import (
    ImportConfig,
)


def pydra_import() -> None:
    config = ImportConfig.init()
    if config is None:
        print('cannot load pydra config file', file=sys.stderr)
        sys.exit(1)
    fixer = Fixer(config, PyflakesEngine())
    lines = vim.current.buffer[:]
    fixed_lines = fixer.fix_lines(lines)
    vim.current.buffer[:] = fixed_lines
    return
