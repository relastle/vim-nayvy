import unittest

from pydra.models.arg import Arg


class TestClass(unittest.TestCase):
    def test_arg_construction(self) -> None:
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
            arg = Arg(case['input_arg_str'])
            self.assertEqual(arg.name, case['expected_name'])
            self.assertEqual(arg.type, case['expected_type'])
        return

    def test_make_assignment_stmt(self) -> None:
        arg = Arg('name: Dict[str, Any]')
        assignment_stmt = arg.make_assignment_stmt()
        self.assertEqual(assignment_stmt, 'self._name = name')

    def test_make_docstring(self) -> None:
        arg = Arg('name: Dict[str, Any]')
        docstring = arg.make_docstring()
        self.assertEqual(docstring, 'name:')

    def test_make_docstring_with_type(self) -> None:
        arg = Arg('name: Dict[str, Any]')
        docstring = arg.make_docstring_with_type()
        self.assertEqual(docstring, 'name (Dict[str, Any]):')
