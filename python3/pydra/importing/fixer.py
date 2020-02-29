'''
Fix the python lines of code dependent on flake8 result
'''

import re
from typing import List, Optional, Tuple
import subprocess as sp

from .utils import (
    get_import_block_indices,
    get_first_line_num,
)
from .import_config import ImportConfig, SingleImport
from .import_sentence import ImportSentence


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


class Fixer:

    @property
    def config(self) -> ImportConfig:
        return self._config

    def __init__(self, config: ImportConfig) -> None:
        self._config = config
        return

    def parse_flake8_output(
        self,
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

    def fix_lines(
        self,
        lines: List[str],
        unused_imports: List[str],
        undefined_names: List[str],
    ) -> List[str]:
        begin_end_indices = get_import_block_indices(lines)

        # get import_sentences for each block
        maybe_import_sentences_lst = [
            ImportSentence.of_lines(lines[begin_index:end_index])
            for begin_index, end_index in begin_end_indices
        ]

        import_sentences_lst = []
        for maybe in maybe_import_sentences_lst:
            if maybe is not None:
                import_sentences_lst.append(maybe)

        # remove unused names from import_sentences
        removed_import_sentences_lst = [
            ImportSentence.get_removed_lst(import_sentences, unused_imports)
            for import_sentences in import_sentences_lst
        ]

        # Constructing not-None single import list
        imports_to_add: List[SingleImport] = []
        for undefined_name in undefined_names:
            single_import = self.config.import_d.get(
                undefined_name,
                None,
            )
            if single_import is None:
                continue
            imports_to_add.append(single_import)

        # sort by import block level
        imports_to_add = sorted(imports_to_add, key=lambda x: x.level)

        # constructing import import sentences
        for import_to_add in imports_to_add:
            import_sentence_to_add = ImportSentence.of(import_to_add.sentence)
            if import_sentence_to_add is None:
                continue
            if len(removed_import_sentences_lst) <= import_to_add.level:
                removed_import_sentences_lst.append([import_sentence_to_add])
            else:
                removed_import_sentences_lst[import_to_add.level].append(
                    import_sentence_to_add
                )

        # constructing resulting lines
        res_lines: List[str] = []

        fitst_line_num = get_first_line_num(lines)

        # add lines before import as it is
        if not begin_end_indices:
            res_lines += lines[:fitst_line_num]
        else:
            res_lines += lines[:begin_end_indices[0][0]]

        # add organized import blocks
        for i, removed_import_sentences in enumerate(
            removed_import_sentences_lst
        ):
            for import_sentence in removed_import_sentences:
                res_lines.append(str(import_sentence))
            if i < len(removed_import_sentences_lst) - 1:
                res_lines.append('')

        # add lines after import as it is
        if not begin_end_indices:
            res_lines += lines[fitst_line_num:]
        else:
            res_lines += lines[begin_end_indices[-1][1]:]
        return res_lines

    def print_fixed_content(self, file_path: str) -> None:
        flake8_job = sp.run(
            'flake8 {}'.format(file_path),
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.DEVNULL,
        )

        # Extract result
        flake8_output = flake8_job.stdout.decode('utf-8')

        # Parse output
        unused_imports, undefined_names = self.parse_flake8_output(
            flake8_output,
        )

        # Fix line of codes
        with open(file_path) as f:
            lines = [line.strip() for line in f.readlines()]

        fixed_lines = self.fix_lines(
            lines,
            unused_imports,
            undefined_names,
        )
        for fixed_line in fixed_lines:
            print(fixed_line)
