
import unittest
from os.path import dirname
from pathlib import Path

from nayvy.importing.import_config import ImportConfig


class TestImportConfig(unittest.TestCase):

    def test__of_config_py(self) -> None:
        nayvy_config_path = (
            Path(dirname(__file__)) /
            'resources' /
            'import_config.nayvy'
        )

        assert nayvy_config_path.exists()
        import_config = ImportConfig._of_config_py(str(nayvy_config_path))
        assert import_config is not None
        return
