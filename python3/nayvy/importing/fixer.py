'''
Fix the python lines of code dependent on Linter result
'''

import subprocess as sp
from abc import ABCMeta, abstractmethod
from typing import Any, List, Tuple, Optional, Generator
from dataclasses import dataclass

from .utils import get_first_line_num, get_import_block_indices
from .import_statement import SingleImport, ImportStatement


class LintEngine(metaclass=ABCMeta):
    """
    Interface for make linting engine such as Pyflakes and flake8
    abstract.
    """

    @abstractmethod
    def get_cmd_piped(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_cmd_filepath(self, file_path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def parse_output(self, output: str) -> Tuple[List[str], List[str]]:
        raise NotImplementedError


class ImportStatementMap(metaclass=ABCMeta):
    """ Interface for providing import statement mapping.
    """

    @abstractmethod
    def __getitem__(self, name: str) -> Optional[SingleImport]:
        raise NotImplementedError

    @abstractmethod
    def items(self) -> Generator[Tuple[str, SingleImport], Any, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class Fixer:

    import_stmt_map: ImportStatementMap
    lint_engine: LintEngine

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

        # get import_statements for each block
        maybe_import_statements_lst = [
            ImportStatement.of_lines(lines[begin_index:end_index])
            for begin_index, end_index in begin_end_indices
        ]

        import_statements_lst = []
        for maybe in maybe_import_statements_lst:
            if maybe is not None:
                import_statements_lst.append(maybe)

        # remove unused names from import_statements
        removed_import_statements_lst = [
            ImportStatement.get_removed_lst(import_statements, unused_imports)
            for import_statements in import_statements_lst
        ]

        # Constructing not-None single import list
        imports_to_add: List[SingleImport] = []
        for undefined_name in undefined_names:
            single_import = self.import_stmt_map[undefined_name]
            if single_import is None:
                continue
            imports_to_add.append(single_import)

        # sort by import block level
        imports_to_add = sorted(imports_to_add, key=lambda x: x.level)

        # constructing import import statements
        for import_to_add in imports_to_add:
            import_statement_to_add = ImportStatement.of(
                import_to_add.statement)
            if import_statement_to_add is None:
                continue
            if len(removed_import_statements_lst) <= import_to_add.level:
                removed_import_statements_lst.append([import_statement_to_add])
            else:
                removed_import_statements_lst[import_to_add.level].append(
                    import_statement_to_add
                )

        # Merget the imports
        merged_import_statements = [
            ImportStatement.merge_list(removed_import_statements)
            for removed_import_statements in removed_import_statements_lst
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
        for i, merged_import_statement in enumerate(
            merged_import_statements
        ):
            for import_statement in merged_import_statement:
                res_lines += import_statement.to_lines()
            if i < len(merged_import_statements) - 1:
                res_lines.append('')

        # add lines after import as it is
        if not begin_end_indices:
            res_lines += lines[fitst_line_num:]
        else:
            res_lines += lines[begin_end_indices[-1][1]:]
        return res_lines

    def fix_lines(self, lines: List[str]) -> Optional[List[str]]:
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

        if not undefined_names and not undefined_names:
            # If there is no problem, return None
            # for prevent vim from updating buffer.
            return None

        fixed_lines = self._fix_lines(
            lines,
            unused_imports,
            undefined_names,
        )
        return fixed_lines

    def add_imports(
        self,
        lines: List[str],
        names: List[str],
    ) -> List[str]:
        ''' add import by names
        '''
        return self._fix_lines(lines, [], names)

    def print_fixed_content(self, file_path: str) -> None:
        with open(file_path) as f:
            lines = [line.strip() for line in f.readlines()]

        fixed_lines = self.fix_lines(lines)
        if fixed_lines is None:
            return None

        for fixed_line in fixed_lines:
            print(fixed_line)
