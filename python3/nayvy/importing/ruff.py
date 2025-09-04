import re
from typing import List, Optional, Tuple

from .fixer import LintEngine


class RuffEngine(LintEngine):
    def get_cmd_piped(self) -> str:
        return 'ruff check --output-format pylint -'

    def get_cmd_filepath(self, file_path: str) -> str:
        return 'ruff {}'.format(file_path)

    def parse_output(self, output: str) -> Tuple[List[str], List[str]]:
        return parse_ruff_output(output)


def parse_ruff_output(
    ruff_output: str,
) -> Tuple[List[str], List[str]]:
    lines = ruff_output.split('\n')
    unused_imports = []
    undefined_names = []
    for line in lines:
        ruff_res = RuffResult.of_line(line.strip())
        if ruff_res is None:
            continue

        # check if line is warning unused import
        unused_import = ruff_res.get_unused_import()
        if unused_import is not None:
            unused_imports.append(unused_import)

        # check if line is warning undefined name
        undefined_name = ruff_res.get_undefined_name()
        if undefined_name is not None:
            undefined_names.append(undefined_name)
    return unused_imports, undefined_names


class RuffResult:
    RUFF_LINE_RE = r'(?P<filepath>[^:]+):(?P<row>\d+):(?P<column>\d+)?:? \S+ (\[\*\] )?(?P<error_msg>.*)'  # noqa
    RUFF_UNUSED_MSG_RE = r'`(?P<target>.*)` imported but unused'
    RUFF_UNDEFINED_MSG_RE = r'Undefined name `(?P<target>.*)`'

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
        m = re.match(self.RUFF_UNUSED_MSG_RE, self.error_msg)
        if m is None:
            return None
        return m.group('target')

    def get_undefined_name(self) -> Optional[str]:
        m = re.match(self.RUFF_UNDEFINED_MSG_RE, self.error_msg)
        if m is None:
            return None
        return m.group('target')

    @classmethod
    def of_line(
        cls,
        ruff_line: str,
    ) -> Optional['RuffResult']:
        m = re.match(cls.RUFF_LINE_RE, ruff_line)
        if m is None:
            return None
        filepath = m.group('filepath')
        row = int(m.group('row'))
        error_msg = m.group('error_msg')
        return RuffResult(
            filepath,
            row,
            error_msg,
        )
