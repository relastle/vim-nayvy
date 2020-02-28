import unittest
from typing import List

from pydra.models.imprt import ImportAsPart, ImportSentence


class TestImportAsPart(unittest.TestCase):

    def test_of(self) -> None:
        # named import
        res = ImportAsPart.of('tensorflow as tf')
        assert res is not None
        assert res.import_what == 'tensorflow'
        assert res.as_what == 'tf'

        # non-named import
        res = ImportAsPart.of('sys')
        assert res is not None
        assert res.import_what == 'sys'
        assert res.as_what == ''
        return


class TestImportSentence(unittest.TestCase):

    def test_of(self) -> None:
        # just import
        res = ImportSentence.of('import tensorflow as tf')
        assert res is not None
        assert res.from_what == ''
        assert len(res.import_as_parts) == 1
        assert res.import_as_parts[0].import_what == 'tensorflow'
        assert res.import_as_parts[0].as_what == 'tf'

        # from import
        res = ImportSentence.of('from typing import Dict, List, Optional')
        assert res is not None
        assert res.from_what == 'typing'
        assert len(res.import_as_parts) == 3
        assert res.import_as_parts[0].import_what == 'Dict'
        assert res.import_as_parts[2].as_what == ''

        # complex pattern
        res = ImportSentence.of('from   typing  import (  Dict, List, Optional,  ) ')  # noqa
        assert res is not None
        assert res.from_what == 'typing'
        assert len(res.import_as_parts) == 3
        assert res.import_as_parts[0].import_what == 'Dict'
        assert res.import_as_parts[2].as_what == ''

    def test_merge(self) -> None:
        # merge if from_what is the same
        import_sentence = ImportSentence(
            'hoge',
            [
                    ImportAsPart('AAA', 'a'),
                    ImportAsPart('BBB', 'b'),
            ],
        )
        target = ImportSentence(
            'hoge',
            [
                ImportAsPart('BBB', 'b'),
                ImportAsPart('CCC', 'c'),
            ]
        )
        import_sentence.merge(target)
        assert len(import_sentence.import_as_parts) == 3

        # not merge if from_what is not the same
        import_sentence = ImportSentence(
            'hoge',
            [
                    ImportAsPart('AAA', 'a'),
                    ImportAsPart('BBB', 'b'),
            ],
        )
        target = ImportSentence(
            'fuga',
            [
                ImportAsPart('BBB', 'b'),
                ImportAsPart('CCC', 'c'),
            ]
        )
        import_sentence.merge(target)
        assert len(import_sentence.import_as_parts) == 2

    def test_removed(self) -> None:
        import_sentence = ImportSentence(
            'hoge',
            [
                    ImportAsPart('AAA', 'a'),
                    ImportAsPart('BBB', 'b'),
                    ImportAsPart('c', ''),
            ],
        )

        # remove as-imported name
        removed = import_sentence.removed('a')
        assert removed is not None

        # remove no-as-import name
        removed = removed.removed('c')
        assert removed is not None

        # assert that one import is remained
        assert len(removed.import_as_parts) == 1
        assert removed.import_as_parts[0].name == 'b'

        # remove the last one
        removed = removed.removed('b')
        assert removed is None
        return

    def test_merge_list(self) -> None:
        import_sentences = [
            ImportSentence(
                'hoge',
                [
                    ImportAsPart('AAA', 'a'),
                    ImportAsPart('BBB', 'b'),
                ]
            ),
            ImportSentence(
                'fuga',
                [
                    ImportAsPart('AAA', 'a'),
                    ImportAsPart('BBB', 'b'),
                ]
            ),
            ImportSentence(
                'hoge',
                [
                    ImportAsPart('CCC', 'c'),
                    ImportAsPart('DDD', 'd'),
                ]
            ),
        ]
        actuals = ImportSentence.merge_list(import_sentences)
        expecteds = [
            ImportSentence(
                'hoge',
                [
                    ImportAsPart('AAA', 'a'),
                    ImportAsPart('BBB', 'b'),
                    ImportAsPart('CCC', 'c'),
                    ImportAsPart('DDD', 'd'),
                ]
            ),
            ImportSentence(
                'fuga',
                [
                    ImportAsPart('AAA', 'a'),
                    ImportAsPart('BBB', 'b'),
                ]
            ),
        ]
        assert len(actuals) == len(expecteds)
        assert all([
            str(a) == str(e)
            for a, e in zip(actuals, expecteds)
        ]) is True

    def test_get_all_imprts(self) -> None:
        lines = [
            'import os',
            'import sys',
            'from pprint import ('
            '    pprint as pp,',
            '    pformat,',
            ')',
            'from typing import (',
            '    List as L,',
            '    Dict as D,',
            ')',
            '',
            'import tensorflow as tf',
        ]
        actuals = ImportSentence.get_all_imprts(lines)
        expecteds: List[ImportSentence] = [
            ImportSentence(
                '',
                [
                    ImportAsPart('os', ''),
                ],
            ),
            ImportSentence(
                '',
                [
                    ImportAsPart('sys', ''),
                ],
            ),
            ImportSentence(
                'pprint',
                [
                    ImportAsPart('pprint', 'pp'),
                    ImportAsPart('pformat', ''),
                ],
            ),
            ImportSentence(
                'typing',
                [
                    ImportAsPart('List', 'L'),
                    ImportAsPart('Dict', 'D'),
                ],
            ),
            ImportSentence(
                '',
                [
                    ImportAsPart('tensorflow', 'tf'),
                ],
            ),

        ]

        assert actuals is not None
        assert len(actuals) == len(expecteds)
        assert all([
            str(a) == str(e)
            for a, e in zip(actuals, expecteds)
        ]) is True
        return
