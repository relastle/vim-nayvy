import re
from typing import List, Tuple, Optional

from .fixer import LintEngine


class PyflakesEngine(LintEngine):

    def get_cmd_piped(self) -> str:
        return 'pyflakes'

    def get_cmd_filepath(self, file_path: str) -> str:
        return 'pyflakes {}'.format(file_path)

    def parse_output(self, output: str) -> Tuple[List[str], List[str]]:
        return parse_pyflakes_output(output)


def parse_pyflakes_output(
    flake8_output: str,
) -> Tuple[List[str], List[str]]:
    lines = flake8_output.split('\n')
    unused_imports = []
    undefined_names = []
    for line in lines:
        pyflakes_res = PyflakesResult.of_line(line.strip())
        if pyflakes_res is None:
            continue

        # check if line is warning unused import
        unused_import = pyflakes_res.get_unused_import()
        if unused_import is not None:
            unused_imports.append(unused_import)

        # check if line is warning undefined name
        undefined_name = pyflakes_res.get_undefined_name()
        if undefined_name is not None:
            undefined_names.append(undefined_name)
    return unused_imports, undefined_names


class PyflakesResult:

    PYFLAKES_LINE_RE = r'(?P<filepath>[^:]+):(?P<row>\d+): (?P<error_msg>.*)'  # noqa
    PYFLAKES_UNUSED_MSG_RE = r"'(?P<target>.*)' imported but unused"
    PYFLAKES_UNDEFINED_MSG_RE = r"undefined name '(?P<target>.*)'"

    @property
    def filepath(self) -> str:
        return self._filepath

    @property
    def row(self) -> int:
        return self._row

    @property
    def error_msg(self) -> str:
        return self._error_msg

    def __init__(
        self,
        filepath: str,
        row: int,
        error_msg: str,
    ) -> None:
        self._filepath = filepath
        self._row = row
        self._error_msg = error_msg
        return

    def get_unused_import(self) -> Optional[str]:
        m = re.match(self.PYFLAKES_UNUSED_MSG_RE, self.error_msg)
        if m is None:
            return None
        return m.group('target')

    def get_undefined_name(self) -> Optional[str]:
        m = re.match(self.PYFLAKES_UNDEFINED_MSG_RE, self.error_msg)
        if m is None:
            return None
        return m.group('target')

    @classmethod
    def of_line(
        cls,
        pyflakes_line: str,
    ) -> Optional['PyflakesResult']:
        m = re.match(cls.PYFLAKES_LINE_RE, pyflakes_line)
        if m is None:
            return None
        filepath = m.group('filepath')
        row = int(m.group('row'))
        error_msg = m.group('error_msg')
        return PyflakesResult(
            filepath,
            row,
            error_msg,
        )
