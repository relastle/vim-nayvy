import sys
from typing import Any

import click
from click_help_colors import HelpColorsGroup, HelpColorsCommand

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    max_content_width=120,
)
DEFAULT_COLOR_OPTIONS = dict(
    help_headers_color='white',
    help_options_color='cyan',
)


def panic(message: str) -> None:
    """ Panic with the given message
    """
    print(message, file=sys.stderr)
    sys.exit(1)
    return


@click.group(
    cls=HelpColorsGroup,
    context_settings=CONTEXT_SETTINGS,
    **DEFAULT_COLOR_OPTIONS,  # type: ignore
)
def cli() -> None:
    """ Pydra: Enhancing python code editting environment
    """
    return


def pydra_sub_command(f: Any) -> Any:
    """ Pydra's default subcommand decorator
    """
    return cli.command(
        cls=HelpColorsCommand,
        context_settings=CONTEXT_SETTINGS,
        **DEFAULT_COLOR_OPTIONS,
    )(f)


@pydra_sub_command
@click.argument('python_script_path', nargs=1)
def lint(
    python_script_path: str,
) -> None:
    """ Run lint of pydra.
    """
    return


def main() -> None:
    cli()
