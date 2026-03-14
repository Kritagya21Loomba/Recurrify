from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class BinOp:
    op: str  # '+', '-', '*', '/', '^'
    left: ASTNode
    right: ASTNode


@dataclass(frozen=True)
class UnaryOp:
    op: str  # '-'
    operand: ASTNode


@dataclass(frozen=True)
class FuncCall:
    name: str
    args: tuple[ASTNode, ...]


ASTNode = Union[Num, Var, BinOp, UnaryOp, FuncCall]


@dataclass(frozen=True)
class Recurrence:
    func_name: str  # 'T'
    var_name: str  # 'n'
    rhs: ASTNode
    base_cases: dict[int, float] | None = None


@dataclass
class RecurrenceInfo:
    func_name: str
    var: str

    # Divide-and-conquer: T(n) = a*T(n/b) + f(n)
    num_subproblems: int | None = None
    division_factor: float | None = None
    driving_function: object | None = None  # SymPy Expr

    # Linear: T(n) = c1*T(n-1) + c2*T(n-2) + ... + g(n)
    # List of (offset, coefficient): [(1, c1), (2, c2)] for c1*T(n-1) + c2*T(n-2)
    coefficients: list[tuple[int, float]] = field(default_factory=list)
    nonhomogeneous_part: object | None = None  # SymPy Expr

    # Full RHS as SymPy expression
    sympy_rhs: object | None = None

    base_cases: dict[int, float] = field(default_factory=dict)
