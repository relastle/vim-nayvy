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


class SyntacticParser:

    CLASS_DECL_RE = r'^ *class +(?P<class_name>\w+)'
    INSTANCE_FUNC_DECL_RE = r'^ *(async *){0,1}def +(?P<function_name>\w+)\(self.*\)'
    CLASS_FUNC_DECL_RE = r'^ *(async *){0,1}def +(?P<function_name>\w+)\(cls.*\)'
    FUNCTION_DECL_RE = r'^ *(async *){0,1}def +(?P<function_name>\w+)\(.*\)'

    res_top_level_function: List[Function]
    res_classes: List[Class]

    buf_functions: List[Function]

    # buffer for multi line declarations
    buf_decl_line: str
    buf_exessive_paren_open: int
    buf_decl_indent: int
    buf_decl_begin: int
    buf_decl_lines: List[str]

    # Buffer for class
    buf_class_name: str
    buf_class_begin: int
    buf_class_indent: int
    buf_class_docstring: str
    buf_class_lines: List[str]

    # Buffer for function
    buf_func_name: str
    buf_func_begin: int
    buf_func_decl_type: FuncDeclType
    buf_func_indent: int
    buf_func_docstring: str
    buf_func_lines: List[str]

    # Flag for declaration of class/function is fount
    # to wait for following docstring
    buf_found_decl: bool
    buf_in_docstring: bool

    buf_empty_line_num: int

    current_indent: int
    processed_line_num: int

    def _clean_buf_class(self) -> None:
        self.buf_class_name = ''
        self.buf_class_begin = 0
        self.buf_class_indent = 0
        self.buf_class_docstring = ''
        self.buf_class_lines = []
        return

    def _clean_buf_func(self) -> None:
        self.buf_func_name = ''
        self.buf_func_begin = 0
        self.buf_func_indent = 0
        self.buf_func_decl_type = FuncDeclType.TOP_LEVEL
        self.buf_func_docstring = ''
        self.buf_func_lines = []
        return

    def __init__(self) -> None:
        self.res_top_level_function = []
        self.res_classes = []

        self.buf_functions = []

        self.buf_decl_line = ''
        self.buf_decl_lines = []
        self.buf_exessive_paren_open = 0
        self.buf_decl_indent = 0
        self.buf_decl_begin = 0

        self._clean_buf_class()
        self._clean_buf_func()

        self.buf_found_decl = False
        self.buf_in_docstring = False

        self.buf_empty_line_num = 0

        self.current_indent = 0
        self.processed_line_num = 0
        return

    def get_indent(self, line: str) -> int:
        return len(line) - len(line.lstrip())

    def _lstrip_indent(self, line: str, indent: int) -> str:
        prefix = ' ' * indent
        if line.startswith(prefix):
            return line[len(prefix):]
        else:
            return line[:]

    def _lstrip_indent_for_lines(self, lines: List[str], indent: int) -> List[str]:
        return [
            self._lstrip_indent(line, indent)
            for line in lines
        ]

    def _start_multi_line_decl(self, line: str) -> bool:
        if (
            not line.lstrip().startswith('class') and
            not line.lstrip().startswith('def') and
            not line.lstrip().startswith('async def')
        ):
            return False

        par_open_count = line.count('(')
        par_close_count = line.count(')')
        if par_open_count == par_close_count:
            return False

        self.buf_decl_line += line.strip()
        self.buf_decl_lines.append(line.rstrip())
        self.buf_exessive_paren_open = par_open_count - par_close_count
        self.buf_decl_indent = self.current_indent
        self.buf_decl_begin = self.processed_line_num
        return True

    def _ends_multi_line_decl(self, line: str) -> bool:
        self.buf_decl_line += line.strip()
        self.buf_decl_lines.append(line.rstrip())
        par_open_count = line.count('(')
        par_close_count = line.count(')')
        self.buf_exessive_paren_open += par_open_count - par_close_count
        if self.buf_exessive_paren_open > 0:
            return False
        return True

    def _check_docstring(self, line: str) -> None:
        # Starts of docstring
        if (
            self.buf_found_decl and
            not self.buf_in_docstring and
            line.lstrip().startswith('"""')
        ):
            # Add docstring to buffered string.
            if self.buf_func_name:
                self.buf_func_docstring += line.replace('"""', '').lstrip()
                self.buf_func_lines.append(line.rstrip())
            elif self.buf_class_name:
                self.buf_class_docstring += line.replace('"""', '').lstrip()
                self.buf_class_lines.append(line.rstrip())
            self.buf_in_docstring = True
            self.buf_found_decl = False
            return

        # Right after the declaration and docstring start is not found.
        if self.buf_found_decl:
            self.buf_found_decl = False
            return

        # Ends of docstring
        if self.buf_in_docstring and line.rstrip().endswith('"""'):
            # Add docstring to buffered string.
            if self.buf_func_name:
                self.buf_func_docstring += line.replace('"""', '').strip()
                self.buf_func_lines.append(line.rstrip())
            elif self.buf_class_name:
                self.buf_class_docstring += line.replace('"""', '').strip()
                self.buf_class_lines.append(line.rstrip())
            self.buf_in_docstring = False
            return

        # Inside the docstring (continueing).
        if self.buf_in_docstring:
            if self.buf_func_name:
                self.buf_func_docstring += line.lstrip()
                self.buf_func_lines.append(line.rstrip())
            elif self.buf_class_name:
                self.buf_class_docstring += line.lstrip()
                self.buf_class_lines.append(line.rstrip())
            return

    def _check_closure(self) -> bool:
        """
        Check if current opned (Function|Class) Declaration is closed
        by detecting the same indentation of the declared (Function|Class).

        Implementation memo:

        def hoge() -> None:
            pass
        ⬆
        ︙ The number of empty line between declarations in the same indent
        ︙ is important to define the END of function.
        ⬇
        def fuga() -> None:
            pass
        """
        if not self.buf_class_name and not self.buf_func_name:
            # Nothing matters when no class or function
            # are read already
            False

        # Flag for remembering there is at least one closure.
        closed_some: bool = False

        # check of top level function
        if (
            self.buf_func_name and
            self.buf_func_decl_type == FuncDeclType.TOP_LEVEL and
            self.current_indent <= self.buf_func_indent
        ):
            # append
            self.res_top_level_function.append(Function(
                name=self.buf_func_name,
                docstring=self.buf_func_docstring,
                line_begin=self.buf_func_begin,
                line_end=self.processed_line_num - self.buf_empty_line_num,
                func_decl_type=self.buf_func_decl_type,
                signature_lines=self._lstrip_indent_for_lines(
                    self.buf_func_lines,
                    self.buf_func_indent,
                ),
            ))
            self._clean_buf_func()
            closed_some = True

        # check instance or class method clusure
        if (
            self.buf_func_name and
            self.current_indent <= self.buf_func_indent
        ):
            # append
            self.buf_functions.append(Function(
                name=self.buf_func_name,
                docstring=self.buf_func_docstring,
                line_begin=self.buf_func_begin,
                line_end=self.processed_line_num - self.buf_empty_line_num,
                func_decl_type=self.buf_func_decl_type,
                signature_lines=self._lstrip_indent_for_lines(
                    self.buf_func_lines,
                    self.buf_func_indent,
                ),
            ))
            self._clean_buf_func()
            closed_some = True

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
                signature_lines=self._lstrip_indent_for_lines(
                    self.buf_class_lines,
                    self.buf_class_indent,
                ),
            ))
            self.buf_functions = []
            self._clean_buf_class()
            closed_some = True
        return closed_some

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
        if self.buf_decl_lines:
            self.buf_class_lines = list(self.buf_decl_lines)
        else:
            self.buf_class_lines = [line.rstrip()]
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
        if self.buf_decl_lines:
            self.buf_func_lines = list(self.buf_decl_lines)
        else:
            self.buf_func_lines = [line.rstrip()]
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
        if self.buf_decl_lines:
            self.buf_func_lines = list(self.buf_decl_lines)
        else:
            self.buf_func_lines = [line.rstrip()]
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
        if self.buf_decl_lines:
            self.buf_func_lines = list(self.buf_decl_lines)
        else:
            self.buf_func_lines = [line.rstrip()]
        return True

    def _consume(self, line: str) -> None:
        indent = self.get_indent(line)
        if (not line.strip() and not self.buf_in_docstring):
            self.buf_empty_line_num += 1
            return
        elif not line.strip():
            indent = int(1e+3)

        self.current_indent = indent

        # check if multi line declarations starts.
        if self._start_multi_line_decl(line):
            return

        # check if multi line declarations ends.
        if (self.buf_decl_line and not self._ends_multi_line_decl(line)):
            # multiline declaratoin is continueing.
            return

        self._check_docstring(line)

        self._check_closure()

        if self.buf_decl_line:
            # If the are buffered declared multiple lines.
            args = (
                self.buf_decl_line,
                self.buf_decl_begin,
                self.buf_decl_indent,
            )
            if (
                self._check_class_decl(*args) or
                self._check_instance_method_decl(*args) or
                self._check_class_method_decl(*args) or
                self._check_other_function_decl(*args)
            ):
                self.buf_found_decl = True
            # clean up
            self.buf_decl_line = ''
            self.buf_decl_lines = []
            self.buf_decl_begin = 0
            self.buf_decl_indent = 0
        else:
            # Check simple one-line funcsion/class declaration.
            args = (
                line,
                self.processed_line_num,
                self.current_indent,
            )
            if (
                self._check_class_decl(*args) or
                self._check_instance_method_decl(*args) or
                self._check_class_method_decl(*args) or
                self._check_other_function_decl(*args)
            ):
                self.buf_found_decl = True
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


class SyntacticModuleLoader(ModuleLoader):
    """
    Implementation for ModuleLoader using
    only syntastic feature obtained from just line by line.
    """

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
        parser = SyntacticParser()
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
