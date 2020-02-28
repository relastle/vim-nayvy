from typing import Dict, Optional
import json

from .import_sentence import ImportSentence


class ImportConfig:

    @property
    def import_d(self) -> Dict[str, ImportSentence]:
        return self._import_d

    def __init__(self, import_d:  Dict[str, ImportSentence]) -> None:
        self._import_d = import_d
        return

    @classmethod
    def of_jsonfile(cls, json_path: str) -> Optional['ImportConfig']:
        with open(json_path) as json_f:
            json_d = json.load(json_f)
        if 'import' not in json_d:
            return None
        import_d: Dict[str, ImportSentence] = {}
        for k, v in json_d.items():
            import_sentence = ImportSentence.of(v)
            if import_sentence is not None:
                import_d[k] = import_sentence
        return ImportConfig(import_d)
