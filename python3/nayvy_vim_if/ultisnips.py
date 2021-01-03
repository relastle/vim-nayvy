"""
Utility function for ultisnips
"""

from typing import Any, Iterable, List
from pprint import pformat

from nayvy.function.func import get_current_func
from nayvy.importing.import_statement import ImportStatement
from nayvy.importing.utils import get_first_line_num, get_import_block_indices

from nayvy_vim_if.utils import warning


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


def generate_pydocstring(snip: Any) -> None:
    """
    generating pydocstring when the snippet eas expanded.
    """
    _ = snip.buffer[snip.line].strip()

    lines = buf2lines(snip.buffer)
    func = get_current_func(lines, snip.line)

    if not func:
        warning("Possibly the cursor is outside function.")
        return

    print(f'func: {pformat(func, indent=2)}')

    # erase current line
    snip.buffer[snip.line] = ' ' * (func.indent + 4)

    # Preparing anonymous snippet
    anon_snippet_lines = []

    # Args
    anon_snippet_lines += [
        '"""',
        '${1:description of this function}',
        '',
        'Args:',
    ]
    anon_snippet_lines += [
        f'    {arg.name} ({arg.t}): ${{{i+2}:description of {arg.name}}}'
        for i, arg in enumerate(func.args)
    ]

    # Returns
    if not (
        func.return_type == "None" or
        func.return_type == "NoReturn"
    ):
        anon_snippet_lines += [
            '',
            'Returns:',
            f'    {func.return_type}: ${{{len(func.args)+2}:description of return value}}',  # noqa
        ]

    anon_snippet_lines += [
        '"""',
        '${0}',
    ]
    # Expand anonymous snippet
    snip.expand_anon(
        '\n'.join(anon_snippet_lines),
        options='wm',
    )
    return
