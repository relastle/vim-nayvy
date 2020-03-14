import sys

from .importing import *   # noqa
from .testing import *  # noqa


def error(msg: str) -> None:
    print(
        '{} {}'.format(
            '[nayvy: ERROR]',
            msg,
        ),
        file=sys.stderr
    )


def warning(msg: str) -> None:
    print(
        '{} {}'.format(
            '[nayvy: WARNING]',
            msg,
        ),
        file=sys.stderr
    )
