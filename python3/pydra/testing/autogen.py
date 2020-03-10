from typing import Optional
from os.path import abspath, relpath
from pathlib import Path

from pydra.projects import get_pyproject_root
from pydra.projects.attrs import AttrResult, ClassAttrs, TopLevelFunctionAttrs


class AutoGenerator:

    def touch_test_file(self, module_filepath: str) -> Optional[str]:
        """ touch the unittest file for module located in `module_filepath`

        Touched test file path will be retunred if succeeded.
        """
        module_abspath = abspath(module_filepath)
        pyproject_root = get_pyproject_root(module_abspath)
        if pyproject_root is None:
            return None

        rel_path = Path(relpath(module_abspath, pyproject_root))
        # Directory path where unit test script will be put.
        target_test_dir = (
            Path(pyproject_root) /
            'tests' /
            Path(*rel_path.parts[1:-1])
        )

        # Test script path
        target_test_path: Path = (
            target_test_dir /
            ('test_' + rel_path.parts[-1])
        )

        target_test_dir.mkdir(parents=True, exist_ok=True)
        (target_test_dir / '__init__.py').touch()
        target_test_path.touch()
        return str(target_test_path)

    def get_additional_attrs(
        self,
        impl_ar: AttrResult,
        test_ar: AttrResult,
    ) -> AttrResult:
        """
        Calculate additional attributes defined in
        test script compared to implementation module file.
        """
        expected_test_ar = AttrResult(
            {
                **{
                    k: v.to_test()
                    for k, v in impl_ar.class_attrs_d.items()
                },
                **{
                    'Test': ClassAttrs(
                        [],
                        [
                            f'test_{name}' for name in
                            impl_ar.top_level_function_attrs.function_names
                        ]
                    ),
                }
            },
            TopLevelFunctionAttrs.of_empty(),
        )
        return expected_test_ar - test_ar

    def generate_test_module(self, test_module_path: str) -> bool:
        pass
