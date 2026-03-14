from __future__ import annotations

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
    numeric_checks: list[dict] = field(default_factory=list)


@dataclass
class SolutionResult:
    method: str
    steps: list[Step]
    closed_form: str  # LaTeX
    closed_form_sympy: str  # SymPy repr for verification
    verification: VerificationResult | None = None
    applicable: bool = True
    inapplicable_reason: str | None = None
