from typing import Dict, Optional, List
import os
import json

from .import_sentence import ImportSentence


class SingleImport:

    @property
    def name(self) -> str:
        return self._name

    @property
    def sentence(self) -> str:
        return self._sentence

    @property
    def level(self) -> int:
        return self._level

    def __init__(
        self,
        name: str,
        sentence: str,
        level: int,
    ) -> None:
        self._name = name
        self._sentence = sentence
        self._level = level
        return

    def __repr__(self) -> str:
        return json.dumps(self.__dict__, indent=2)


class ImportConfig:

    @property
    def import_d(self) -> Dict[str, SingleImport]:
        return self._import_d

    def __init__(self, import_d:  Dict[str, SingleImport]) -> None:
        self._import_d = import_d
        return

    @classmethod
    def init(cls) -> Optional['ImportConfig']:
        xdg_root = os.getenv(
            'XDG_CONFIG_HOME',
            '{}/.config'.format(
                os.environ['HOME']
            )
        )
        pydra_import_config_path = '{}/pydra/import_config.pydra'.format(
            xdg_root,
        )
        return cls._of_config_py(pydra_import_config_path)

    @classmethod
    def _of_config_py(cls, config_path: str) -> Optional['ImportConfig']:
        if not os.path.exists(config_path):
            return None

        blocks: List[List[str]] = []
        tmp_block: List[str] = []
        with open(config_path) as f:
            for line in f:
                if line.strip() == '':
                    blocks.append(tmp_block)
                    tmp_block = []
                else:
                    tmp_block.append(line.strip())
            if tmp_block:
                blocks.append(tmp_block)

        import_d: Dict[str, SingleImport] = {}
        for block_i, block in enumerate(blocks):
            import_sentences = ImportSentence.of_lines(block)
            if import_sentences is None:
                return None
            for import_sentence in import_sentences:
                for import_as_part in import_sentence.import_as_parts:
                    single_import = SingleImport(
                        import_as_part.name,
                        import_sentence.get_single_sentence(
                            import_as_part,
                        ),
                        block_i,
                    )
                    import_d[single_import.name] = single_import
        return ImportConfig(import_d)

    @classmethod
    def _of_jsonfile(cls, json_path: str) -> Optional['ImportConfig']:
        ''' DEPREDATED!! use `_of_config_py` instead'''
        with open(json_path) as json_f:
            json_d = json.load(json_f)
        if 'auto_import' not in json_d:
            return None
        import_d: Dict[str, SingleImport] = {}
        for single_import_d in json_d['auto_import']:
            import_d[single_import_d['name']] = SingleImport(
                single_import_d['name'],
                single_import_d['sentence'],
                single_import_d['level'],
            )
        return ImportConfig(import_d)
