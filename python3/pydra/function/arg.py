'''
Module for manipulating arg (of function)
'''
from typing import List
from dataclasses import dataclass


# The code is inspired by https://github.com/honza/vim-snippets
@dataclass
class Arg:
    '''
    Domain object of one argument of `Function`,
    '''

    arg_str: str
    name: str
    t: str

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
            self.t,
        )

    @classmethod
    def of(cls, arg_str: str) -> 'Arg':
        name_and_type = arg_str.split('=')[0].split(':')
        _name = name_and_type[0].strip()
        if len(name_and_type) == 2:
            _type = name_and_type[1].strip()
        else:
            _type = 'None'
        return Arg(
            arg_str,
            _name,
            _type,
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
        # strip arg_str
        argstr_lst = [
            argstr.strip() for argstr in argstr_lst
        ]
        args = [
            Arg.of(argstr) for argstr in argstr_lst
            if argstr != 'self' and argstr.strip() != ''
        ]
        return args
