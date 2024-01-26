import unittest

from nayvy.importing.ruff import RuffResult


class TestFlake8Result(unittest.TestCase):

    def test_of_line(self) -> None:
        # warning of unused
        res = RuffResult.of_line(
            "tmp.py:1: F401 [*] `pprint.pprint` imported but unused"
        )
        assert res is not None
        assert res.error_msg == "`pprint.pprint` imported but unused"
        assert res.get_unused_import() == 'pprint.pprint'
        assert res.get_undefined_name() is None

        # warning of undefined
        res = RuffResult.of_line(
            'tmp.py:4:1: F821 Undefined name `np`'
        )
        assert res is not None
        assert res.error_msg == "Undefined name `np`"
        assert res.get_unused_import() is None
        assert res.get_undefined_name() == 'np'
        return
