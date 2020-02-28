'''
Module for manipulating import statements
generally defiend in top of the script.
'''
import json
import re
from typing import List, Tuple, Optional, Dict


class ImportAsPart:

    IMPORT_AS_RE = r'(?P<import>[\w\.]+)( +as +(?P<as>[\w\.]+)){0,1}'

    @property
    def import_what(self) -> str:
        return self._import_what

    @property
    def as_what(self) -> str:
        return self._as_what

    @property
    def name(self) -> str:
        if self._as_what == '':
            return self.import_what
        else:
            return self._as_what

    def __init__(self, import_what: str, as_what: str) -> None:
        self._import_what = import_what
        self._as_what = as_what
        return

    @classmethod
    def of(cls, s: str) -> Optional['ImportAsPart']:
        m = re.match(cls.IMPORT_AS_RE, s)
        if m is None:
            return None
        import_what = m.group('import')
        if import_what is None:
            return None
        as_what = m.group('as')
        if as_what is None:
            as_what = ''
        return ImportAsPart(import_what, as_what)

    def __repr__(self) -> str:
        if self.as_what == '':
            return self.import_what
        else:
            return '{} as {}'.format(
                self.import_what,
                self.as_what,
            )


class ImportSentence:

    FROM_IMPORT_SENTENCE_RE = r'from +(?P<from>[\w\.]+) +import +(?P<other>.*)'

    @property
    def from_what(self) -> str:
        return self._from_what

    @property
    def import_as_parts(self) -> List[ImportAsPart]:
        return self._import_as_parts

    def __init__(
        self,
        from_what: str,
        import_as_parts: List[ImportAsPart],
    ) -> None:
        self._from_what = from_what
        self._import_as_parts = import_as_parts
        return

    @classmethod
    def of(cls, s: str) -> Optional['ImportSentence']:
        s = s.replace('(', '').replace(')', '')
        s = s.strip()
        s = s.strip(',')
        if s.startswith('import '):
            import_as_part = ImportAsPart.of(s.replace('import ', ''))
            if import_as_part is None:
                return None
            return ImportSentence(
                '',
                [import_as_part],
            )
        m = re.match(cls.FROM_IMPORT_SENTENCE_RE, s)
        if m is None:
            return None

        from_what = m.group('from')
        other = m.group('other')
        import_as_parts = []
        for elm in other.split(','):
            import_as_part = ImportAsPart.of(elm.strip())
            if import_as_part is None:
                return None
            import_as_parts.append(import_as_part)
        return ImportSentence(
            from_what,
            import_as_parts,
        )

    def merge(self, import_sentence: 'ImportSentence') -> bool:
        ''' merge import_sentence to self if possible
        '''
        if not self.from_what == import_sentence.from_what:
            return False

        self_import_as_part_strs = [
            str(import_as_part)
            for import_as_part in self.import_as_parts
        ]

        for import_as_part in import_sentence.import_as_parts:
            if str(import_as_part) not in self_import_as_part_strs:
                self.import_as_parts.append(import_as_part)
        return True

    def removed(self, name: str) -> Optional['ImportSentence']:
        if self.from_what == '':
            if self._import_as_parts[0].name == name:
                return None
            else:
                return ImportSentence(
                    self.from_what,
                    self.import_as_parts,
                )
        res_import_as_parts = []
        for import_as_part in self.import_as_parts:
            if not import_as_part.name == name:
                res_import_as_parts.append(import_as_part)
        if not res_import_as_parts:
            return None
        return ImportSentence(
            self.from_what,
            res_import_as_parts,
        )

    @classmethod
    def merge_list(
        cls,
        import_sentences: List['ImportSentence'],
    ) -> List['ImportSentence']:
        ''' Merge multiple import_sentences

        if some ImportSentence objects share `from_what`,
        they are merged correctly
        '''
        merged_import_sentences: List['ImportSentence'] = []
        for import_sentence in import_sentences:
            for merged in merged_import_sentences:
                merge_success = merged.merge(import_sentence)
                if merge_success:
                    break
            else:
                merged_import_sentences.append(import_sentence)
        return merged_import_sentences

    @classmethod
    def get_removed_lst(
        cls,
        import_sentences: List['ImportSentence'],
        name: str,
    ) -> List['ImportSentence']:
        ''' Remove certain name import from import_sentences
        '''
        return [
            maybe for maybe in
            (
                import_sentence.removed(name)
                for import_sentence in import_sentences
            )
            if maybe is not None
        ]

    @classmethod
    def get_all_imprts(
        cls,
        lines: List[str],
    ) -> Optional[List['ImportSentence']]:
        '''
        Create list of `ImportSentence` List
        from lines( real python code)
        '''
        import_sentence_lines = []
        line_coutinuous = False
        line_tmp = ''
        excessive_open_paren = 0
        for line in lines:
            if (
                not line_coutinuous and
                not line.startswith('from') and
                not line.startswith('import')
            ):
                # Skip irrelevant line
                continue

            line = line.strip()

            # calculate parenthesis for line continuation
            excessive_open_paren += line.count('(')
            excessive_open_paren -= line.count(')')

            if excessive_open_paren < 0:
                # illegal
                return None
            elif excessive_open_paren == 0:
                import_sentence_lines.append(
                    line_tmp + line
                )
                line_coutinuous = False
                line_tmp = ''
            else:
                line_coutinuous = True
                line_tmp += line

        # Construct return value
        import_sentences = []
        for line in import_sentence_lines:
            import_sentence = ImportSentence.of(line)
            if import_sentence is not None:
                import_sentences.append(import_sentence)
        return import_sentences

    def __repr__(self) -> str:
        if self.from_what == '':
            return 'import {}'.format(
                self.import_as_parts[0],
            )
        else:
            return 'from {} import {}'.format(
                self.from_what,
                ', '.join([
                    str(import_as_part)
                    for import_as_part in self.import_as_parts
                ]),
            )


class ImportConfig:

    @property
    def import_d(self) -> Dict[str, ImportSentence]:
        return self._import_d

    def __init__(self, import_d:  Dict[str, ImportSentence]) -> None:
        self._import_d = import_d
        return

    @classmethod
    def of_jsonfile(cls, json_path: str) -> Optional['ImportConfig']:
        with open(json_path) as json_f:
            json_d = json.load(json_f)
        if 'import' not in json_d:
            return None
        import_d: Dict[str, ImportSentence] = {}
        for k, v in json_d.items():
            import_sentence = ImportSentence.of(v)
            if import_sentence is not None:
                import_d[k] = import_sentence
        return ImportConfig(import_d)


def get_first_line_num(lines: List[str]) -> int:
    '''
    Return first python code line line line number(0-based)
    except for module DocString(__doc__)
    and shebang (#!/usr/bin/env python3)
    '''
    in_docstring = False
    try:
        for i, line in enumerate(lines):
            if in_docstring and line.startswith("'''"):
                in_docstring = False
                continue
            if (not in_docstring) and line.startswith("'''"):
                in_docstring = True
                continue
            if line.startswith('#'):
                continue
            if not in_docstring:
                return i
    except Exception:
        return 0
    return i


def already_exists(sentence: str, lines: List[str]) -> bool:
    '''
    Check if sentence is in lines
    '''
    return any(sentence in line.strip() for line in lines)


def get_import_block_indices(lines: List[str]) -> List[Tuple[int, int]]:
    '''
    Returns:
        [
            (1st block's start begin(inclusive), 1st block's end(exclusive)),
            (2nd block's start begin(inclusive), 2nd block's end(exclusive)),
            (3rd block's start begin(inclusive), 3rd block's end(exclusive)),
            ]
    '''
    res = []
    in_block = False
    try:
        for i, line in enumerate(lines):
            if (
                not in_block and
                (
                    line.startswith('import ') or
                    line.startswith('from ')
                )
            ):
                in_block = True
                start_index = i
                continue
            elif in_block and line == '':
                in_block = False
                res.append((start_index, i))
    except Exception:
        return res
    return res


def find_target_line_num(level: int, lines: List[str]) -> int:
    '''
    import文を探して、与えられたlevelのblockの最後の
    import文の次の行番号を返す(0-based-index)
    level:
        0 (標準ライブラリのimport)
        1 (third-partyライブラリのimport)
        2 (相対パスでのimportなどなど)
    '''
    if not (0 <= level and level <= 2):
        return -1
    import_block_indices = get_import_block_indices(lines)
    if len(import_block_indices) >= level + 1:
        # このときは素直に行挿入すればよい
        return import_block_indices[level][1]
    elif len(import_block_indices) == 0:
        # ブロックがそもそもないときは
        # コメントを抜かした一番上にimportするのがよい
        target_line = get_first_line_num(lines)
        if len(lines) >= target_line + 1 and lines[target_line] != '':
            lines[target_line:target_line] = ['']
        return target_line
    else:
        # 所与のブロックは見つからなかったがいくらかはあるとき
        # 存在しているブロックに空行付け加えて
        # 対処するのがよい
        target_line = import_block_indices[-1][1]
        lines[target_line:target_line] = ['']
        return target_line + 1
