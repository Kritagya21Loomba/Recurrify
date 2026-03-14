import pytest
from recurrify.parser.parser import parse, ParseError
from recurrify.models.ast_nodes import BinOp, FuncCall, Num, Recurrence, Var


@pytest.mark.parametrize(
    "input_str",
    [
        "T(n) = 2T(n/2) + n",
        "T(n) = T(n-1) + n^2",
        "T(n) = 2T(n-1) + 3T(n-2)",
        "T(n) = 3T(n/2) + n^2 log(n)",
        "T(n) = 4T(n/2) + n^2",
        "T(n) = T(n/2) + 1",
        "T(n) = T(n-1) + T(n-2)",
        "T(n) = T(n-1) + 1",
    ],
)
def test_parser_accepts(input_str):
    result = parse(input_str)
    assert isinstance(result, Recurrence)
    assert result.func_name == "T"
    assert result.var_name == "n"


def test_divide_and_conquer_structure():
    result = parse("T(n) = 2T(n/2) + n")
    assert result.func_name == "T"
    assert result.var_name == "n"
    assert isinstance(result.rhs, BinOp)
    assert result.rhs.op == "+"


def test_invalid_input():
    with pytest.raises(ParseError):
        parse("= 2T(n/2) + n")
