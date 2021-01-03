

from nayvy.function.func import (
    get_current_func,
    is_func_decl_start_line,
    parse_function_line,
)


def test_parse_function_line() -> None:
    func = parse_function_line('def hoge(a: int, b: str) -> None:')
    assert func
    len(func.args) == 2
    len(func.return_type) == 'None'

    func = parse_function_line(
        '        async def _hoge(a: Sequence[int], b: Dict[str, Any]) -> List[str]:',
    )
    assert func
    func.indent == 8
    len(func.args) == 2
    len(func.return_type) == 'List[str]'


def test_is_func_decl_start_line() -> None:
    assert is_func_decl_start_line('async def hoge(')
    assert is_func_decl_start_line('def hoge(')
    assert not is_func_decl_start_line('def aaa hoge(')


def test_get_current_func() -> None:
    # simple case
    target = [
        'def hogehoge(a: str, b: int) -> None:',
        '    pass',
    ]
    res = get_current_func(target, 1)
    assert res

    assert res.name == 'hogehoge'
    assert res.args[0].name == 'a'
    assert res.args[0].t == 'str'

    assert res.args[1].name == 'b'
    assert res.args[1].t == 'int'

    assert res.return_type == 'None'
    assert res.indent == 0

    # complicated case

    target = [
        'def test_function(a: str, b: int) -> None:',
        '',
        '    def inner_function(c: List[int], d: Dict[str, int]) -> List[Dict[str, Any]]:',  # noqa
        '',
    ]

    res = get_current_func(target, 3)
    assert res

    assert res.name == 'inner_function'
    assert res.args[0].name == 'c'
    assert res.args[0].t == 'List[int]'

    assert res.args[1].name == 'd'
    assert res.args[1].t == 'Dict[str, int]'

    assert res.return_type == 'List[Dict[str, Any]]'
    assert res.indent == 4
