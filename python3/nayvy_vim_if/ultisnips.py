"""
Utility function for ultisnips
"""

from typing import Any, List, Iterable

from nayvy.importing.utils import (
    get_first_line_num,
    get_import_block_indices
)
from nayvy.importing.import_statement import ImportStatement


def buf2lines(buf: Iterable[str]) -> List[str]:
    """
    Hacky functions for Ultisnips lines into normal list of str.
    """
    lines = []
    try:
        for i, line in enumerate(buf):
            lines.append(line)
    except Exception:
        return lines
    return lines


def auto_import(snip: Any, statement: str, level: int) -> None:
    """ Hookable funciton for auto-importing when snippet expansion
    """
    lines = buf2lines(snip.buffer)

    # get import blocks
    begin_end_indices = get_import_block_indices(lines)

    # get import_statements for each block
    maybe_import_statements_lst = [
        ImportStatement.of_lines(lines[begin_index:end_index])
        for begin_index, end_index in begin_end_indices
    ]

    import_statements_lst = []
    for maybe in maybe_import_statements_lst:
        if maybe is not None:
            import_statements_lst.append(maybe)

    # Constructing import sentence should be added.
    import_stmt_to_add = ImportStatement.of(statement)
    if import_stmt_to_add is None:
        return None

    # constructing import import statements
    if len(import_statements_lst) <= level:
        import_statements_lst.append([import_stmt_to_add])
    else:
        import_statements_lst[level].append(import_stmt_to_add)

    # Merge the imports
    merged_import_statements = [
        ImportStatement.merge_list(import_statements)
        for import_statements in import_statements_lst
    ]

    # Make organized import blocks
    import_lines: List[str] = []
    for i, merged_import_statement in enumerate(
        merged_import_statements
    ):
        for import_statement in merged_import_statement:
            import_lines += import_statement.to_lines()
        if i < len(merged_import_statements) - 1:
            import_lines.append('')

    if not begin_end_indices:
        fitst_line_num = get_first_line_num(lines)
        snip.buffer[fitst_line_num:fitst_line_num] = import_lines
    else:
        snip.buffer[begin_end_indices[0][0]:begin_end_indices[-1][-1]] = import_lines
    return
