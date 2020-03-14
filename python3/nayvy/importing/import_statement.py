import re
from typing import List, Optional
from dataclasses import dataclass

from ..utils.colors import Color


class ImportAsPart:

    IMPORT_AS_RE = r'(?P<import>[\w\.]+)( +as +(?P<as>[\w\.]+)){0,1}( *#(?P<comment>.*)){0,1}'  # noqa

    @property
    def import_what(self) -> str:
        return self._import_what

    @property
    def as_what(self) -> str:
        return self._as_what

    @property
    def comment(self) -> str:
        return self._comment.strip()

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

    def __init__(
        self,
        import_what: str,
        as_what: str,
        comment: str = '',
    ) -> None:
        self._import_what = import_what
        self._as_what = as_what
        self._comment = comment
        return

    @classmethod
    def of(cls, s: str) -> Optional['ImportAsPart']:
        m = re.match(cls.IMPORT_AS_RE, s)
        if m is None:
            return None
        import_what = m.group('import')
        as_what = m.group('as')
        if as_what is None:
            as_what = ''
        comment = m.group('comment')
        if comment is None:
            comment = ''
        return ImportAsPart(import_what, as_what, comment)

    def __repr__(self) -> str:
        return '{}{}{}'.format(
            self.import_what,
            ' as {}'.format(self.as_what) if self.as_what else '',
            '  # {}'.format(self.comment) if self.comment else '',
        )


class ImportStatement:

    FROM_IMPORT_STATEMENT_RE = r'from +(?P<from>[\w\.]+) +import +(?P<other>.*)'

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
    def of(cls, s: str) -> Optional['ImportStatement']:
        s = s.replace('(', '').replace(')', '')
        s = s.strip()
        s = s.strip(',')
        if s.startswith('import '):
            import_as_part = ImportAsPart.of(s.replace('import ', ''))
            if import_as_part is None:
                return None
            return ImportStatement(
                '',
                [import_as_part],
            )
        m = re.match(cls.FROM_IMPORT_STATEMENT_RE, s)
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
        return ImportStatement(
            from_what,
            import_as_parts,
        )

    def merge(self, import_statement: 'ImportStatement') -> bool:
        ''' merge import_statement to self if possible
        '''
        if str(self) == str(import_statement):
            # is completely same, assume that merged successfully
            return True

        if self.from_what == '':
            # if no-from statement, merge is impossible
            return False

        if not self.from_what == import_statement.from_what:
            return False

        self_import_as_part_strs = [
            str(import_as_part)
            for import_as_part in self.import_as_parts
        ]

        for import_as_part in import_statement.import_as_parts:
            if str(import_as_part) not in self_import_as_part_strs:
                self.import_as_parts.append(import_as_part)
        return True

    def removed(self, import_name: str) -> Optional['ImportStatement']:
        if self.from_what == '':
            if self._import_as_parts[0].import_name == import_name:
                return None
            else:
                return ImportStatement(
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
        return ImportStatement(
            self.from_what,
            res_import_as_parts,
        )

    def get_single_statement(
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

    def to_lines(self) -> List[str]:
        return str(self).split('\n')

    def __repr__(self) -> str:
        if self.from_what == '':
            # Just a one line import without from
            return 'import {}'.format(
                self.import_as_parts[0],
            )

        if any(
            import_as_part.comment
            for import_as_part in self.import_as_parts
        ):
            # If any is commented no grouping
            return '\n'.join([
                'from {} import {}'.format(
                    self.from_what,
                    str(import_as_part),
                )
                for import_as_part in sorted(
                    self.import_as_parts,
                    key=lambda x: x.name
                )
            ])

        # represents with commna-seperated
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
        import_statements: List['ImportStatement'],
    ) -> List['ImportStatement']:
        ''' Merge multiple import_statements

        if some ImportStatement objects share `from_what`,
        they are merged correctly
        '''
        merged_import_statements: List['ImportStatement'] = []
        for import_statement in import_statements:
            for merged in merged_import_statements:
                merge_success = merged.merge(import_statement)
                if merge_success:
                    break
            else:
                merged_import_statements.append(import_statement)
        return merged_import_statements

    @classmethod
    def get_removed_lst(
        cls,
        import_statements: List['ImportStatement'],
        import_names: List[str],
    ) -> List['ImportStatement']:
        ''' Remove certain name import from import_statements
        '''
        for name in import_names:
            import_statements = [
                maybe for maybe in
                (
                    import_statement.removed(name)
                    for import_statement in import_statements
                )
                if maybe is not None
            ]
        return import_statements

    @classmethod
    def of_lines(
        cls,
        lines: List[str],
    ) -> Optional[List['ImportStatement']]:
        '''
        Create list of `ImportStatement` List
        from lines( real python code)
        '''
        import_statement_lines = []
        line_coutinuous = False
        line_tmp = ''
        comment_tmp = ''
        excessive_open_paren = 0
        for line in lines:
            if (
                not line_coutinuous and
                not line.startswith('from') and
                not line.startswith('import') and
                not line.startswith('#')
            ):
                # Skip irrelevant line
                continue

            line = line.strip()

            only_comment = line.startswith('#')

            # handle the comment
            COMMENT_RE = r'#.*$'
            comment_m = re.search(COMMENT_RE, line)
            if comment_m is not None:
                line = re.sub(COMMENT_RE, '', line).strip()
                comment = comment_m.group().lstrip('#')
            else:
                comment = ''

            comment_tmp += comment

            if only_comment:
                continue

            # calculate parenthesis for line continuation
            excessive_open_paren += line.count('(')
            excessive_open_paren -= line.count(')')

            if excessive_open_paren < 0:
                # illegal
                return None
            elif excessive_open_paren == 0:
                # when import statement is completed
                # with the number of open parenthesis 0
                line_completed = '{}{}'.format(
                    line_tmp + line,
                    '# ' + comment_tmp if comment_tmp else '',
                )
                import_statement_lines.append(
                    line_completed
                )
                line_coutinuous = False
                line_tmp = ''
                comment_tmp = ''

            else:
                # open parenthesis is excessive,
                if line.endswith(','):
                    line = '{}{}{}'.format(
                        line.rstrip(','),
                        '# ' + comment_tmp if comment_tmp else '',
                        ',',
                    )
                    comment_tmp = ''
                line_coutinuous = True
                line_tmp += line
        # Construct return value
        import_statements = []
        for line in import_statement_lines:
            import_statement = ImportStatement.of(line)
            if import_statement is not None:
                import_statements.append(import_statement)
        return import_statements


@dataclass(frozen=True)
class SingleImport:

    name: str
    statement: str
    level: int

    def to_line(self, color: bool = False) -> str:
        """ Convert object to line selected by fzf
        """
        if color:
            return '{}{}{} : {}'.format(
                Color.GREEN,
                self.name,
                Color.RESET,
                self.statement,
            )
        else:
            return '{} : {}'.format(
                self.name,
                self.statement,
            )
