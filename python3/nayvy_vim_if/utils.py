import sys


def error(msg: str) -> None:
    print(
        '{} {}'.format(
            '[nayvy: ERROR]',
            msg,
        ),
        file=sys.stderr,
    )


def warning(msg: str) -> None:
    print(
        '{} {}'.format(
            '[nayvy: WARNING]',
            msg,
        ),
        file=sys.stdout,
    )
