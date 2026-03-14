from recurrify.parser.tokenizer import TokenType, tokenize


def test_basic_tokenize():
    tokens = tokenize("T(n) = 2T(n/2) + n")
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    # T ( n ) = 2 * T ( n / 2 ) + n
    assert TokenType.IDENT in types
    assert TokenType.NUMBER in types
    assert TokenType.STAR in types  # implicit multiplication between 2 and T


def test_implicit_multiplication():
    tokens = tokenize("2T(n/2)")
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    # 2 * T( n / 2 ) — implicit * between number and function call
    assert types == [
        TokenType.NUMBER,
        TokenType.STAR,  # implicit multiplication
        TokenType.IDENT,  # T
        TokenType.LPAREN,  # (  — NOT preceded by * since T( is a function call
        TokenType.IDENT,  # n
        TokenType.SLASH,  # /
        TokenType.NUMBER,  # 2
        TokenType.RPAREN,  # )
    ]


def test_power_and_log():
    tokens = tokenize("n^2 log n")
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    # n ^ 2 * log * n
    assert TokenType.CARET in types
    assert TokenType.STAR in types


def test_negative_numbers():
    tokens = tokenize("T(n) = -3T(n-1)")
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert TokenType.MINUS in types
