import argparse
import os
import sys

from .importing.fixer import Fixer
from .importing.import_config import ImportConfig


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('file_path', type=str)
    args = parser.parse_args()
    # load config
    config = ImportConfig.of_jsonfile(
        os.environ['HOME'] +
        '/.config/pydra/config.json'
    )
    if config is None:
        print('cannot load pydra config file', file=sys.stderr)
        sys.exit(1)
    fixer = Fixer(config)
    fixer.print_fixed_content_with_flake8(args.file_path)
    return
