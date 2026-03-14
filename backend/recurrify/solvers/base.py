from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from sympy import Integer, Rational


def to_sympy_number(val):
    """Convert a numeric value to an appropriate SymPy type.

    Integer values become Integer; non-integer values become Rational.
    This avoids Integer(1.5) silently truncating to 1.
    """
    if isinstance(val, (Integer, Rational)):
        return val
    if isinstance(val, int) or (isinstance(val, float) and val == int(val)):
        return Integer(int(val))
    return Rational(val).limit_denominator(1000)


@dataclass
class TableData:
    headers: list[str]
    rows: list[list[str]]


@dataclass
class Step:
    explanation: str
    latex: str
    substeps: list[Step] | None = None
    table: TableData | None = None


@dataclass
class VerificationResult:
    passed: bool
    symbolic_check: str
    numeric_checks: list[dict]


@dataclass
class SolutionResult:
    method: str
    steps: list[Step]
    closed_form: str
    closed_form_sympy: object | None = None
    verification: VerificationResult | None = None
    applicable: bool = True
    inapplicable_reason: str | None = None


class BaseSolver(ABC):
    @abstractmethod
    def can_solve(self, info) -> bool:
        ...

    @abstractmethod
    def solve(self, info) -> SolutionResult:
        ...
