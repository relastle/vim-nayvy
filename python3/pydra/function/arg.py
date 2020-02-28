'''
Module for manipulating arg (of function)
'''
from typing import List


# The code is inspired by https://github.com/honza/vim-snippets
class Arg:
    '''
    Domain object of one argument of `Function`,
    '''

    @property
    def arg_str(self) -> str:
        return self._arg_str

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    def __init__(self, arg_str: str) -> None:
        self._arg_str = arg_str
        name_and_type = arg_str.split('=')[0].split(':')
        self._name = name_and_type[0].strip()
        if len(name_and_type) == 2:
            self._type = name_and_type[1].strip()
        else:
            self._type = 'None'

    def is_kwarg(self) -> bool:
        return '=' in self.arg_str

    def is_vararg(self) -> bool:
        return '*' in self.name

    def make_assignment_stmt(self) -> str:
        '''make assignment statment usually written in a initializer

        This makes assignment to single-under-scored `_`
        prefixed-member variable. (i.g. self._name = name)
        '''
        return 'self._{} = {}'.format(
            self.name,
            self.name,
        )

    def make_docstring(self) -> str:
        '''make arg description scheme used in docstring'''
        return '{}:'.format(
            self.name,
        )

    def make_docstring_with_type(self) -> str:
        ''' `make_docstring` of type included version'''
        return '{} ({}):'.format(
            self.name,
            self.type,
        )

    @classmethod
    def parse_args(cls, argliststr: str) -> List['Arg']:
        square_bracket_level = 0
        argstr_lst: List[str] = []
        tmp_arg = ''
        for c in argliststr:
            if c == ',' and square_bracket_level == 0:
                argstr_lst.append(tmp_arg)
                tmp_arg = ''
                continue

            if c == '[':
                square_bracket_level += 1
            elif c == ']':
                square_bracket_level -= 1
            tmp_arg += c
        argstr_lst.append(tmp_arg)
        args = [
            Arg(argstr) for argstr in argstr_lst
            if argstr != 'self' and argstr.strip() != ''
        ]
        return args
