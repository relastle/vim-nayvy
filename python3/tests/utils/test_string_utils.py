import unittest

from nayvy.utils.string_utils import remove_prefix, remove_suffix


class Test(unittest.TestCase):

    def test_remove_prefix(self) -> None:
        assert remove_prefix('test_hoge', 'test_') == 'hoge'
        return

    def test_remove_suffix(self) -> None:
        assert remove_suffix('hoge.py', '.py') == 'hoge'
        return
