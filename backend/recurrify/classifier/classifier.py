from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from recurrify.models.ast_nodes import RecurrenceInfo


class RecurrenceType(Enum):
    DIVIDE_AND_CONQUER = "divide_and_conquer"
    LINEAR_HOMOGENEOUS = "linear_homogeneous"
    LINEAR_NONHOMOGENEOUS = "linear_nonhomogeneous"
    UNKNOWN = "unknown"


class SolverMethod(Enum):
    MASTER_THEOREM = "Master Theorem"
    RECURSION_TREE = "Recursion Tree"
    ITERATION = "Iteration"
    CHARACTERISTIC_EQUATION = "Characteristic Equation"


@dataclass
class ClassificationResult:
    recurrence_type: RecurrenceType
    applicable_methods: list[SolverMethod]
    preferred_method: SolverMethod
    reasoning: str


class Classifier:
    def classify(self, info: RecurrenceInfo) -> ClassificationResult:
        if info.num_subproblems is not None and info.division_factor is not None:
            return self._classify_divide_and_conquer(info)

        if info.coefficients:
            return self._classify_linear(info)

        return ClassificationResult(
            recurrence_type=RecurrenceType.UNKNOWN,
            applicable_methods=[SolverMethod.ITERATION],
            preferred_method=SolverMethod.ITERATION,
            reasoning="Could not determine recurrence type; iteration may still work.",
        )

    def _classify_divide_and_conquer(self, info: RecurrenceInfo) -> ClassificationResult:
        a = info.num_subproblems
        b = info.division_factor
        f = info.driving_function

        methods = [
            SolverMethod.MASTER_THEOREM,
            SolverMethod.RECURSION_TREE,
            SolverMethod.ITERATION,
        ]

        return ClassificationResult(
            recurrence_type=RecurrenceType.DIVIDE_AND_CONQUER,
            applicable_methods=methods,
            preferred_method=SolverMethod.MASTER_THEOREM,
            reasoning=(
                f"Divide-and-conquer form with a={a}, b={b}, "
                f"f(n)={f}. Master Theorem, Recursion Tree, and Iteration apply."
            ),
        )

    def _classify_linear(self, info: RecurrenceInfo) -> ClassificationResult:
        has_nonhom = info.nonhomogeneous_part is not None

        if has_nonhom:
            methods = [SolverMethod.ITERATION, SolverMethod.CHARACTERISTIC_EQUATION]
            return ClassificationResult(
                recurrence_type=RecurrenceType.LINEAR_NONHOMOGENEOUS,
                applicable_methods=methods,
                preferred_method=SolverMethod.ITERATION,
                reasoning=(
                    f"Linear non-homogeneous recurrence with coefficients "
                    f"{info.coefficients} and non-homogeneous part "
                    f"{info.nonhomogeneous_part}."
                ),
            )

        methods = [SolverMethod.CHARACTERISTIC_EQUATION, SolverMethod.ITERATION]
        return ClassificationResult(
            recurrence_type=RecurrenceType.LINEAR_HOMOGENEOUS,
            applicable_methods=methods,
            preferred_method=SolverMethod.CHARACTERISTIC_EQUATION,
            reasoning=(
                f"Linear homogeneous recurrence with constant coefficients: "
                f"{info.coefficients}."
            ),
        )
