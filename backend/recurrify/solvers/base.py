from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


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
