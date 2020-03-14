import unittest

from nayvy.importing.flake8 import Flake8Result


class TestFlake8Result(unittest.TestCase):

    def test_of_line(self) -> None:
        # init of F401
        res = Flake8Result.of_line(
            "tmp.py:1:1: F401 'pprint.pprint as pp' imported but unused"
        )
        assert res is not None
        assert res.error_msg == "'pprint.pprint as pp' imported but unused"
        assert res.get_unused_import() == 'pprint.pprint as pp'
        assert res.get_undefined_name() is None

        # init of 821
        res = Flake8Result.of_line(
            "tmp.py:4:1: F821 undefined name 'sp'"
        )
        assert res is not None
        assert res.error_msg == "undefined name 'sp'"
        assert res.get_unused_import() is None
        assert res.get_undefined_name() == 'sp'
        return
