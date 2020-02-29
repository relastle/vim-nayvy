import os
import sys

import vim

from .pydra.importing.fixer import (
    Fixer,
)
from .pydra.importing.import_config import (
    ImportConfig,
)


def pydra_import() -> None:
    config = ImportConfig.of_jsonfile(
        os.environ['HOME'] +
        '/.config/pydra/config.json'
    )
    if config is None:
        print('cannot load pydra config file', file=sys.stderr)
        sys.exit(1)
    fixer = Fixer(config)
    lines = vim.current.buffer[:]
    fixed_lines = fixer.fix_lines_with_flake8(lines)
    vim.current.buffer[:] = fixed_lines
    return
