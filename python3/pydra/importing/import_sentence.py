import re
from typing import List, Optional


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
        ''' name that can be referred in python code

        import subprocess as sp  --> 'sp'
        import tensorflow        --> 'tensorflow'
        '''
        if self._as_what == '':
            return self.import_what
        else:
            return self._as_what

    @property
    def import_name(self) -> str:
        ''' import name that can be referred by linter
        when it is unused in source code.

        import subprocess as sp   --> 'subprocess as sp'
        from numpy import ndarray --> 'ndarray'
        '''
        return str(self)

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

    def removed(self, import_name: str) -> Optional['ImportSentence']:
        if self.from_what == '':
            if self._import_as_parts[0].import_name == import_name:
                return None
            else:
                return ImportSentence(
                    self.from_what,
                    self.import_as_parts,
                )
        res_import_as_parts = []
        for import_as_part in self.import_as_parts:
            if not '{}.{}'.format(
                self.from_what,
                import_as_part.import_name
            ) == import_name:
                res_import_as_parts.append(import_as_part)
        if not res_import_as_parts:
            return None
        return ImportSentence(
            self.from_what,
            res_import_as_parts,
        )

    def get_single_sentence(
        self,
        import_as_part: ImportAsPart,
    ) -> str:
        if self.from_what == '':
            return 'import {}'.format(
                self.import_as_parts[0],
            )
        else:
            return 'from {} import {}'.format(
                self.from_what,
                str(import_as_part)
            )

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
                    for import_as_part in sorted(
                        self.import_as_parts,
                        key=lambda x: x.name
                    )
                ]),
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
        import_names: List[str],
    ) -> List['ImportSentence']:
        ''' Remove certain name import from import_sentences
        '''
        for name in import_names:
            import_sentences = [
                maybe for maybe in
                (
                    import_sentence.removed(name)
                    for import_sentence in import_sentences
                )
                if maybe is not None
            ]
        return import_sentences

    @classmethod
    def of_lines(
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
