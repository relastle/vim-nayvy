import re
from typing import Optional, Tuple, List

from .fixer import LintEngine


class Flake8Engine(LintEngine):

    def get_cmd_piped(self) -> str:
        return 'flake8 -'

    def get_cmd_filepath(self, file_path: str) -> str:
        return 'flake8 {}'.format(file_path)

    def parse_output(self, output: str) -> Tuple[List[str], List[str]]:
        return parse_flake8_output(output)


def parse_flake8_output(
    flake8_output: str,
) -> Tuple[List[str], List[str]]:
    lines = flake8_output.split('\n')
    unused_imports = []
    undefined_names = []
    for line in lines:
        flake8_res = Flake8Result.of_line(line.strip())
        if flake8_res is None:
            continue

        # check if line is warning unused import
        unused_import = flake8_res.get_unused_import()
        if unused_import is not None:
            unused_imports.append(unused_import)

        # check if line is warning undefined name
        undefined_name = flake8_res.get_undefined_name()
        if undefined_name is not None:
            undefined_names.append(undefined_name)
    return unused_imports, undefined_names


class Flake8Result:

    FLAKE8_LINE_RE = r'(?P<filepath>[^:]+):(?P<row>\d+):(?P<column>\d+): (?P<error_code>\w+) (?P<error_msg>.*)'  # noqa
    FLAKE8_F401_MSG_RE = r"'(?P<target>.*)' imported but unused"
    FLAKE8_F821_MSG_RE = r"undefined name '(?P<target>.*)'"

    @property
    def filepath(self) -> str:
        return self._filepath

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._column

    @property
    def error_code(self) -> str:
        return self._error_code

    @property
    def error_msg(self) -> str:
        return self._error_msg

    def __init__(
        self,
        filepath: str,
        row: int,
        column: int,
        error_code: str,
        error_msg: str,
    ) -> None:
        self._filepath = filepath
        self._row = row
        self._column = column
        self._error_code = error_code
        self._error_msg = error_msg
        return

    def get_unused_import(self) -> Optional[str]:
        if self.error_code != 'F401':
            return None

        m = re.match(self.FLAKE8_F401_MSG_RE, self.error_msg)
        if m is None:
            return None
        return m.group('target')

    def get_undefined_name(self) -> Optional[str]:
        if self.error_code != 'F821':
            return None

        m = re.match(self.FLAKE8_F821_MSG_RE, self.error_msg)
        if m is None:
            return None
        return m.group('target')

    @classmethod
    def of_line(
        cls,
        flake8_line: str,
    ) -> Optional['Flake8Result']:
        m = re.match(cls.FLAKE8_LINE_RE, flake8_line)
        if m is None:
            return None
        filepath = m.group('filepath')
        row = int(m.group('row'))
        column = int(m.group('column'))
        error_code = m.group('error_code')
        error_msg = m.group('error_msg')
        return Flake8Result(
            filepath,
            row,
            column,
            error_code,
            error_msg,
        )
