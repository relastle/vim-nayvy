from typing import Dict, Optional
import json


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
    def of_jsonfile(cls, json_path: str) -> Optional['ImportConfig']:
        with open(json_path) as json_f:
            json_d = json.load(json_f)
        if 'import' not in json_d:
            return None
        import_d: Dict[str, SingleImport] = {}
        for single_import_d in json_d['import']:
            import_d[single_import_d['name']] = SingleImport(
                single_import_d['name'],
                single_import_d['sentence'],
                single_import_d['level'],
            )
        return ImportConfig(import_d)
