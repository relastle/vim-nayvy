'''
Fix the python lines of code dependent on flake8 result
'''

from typing import List

from .utils import get_import_block_indices
from .import_config import ImportConfig
from .import_sentence import ImportSentence


class Fixer:

    @property
    def config(self) -> ImportConfig:
        return self._config

    def __init__(self, config: ImportConfig) -> None:
        self._config = config
        return

    def parse_flake8_output(self) -> None:
        # TODO
        pass

    def fix_lines(
        self,
        lines: List[str],
        unused_names: List[str],
        not_defined_names: List[str],
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
            ImportSentence.get_removed_lst(import_sentences, unused_names)
            for import_sentences in import_sentences_lst
        ]

        # add not defined names
        for not_defined_name in not_defined_names:
            single_import = self.config.import_d.get(not_defined_name, None)
            if single_import is None:
                continue
            added_import_sentence = ImportSentence.of(single_import.sentence)
            if added_import_sentence is None:
                return lines
            removed_import_sentences_lst[single_import.level].append(
                added_import_sentence
            )

        # constructing resulting lines
        res_lines: List[str] = []

        res_lines += lines[:begin_end_indices[0][0]]
        for i, removed_import_sentences in enumerate(
            removed_import_sentences_lst
        ):
            for import_sentence in removed_import_sentences:
                res_lines.append(str(import_sentence))
            if i < len(removed_import_sentences_lst) - 1:
                res_lines.append('')
        res_lines += lines[begin_end_indices[-1][1]:]
        return res_lines
