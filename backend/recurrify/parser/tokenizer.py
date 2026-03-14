from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    IDENT = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    LPAREN = auto()
    RPAREN = auto()
    EQUALS = auto()
    COMMA = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    pos: int


_KNOWN_FUNCS = {"log", "ln", "sqrt", "lg"}

_TOKEN_PATTERNS = [
    (r"\d+(?:\.\d+)?", TokenType.NUMBER),
    (r"[a-zA-Z_][a-zA-Z_0-9]*", TokenType.IDENT),
    (r"\+", TokenType.PLUS),
    (r"-", TokenType.MINUS),
    (r"\*", TokenType.STAR),
    (r"/", TokenType.SLASH),
    (r"\^", TokenType.CARET),
    (r"\(", TokenType.LPAREN),
    (r"\)", TokenType.RPAREN),
    (r"=", TokenType.EQUALS),
    (r",", TokenType.COMMA),
]

_MASTER_RE = re.compile(
    "|".join(f"({pat})" for pat, _ in _TOKEN_PATTERNS)
)


def _is_operand_end(t: TokenType) -> bool:
    return t in (TokenType.NUMBER, TokenType.IDENT, TokenType.RPAREN)


def _is_operand_start(t: TokenType) -> bool:
    return t in (TokenType.NUMBER, TokenType.IDENT, TokenType.LPAREN)


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for m in _MASTER_RE.finditer(text):
        value = m.group()
        pos = m.start()

        # Determine token type
        token_type = None
        for i, (_, tt) in enumerate(_TOKEN_PATTERNS):
            if m.group(i + 1) is not None:
                token_type = tt
                break

        if token_type is None:
            raise ValueError(f"Unexpected character at position {pos}: {value!r}")

        # Insert implicit multiplication, but NOT between IDENT and LPAREN (function call)
        if tokens and _is_operand_end(tokens[-1].type) and _is_operand_start(token_type):
            # Skip: IDENT followed by LPAREN is a function call, not multiplication
            if not (tokens[-1].type == TokenType.IDENT and token_type == TokenType.LPAREN):
                tokens.append(Token(TokenType.STAR, "*", pos))

        tokens.append(Token(token_type, value, pos))

    tokens.append(Token(TokenType.EOF, "", len(text)))
    return tokens
