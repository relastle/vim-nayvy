from typing import Any, List

from deoplete.base.source import Base


class Source(Base):
    def __init__(self, vim: Any):
        Base.__init__(self, vim)

        self.name = "nayvy"
        self.mark = "[ nayvy]"
        self.rank = 8
        self.is_volatile = True
        return

    def gather_candidates(self, context: Any) -> List[Any]:
        suggestions = []
        single_imports = self.vim.eval("nayvy#nayvy_list_imports()")
        for single_import in single_imports:
            suggestions.append(
                {
                    "word": single_import['name'],
                    "menu": self.mark + f'({single_import["statement"]})',
                    "info": single_import['statement'],
                    "dup": 0,
                }
            )
        return suggestions
