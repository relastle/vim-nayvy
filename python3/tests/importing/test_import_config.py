
import unittest
from os.path import dirname
from pathlib import Path

from pydra.importing.import_config import ImportConfig


class TestImportConfig(unittest.TestCase):

    def test__of_config_py(self) -> None:
        pydra_config_path = (
            Path(dirname(__file__)) /
            'resources' /
            'import_config.pydra'
        )

        assert pydra_config_path.exists()
        import_config = ImportConfig._of_config_py(str(pydra_config_path))
        assert import_config is not None
        return
