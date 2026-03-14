from __future__ import annotations

from recurrify.models.ast_nodes import (
    ASTNode,
    BinOp,
    FuncCall,
    Num,
    Recurrence,
    UnaryOp,
    Var,
)
from recurrify.parser.tokenizer import Token, TokenType


class ParseError(Exception):
    def __init__(self, message: str, pos: int | None = None):
        self.pos = pos
        super().__init__(message)


class Parser:
    """Recursive descent parser for recurrence relations.

    Grammar:
        recurrence ::= funcall '=' expr
        expr       ::= term (('+' | '-') term)*
        term       ::= power ('*' power)*
        power      ::= unary ('^' unary)*
        unary      ::= '-' unary | atom
        atom       ::= NUMBER | IDENT | funcall | '(' expr ')'
        funcall    ::= IDENT '(' arglist ')'
        arglist    ::= expr (',' expr)*
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Recurrence:
        lhs = self._parse_funcall_or_ident()
        if not isinstance(lhs, FuncCall) or len(lhs.args) != 1:
            raise ParseError("Expected T(n) on left-hand side", self._peek().pos)
        var_node = lhs.args[0]
        if not isinstance(var_node, Var):
            raise ParseError("Expected variable in T(n)", self._peek().pos)

        self._expect(TokenType.EQUALS)
        rhs = self._parse_expr()

        if self._peek().type != TokenType.EOF:
            raise ParseError(
                f"Unexpected token after expression: {self._peek().value!r}",
                self._peek().pos,
            )

        return Recurrence(
            func_name=lhs.name,
            var_name=var_node.name,
            rhs=rhs,
        )

    def _parse_expr(self) -> ASTNode:
        left = self._parse_term()
        while self._peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self._advance().value
            right = self._parse_term()
            left = BinOp(op, left, right)
        return left

    def _parse_term(self) -> ASTNode:
        left = self._parse_power()
        while self._peek().type in (TokenType.STAR, TokenType.SLASH):
            op = self._advance().value
            right = self._parse_power()
            left = BinOp(op, left, right)
        return left

    def _parse_power(self) -> ASTNode:
        base = self._parse_unary()
        if self._peek().type == TokenType.CARET:
            self._advance()
            exp = self._parse_unary()
            base = BinOp("^", base, exp)
        return base

    def _parse_unary(self) -> ASTNode:
        if self._peek().type == TokenType.MINUS:
            self._advance()
            operand = self._parse_unary()
            return UnaryOp("-", operand)
        return self._parse_atom()

    def _parse_atom(self) -> ASTNode:
        tok = self._peek()

        if tok.type == TokenType.NUMBER:
            self._advance()
            return Num(float(tok.value))

        if tok.type == TokenType.IDENT:
            return self._parse_funcall_or_ident()

        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expr()
            self._expect(TokenType.RPAREN)
            return expr

        raise ParseError(f"Unexpected token: {tok.value!r}", tok.pos)

    def _parse_funcall_or_ident(self) -> ASTNode:
        tok = self._advance()
        if tok.type != TokenType.IDENT:
            raise ParseError(f"Expected identifier, got {tok.value!r}", tok.pos)

        # Check if followed by '(' — it's a function call
        if self._peek().type == TokenType.LPAREN:
            self._advance()  # consume '('
            args: list[ASTNode] = []
            if self._peek().type != TokenType.RPAREN:
                args.append(self._parse_expr())
                while self._peek().type == TokenType.COMMA:
                    self._advance()
                    args.append(self._parse_expr())
            self._expect(TokenType.RPAREN)
            return FuncCall(tok.value, tuple(args))

        return Var(tok.value)

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, token_type: TokenType) -> Token:
        tok = self._advance()
        if tok.type != token_type:
            raise ParseError(
                f"Expected {token_type.name}, got {tok.type.name} ({tok.value!r})",
                tok.pos,
            )
        return tok


def parse(text: str) -> Recurrence:
    from recurrify.parser.tokenizer import tokenize

    tokens = tokenize(text)
    return Parser(tokens).parse()
