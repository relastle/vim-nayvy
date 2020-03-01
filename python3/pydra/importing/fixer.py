'''
Fix the python lines of code dependent on Linter result
'''

import subprocess as sp
from abc import ABCMeta, abstractmethod
from typing import List, Tuple
from pprint import pformat

from .utils import get_first_line_num, get_import_block_indices
from .import_config import ImportConfig, SingleImport
from .import_sentence import ImportSentence


class LintEngine(metaclass=ABCMeta):

    @abstractmethod
    def get_cmd_piped(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_cmd_filepath(self, file_path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def parse_output(self, output: str) -> Tuple[List[str], List[str]]:
        raise NotImplementedError


class Fixer:

    @property
    def config(self) -> ImportConfig:
        return self._config

    @property
    def lint_engine(self) -> LintEngine:
        return self._lint_engine

    def __init__(
        self,
        config: ImportConfig,
        lint_engnie: LintEngine,
    ) -> None:
        self._config = config
        self._lint_engine = lint_engnie
        return

    def _fix_lines(
        self,
        lines: List[str],
        unused_imports: List[str],
        undefined_names: List[str],
    ) -> List[str]:
        # remove duplicate entries
        unused_imports = list(dict.fromkeys(unused_imports))
        undefined_names = list(dict.fromkeys(undefined_names))

        # get import blocks
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

        # Merget the imports
        merged_import_sentences = [
            ImportSentence.merge_list(removed_import_sentences)
            for removed_import_sentences in removed_import_sentences_lst
        ]

        # constructing resulting lines
        res_lines: List[str] = []

        fitst_line_num = get_first_line_num(lines)

        # add lines before import as it is
        if not begin_end_indices:
            res_lines += lines[:fitst_line_num]
        else:
            res_lines += lines[:begin_end_indices[0][0]]

        # add organized import blocks
        for i, merged_import_sentence in enumerate(
            merged_import_sentences
        ):
            for import_sentence in merged_import_sentence:
                res_lines += import_sentence.to_lines()
            if i < len(merged_import_sentences) - 1:
                res_lines.append('')

        # add lines after import as it is
        if not begin_end_indices:
            res_lines += lines[fitst_line_num:]
        else:
            res_lines += lines[begin_end_indices[-1][1]:]
        return res_lines

    def fix_lines(self, lines: List[str]) -> List[str]:
        lint_job = sp.run(
            self.lint_engine.get_cmd_piped(),
            shell=True,
            input='\n'.join(lines).encode('utf-8'),
            stdout=sp.PIPE,
            stderr=sp.DEVNULL,
        )

        # Extract result
        lint_output = lint_job.stdout.decode('utf-8')

        # Parse output
        unused_imports, undefined_names = self.lint_engine.parse_output(
            lint_output,
        )

        fixed_lines = self._fix_lines(
            lines,
            unused_imports,
            undefined_names,
        )
        return fixed_lines

    def print_fixed_content(self, file_path: str) -> None:
        lint_job = sp.run(
            self.lint_engine.get_cmd_filepath(file_path),
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.DEVNULL,
        )

        # Extract result
        lint_output = lint_job.stdout.decode('utf-8')

        # Parse output
        unused_imports, undefined_names = self.lint_engine.parse_output(
            lint_output,
        )

        # Fix line of codes
        with open(file_path) as f:
            lines = [line.strip() for line in f.readlines()]

        fixed_lines = self._fix_lines(
            lines,
            unused_imports,
            undefined_names,
        )
        for fixed_line in fixed_lines:
            print(fixed_line)
