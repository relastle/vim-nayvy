import re
from abc import ABCMeta, abstractmethod
from typing import List, Optional

from .models import Class, Module, Function, FuncDeclType

PYTHON_STANDARD_INDENT = 4


def is_dunder(func_name: str) -> bool:
    return (
        func_name.startswith('__') and
        func_name.endswith('__')
    )


class ModuleLoader(metaclass=ABCMeta):

    @abstractmethod
    def load_module_from_path(
        self,
        module_filepath: str,
    ) -> Optional[Module]:
        raise NotImplementedError

    @abstractmethod
    def load_module_from_lines(
        self,
        lines: List[str],
    ) -> Optional[Module]:
        raise NotImplementedError


class SyntacticModuleLoader(ModuleLoader):
    """
    Implementation for ModuleLoader using
    only syntastic feature obtained from just line by line.
    """

    class SyntacticParser:

        CLASS_DECL_RE = r'^ *class +(?P<class_name>\w+)'
        INSTANCE_FUNC_DECL_RE = r'^ *def +(?P<function_name>\w+)\(self.*\)'
        CLASS_FUNC_DECL_RE = r'^ *def +(?P<function_name>\w+)\(cls.*\)'
        FUNCTION_DECL_RE = r'^ *def +(?P<function_name>\w+)\(.*\)'

        res_top_level_function: List[Function]
        res_classes: List[Class]

        buf_functions: List[Function]

        # buffer for multi line declarations
        buf_decl_line: str
        buf_exessive_paren_open: int
        buf_decl_indent: int
        buf_decl_begin: int

        buf_class_name: str
        buf_class_begin: int
        buf_class_indent: int

        buf_func_name: str
        buf_func_begin: int
        buf_func_decl_type: FuncDeclType
        buf_func_indent: int

        buf_empty_line_num: int

        current_indent: int
        processed_line_num: int

        def _clean_buf_class(self) -> None:
            self.buf_class_name = ''
            self.buf_class_begin = 0
            self.buf_class_indent = 0

        def _clean_buf_func(self) -> None:
            self.buf_func_name = ''
            self.buf_func_begin = 0
            self.buf_func_indent = 0
            self.buf_func_decl_type = FuncDeclType.TOP_LEVEL
            return

        def __init__(self) -> None:
            self.res_top_level_function = []
            self.res_classes = []

            self.buf_functions = []

            self.buf_decl_line = ''
            self.buf_exessive_paren_open = 0
            self.buf_decl_indent = 0
            self.buf_decl_begin = 0

            self._clean_buf_class()
            self._clean_buf_func()

            self.buf_empty_line_num = 0

            self.current_indent = 0
            self.processed_line_num = 0

        def get_indent(self, line: str) -> int:
            return len(line) - len(line.lstrip())

        def _starts_multi_line_buffer(self, line: str) -> bool:
            if (
                not line.lstrip().startswith('class') and
                not line.lstrip().startswith('def')
            ):
                return False

            par_open_count = line.count('(')
            par_close_count = line.count(')')
            if par_open_count == par_close_count:
                return False

            self.buf_decl_line += line.strip()
            self.buf_exessive_paren_open = par_open_count - par_close_count
            self.buf_decl_indent = self.current_indent
            self.buf_decl_begin = self.processed_line_num
            return True

        def _ends_multi_line_buffer(self, line: str) -> bool:
            self.buf_decl_line += line.strip()
            par_open_count = line.count('(')
            par_close_count = line.count(')')
            self.buf_exessive_paren_open += par_open_count - par_close_count
            if self.buf_exessive_paren_open > 0:
                return False
            return True

        def _check_closure(self) -> None:
            """ proccess related to change of indent
            """
            if not self.buf_class_name and not self.buf_func_name:
                # Nothing matters when no class or function
                # are read already
                return

            # check of top level function
            if (
                self.buf_func_name and
                self.buf_func_decl_type == FuncDeclType.TOP_LEVEL and
                self.current_indent <= self.buf_func_indent
            ):
                # append
                self.res_top_level_function.append(Function(
                    name=self.buf_func_name,
                    line_begin=self.buf_func_begin,
                    line_end=self.processed_line_num - self.buf_empty_line_num,
                    func_decl_type=self.buf_func_decl_type,
                ))
                self._clean_buf_func()

            # check instance or class method clusure
            if (
                self.buf_func_name and
                self.current_indent <= self.buf_func_indent
            ):
                # append
                self.buf_functions.append(Function(
                    name=self.buf_func_name,
                    line_begin=self.buf_func_begin,
                    line_end=self.processed_line_num - self.buf_empty_line_num,
                    func_decl_type=self.buf_func_decl_type,
                ))
                self._clean_buf_func()

            # check of class clusure
            if (
                self.buf_class_name and
                self.current_indent <= self.buf_class_indent
            ):
                self.res_classes.append(Class(
                    name=self.buf_class_name,
                    line_begin=self.buf_class_begin,
                    line_end=self.processed_line_num - self.buf_empty_line_num,
                    function_map={
                        f.name: f
                        for f in self.buf_functions
                    },
                ))
                self.buf_functions = []
                self._clean_buf_class()

        def _check_class_decl(
            self,
            line: str,
            begin: int,
            indent: int,
        ) -> bool:
            if self.buf_class_name:
                # if there already exists buffered class
                return False
            m = re.match(self.CLASS_DECL_RE, line)
            if m is None:
                return False
            class_name = m.group('class_name')
            self.buf_class_name = class_name
            self.buf_class_begin = begin
            self.buf_class_indent = indent
            return True

        def _check_instance_method_decl(
            self,
            line: str,
            begin: int,
            indent: int,
        ) -> bool:
            if self.buf_func_name:
                # if there already exists buffered function
                return False
            if indent != self.buf_class_indent + PYTHON_STANDARD_INDENT:
                # inappropriate indent as instance method
                return False
            m = re.match(self.INSTANCE_FUNC_DECL_RE, line)
            if m is None:
                return False
            function_name = m.group('function_name')
            if is_dunder(function_name):
                return True
            self.buf_func_name = function_name
            self.buf_func_begin = begin
            self.buf_func_decl_type = FuncDeclType.INSTANCE
            self.buf_func_indent = indent
            return True

        def _check_class_method_decl(
            self,
            line: str,
            begin: int,
            indent: int,
        ) -> bool:
            if self.buf_func_name:
                # if there already exists buffered function
                return False
            if indent != self.buf_class_indent + PYTHON_STANDARD_INDENT:
                # inappropriate indent as class method
                return False
            m = re.match(self.CLASS_FUNC_DECL_RE, line)
            if m is None:
                return False
            function_name = m.group('function_name')
            if is_dunder(function_name):
                return True
            self.buf_func_name = function_name
            self.buf_func_begin = begin
            self.buf_func_decl_type = FuncDeclType.CLASS
            self.buf_func_indent = indent
            return True

        def _check_other_function_decl(
            self,
            line: str,
            begin: int,
            indent: int,
        ) -> bool:
            if self.buf_func_name:
                return False
            m = re.match(self.FUNCTION_DECL_RE, line)
            if m is None:
                return False
            function_name = m.group('function_name')
            if is_dunder(function_name):
                return True
            self.buf_func_name = function_name
            self.buf_func_begin = begin
            self.buf_func_decl_type = FuncDeclType.TOP_LEVEL
            self.buf_func_indent = indent
            return True

        def _consume(self, line: str) -> None:
            if not line.strip():
                # empty line
                self.buf_empty_line_num += 1
                return

            indent = self.get_indent(line)
            self.current_indent = indent

            # check if multi line declarations starts.
            if (
                self._starts_multi_line_buffer(line)
            ):
                return

            # check if multi line declarations ends.
            if (
                self.buf_decl_line and
                not self._ends_multi_line_buffer(line)
            ):
                return

            self._check_closure()

            if self.buf_decl_line:
                args = (
                    self.buf_decl_line,
                    self.buf_decl_begin,
                    self.buf_decl_indent,
                )
                (
                    self._check_class_decl(*args) or
                    self._check_instance_method_decl(*args) or
                    self._check_class_method_decl(*args) or
                    self._check_other_function_decl(*args)
                )
                # clean up
                self.buf_decl_line = ''
                self.buf_decl_begin = 0
                self.buf_decl_indent = 0
            else:
                args = (
                    line,
                    self.processed_line_num,
                    self.current_indent,
                )
                (
                    self._check_class_decl(*args) or
                    self._check_instance_method_decl(*args) or
                    self._check_class_method_decl(*args) or
                    self._check_other_function_decl(*args)
                )

            # reset empty line counter
            self.buf_empty_line_num = 0
            return

        def consume(self, line: str) -> None:
            self._consume(line)
            self.processed_line_num += 1
            return

        def close(self) -> None:
            self.current_indent = 0
            self._check_closure()
            return

    def load_module_from_path(
        self,
        module_filepath: str,
    ) -> Optional[Module]:
        try:
            with open(module_filepath) as f:
                lines = f.readlines()
        except Exception:
            return None
        return self.load_module_from_lines(lines)

    def load_module_from_lines(
        self,
        lines: List[str],
    ) -> Optional[Module]:
        parser = self.SyntacticParser()
        for line in lines:
            parser.consume(line)
        parser.close()
        return Module(
            function_map={
                f.name: f for f in
                parser.res_top_level_function
            },
            class_map={
                _class.name: _class for _class in
                parser.res_classes
            },
        )
