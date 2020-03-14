from typing import List, Optional, Generator, Tuple, Any, Dict
import os

from .import_statement import ImportStatement, SingleImport
from .fixer import ImportStatementMap


class ImportConfig(ImportStatementMap):

    @property
    def import_d(self) -> Dict[str, SingleImport]:
        return self._import_d

    def __init__(self, import_d:  Dict[str, SingleImport]) -> None:
        self._import_d = import_d
        return

    def __getitem__(self, name: str) -> Optional[SingleImport]:
        return self._import_d.get(name, None)

    def items(self) -> Generator[Tuple[str, SingleImport], Any, Any]:
        for k, v in self._import_d.items():
            yield (k, v)

    @classmethod
    def init(cls) -> Optional['ImportConfig']:
        xdg_root = os.getenv(
            'XDG_CONFIG_HOME',
            '{}/.config'.format(
                os.environ['HOME']
            )
        )
        nayvy_import_config_path = '{}/nayvy/import_config.nayvy'.format(
            xdg_root,
        )
        return cls._of_config_py(nayvy_import_config_path)

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
            import_statements = ImportStatement.of_lines(block)
            if import_statements is None:
                return None
            for import_statement in import_statements:
                for import_as_part in import_statement.import_as_parts:
                    single_import = SingleImport(
                        import_as_part.name,
                        import_statement.get_single_statement(
                            import_as_part,
                        ),
                        block_i,
                    )
                    import_d[single_import.name] = single_import
        return ImportConfig(import_d)
