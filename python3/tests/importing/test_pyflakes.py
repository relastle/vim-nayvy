import unittest

from nayvy.importing.pyflakes import PyflakesResult


class TestFlake8Result(unittest.TestCase):

    def test_of_line(self) -> None:
        # warning of unused
        res = PyflakesResult.of_line(
            "tmp.py:1: 'pprint.pprint as pp' imported but unused"
        )
        assert res is not None
        assert res.error_msg == "'pprint.pprint as pp' imported but unused"
        assert res.get_unused_import() == 'pprint.pprint as pp'
        assert res.get_undefined_name() is None

        # warning of undefined
        res = PyflakesResult.of_line(
            "tmp.py:1: undefined name 'sys'"
        )
        assert res is not None
        assert res.error_msg == "undefined name 'sys'"
        assert res.get_unused_import() is None
        assert res.get_undefined_name() == 'sys'
        return
