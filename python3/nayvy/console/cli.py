import sys
from typing import Any

import click
from click_help_colors import HelpColorsGroup, HelpColorsCommand

from nayvy.projects.path import (
    ProjectImportHelperBuilder,
    ImportPathFormat,
)
from ..projects.modules.loader import SyntacticModuleLoader

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
    """ Nayvy: Enriching python coding.
    """
    return


def nayvy_sub_command(f: Any) -> Any:
    """ Nayvy's default subcommand decorator
    """
    return cli.command(
        cls=HelpColorsCommand,
        context_settings=CONTEXT_SETTINGS,
        **DEFAULT_COLOR_OPTIONS,
    )(f)


@nayvy_sub_command
@click.argument('python_script_path', nargs=1)
def lint(
    python_script_path: str,
) -> None:
    """ Run lint of nayvy.
    """
    return


@nayvy_sub_command
@click.argument('python_script_path', nargs=1)
def load(
    python_script_path: str,
) -> None:
    """ Load filepath and convert is to Nayvy's object
    """
    loader = SyntacticModuleLoader()
    module = loader.load_module_from_path(python_script_path)
    if module is None:
        print('Failed to load script', file=sys.stderr)
        return
    print(module.to_json())
    return


@nayvy_sub_command
@click.argument('python_script_path', nargs=1)
def list_imports(
    python_script_path: str,
) -> None:
    """ List all project importable object into script.
    """
    project_import_helper_builder = ProjectImportHelperBuilder(
        python_script_path,
        SyntacticModuleLoader(),
        ImportPathFormat.ALL_ABSOLUTE,
        ['setup.py', 'pyproject.toml'],
        False,
    )
    helper = project_import_helper_builder.build()
    if helper is None:
        print('Failed to load project', file=sys.stderr)
        return

    for _, single_import in helper.items():
        print(single_import.to_line(color=True))
    return


def main() -> None:
    cli()
