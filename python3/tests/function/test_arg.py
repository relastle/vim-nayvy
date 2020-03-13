import unittest

from pydra.function.arg import Arg


class TestArg(unittest.TestCase):

    def test_make_assignment_stmt(self) -> None:
        arg = Arg.of('name: Dict[str, Any]')
        assignment_stmt = arg.make_assignment_stmt()
        self.assertEqual(assignment_stmt, 'self._name = name')

    def test_make_docstring(self) -> None:
        arg = Arg.of('name: Dict[str, Any]')
        docstring = arg.make_docstring()
        self.assertEqual(docstring, 'name:')

    def test_make_docstring_with_type(self) -> None:
        arg = Arg.of('name: Dict[str, Any]')
        docstring = arg.make_docstring_with_type()
        self.assertEqual(docstring, 'name (Dict[str, Any]):')

    def test_of(self) -> None:
        cases = [
            {
                'input_arg_str': 'name',
                'expected_name': 'name',
                'expected_type': 'None',
            },
            {
                'input_arg_str': 'name: str',
                'expected_name': 'name',
                'expected_type': 'str',
            },
        ]

        for case in cases:
            arg = Arg.of(case['input_arg_str'])
            self.assertEqual(arg.name, case['expected_name'])
            self.assertEqual(arg.t, case['expected_type'])
        return

    def test_parse_args(self) -> None:
        given = 'a: int, b: str, c: Dict[str, Any]'
        actual = Arg.parse_args(given)
        assert actual == [
            Arg('a: int', 'a', 'int'),
            Arg('b: str', 'b', 'str'),
            Arg('c: Dict[str, Any]', 'c', 'Dict[str, Any]'),
        ]
        return
