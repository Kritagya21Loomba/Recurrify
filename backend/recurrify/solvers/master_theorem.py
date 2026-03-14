from __future__ import annotations

from sympy import (
    Integer,
    Rational,
    S,
    Symbol,
    latex,
    limit,
    log,
    oo,
    simplify,
)

from recurrify.models.ast_nodes import RecurrenceInfo
from recurrify.solvers.base import BaseSolver, SolutionResult, Step, to_sympy_number


class MasterTheoremSolver(BaseSolver):
    """Solves divide-and-conquer recurrences T(n) = aT(n/b) + f(n) using the Master Theorem."""

    def can_solve(self, info: RecurrenceInfo) -> bool:
        return (
            info.num_subproblems is not None
            and info.division_factor is not None
            and info.division_factor > 1
            and info.num_subproblems >= 1
        )

    def solve(self, info: RecurrenceInfo) -> SolutionResult:
        if not self.can_solve(info):
            return SolutionResult(
                method="Master Theorem",
                steps=[],
                closed_form="",
                applicable=False,
                inapplicable_reason="Not a divide-and-conquer recurrence of the form T(n) = aT(n/b) + f(n).",
            )

        n = Symbol("n", positive=True)
        a = info.num_subproblems
        b = info.division_factor
        f = info.driving_function
        if f is None:
            f = S.Zero

        steps: list[Step] = []

        # Step 1: Identify parameters
        steps.append(
            Step(
                explanation="Identify the recurrence parameters",
                latex=f"a = {a}, \\quad b = {b}, \\quad f(n) = {latex(f)}",
            )
        )

        # Step 2: Compute critical exponent
        crit = log(Integer(a), to_sympy_number(b)) if b != 1 else S.Zero
        crit_simplified = simplify(crit)
        steps.append(
            Step(
                explanation="Compute the critical exponent",
                latex=f"\\log_b a = \\log_{{{b}}} {a} = {latex(crit_simplified)}",
            )
        )

        # Step 3: Compare f(n) with n^{log_b a}
        n_crit = n ** crit_simplified

        case, k = self._determine_case(f, n, crit_simplified)

        if case == 1:
            steps.append(
                Step(
                    explanation=(
                        f"Compare f(n) = {latex(f)} with n^{{\\log_b a}} = {latex(n_crit)}"
                    ),
                    latex=(
                        f"f(n) = {latex(f)} = O\\left({latex(n_crit / n**Rational(1, 2))}\\right)"
                        f" \\Rightarrow f(n) \\text{{ grows polynomially slower than }} {latex(n_crit)}"
                    ),
                )
            )
            steps.append(
                Step(
                    explanation="Apply Master Theorem Case 1",
                    latex=(
                        f"\\text{{Case 1: }} f(n) = O(n^{{\\log_b a - \\varepsilon}}) "
                        f"\\text{{ for some }} \\varepsilon > 0"
                    ),
                )
            )
            closed = n_crit
            closed_form_latex = f"T(n) = \\Theta\\left({latex(closed)}\\right)"

        elif case == 2:
            log_factor = log(n, 2) ** (k + 1) if k >= 0 else log(n, 2)
            if k == 0:
                steps.append(
                    Step(
                        explanation=(
                            f"Compare f(n) = {latex(f)} with n^{{\\log_b a}} = {latex(n_crit)}"
                        ),
                        latex=(
                            f"f(n) = {latex(f)} = \\Theta\\left({latex(n_crit)}\\right)"
                        ),
                    )
                )
                steps.append(
                    Step(
                        explanation="Apply Master Theorem Case 2",
                        latex=(
                            f"\\text{{Case 2: }} f(n) = \\Theta(n^{{\\log_b a}}) "
                            f"\\Rightarrow T(n) = \\Theta\\left({latex(n_crit)} \\log n\\right)"
                        ),
                    )
                )
                closed = n_crit * log(n, 2)
                closed_form_latex = f"T(n) = \\Theta\\left({latex(n_crit)} \\log n\\right)"
            else:
                steps.append(
                    Step(
                        explanation=(
                            f"Compare f(n) = {latex(f)} with n^{{\\log_b a}} = {latex(n_crit)}"
                        ),
                        latex=(
                            f"f(n) = {latex(f)} = "
                            f"\\Theta\\left({latex(n_crit)} \\log^{{{k}}} n\\right)"
                        ),
                    )
                )
                steps.append(
                    Step(
                        explanation="Apply Master Theorem Case 2 (extended)",
                        latex=(
                            f"\\text{{Case 2: }} f(n) = \\Theta(n^{{\\log_b a}} \\log^{{{k}}} n) "
                            f"\\Rightarrow T(n) = \\Theta\\left({latex(n_crit)} \\log^{{{k + 1}}} n\\right)"
                        ),
                    )
                )
                closed = n_crit * log(n, 2) ** (k + 1)
                closed_form_latex = (
                    f"T(n) = \\Theta\\left({latex(n_crit)} \\log^{{{k + 1}}} n\\right)"
                )

        elif case == 3:
            steps.append(
                Step(
                    explanation=(
                        f"Compare f(n) = {latex(f)} with n^{{\\log_b a}} = {latex(n_crit)}"
                    ),
                    latex=(
                        f"f(n) = {latex(f)} = \\Omega\\left({latex(n_crit * n**Rational(1, 2))}\\right)"
                        f" \\Rightarrow f(n) \\text{{ grows polynomially faster than }} {latex(n_crit)}"
                    ),
                )
            )
            steps.append(
                Step(
                    explanation="Check regularity condition and apply Master Theorem Case 3",
                    latex=(
                        f"\\text{{Case 3: }} f(n) = \\Omega(n^{{\\log_b a + \\varepsilon}}) "
                        f"\\text{{ and regularity holds}} "
                        f"\\Rightarrow T(n) = \\Theta\\left({latex(f)}\\right)"
                    ),
                )
            )
            closed = f
            closed_form_latex = f"T(n) = \\Theta\\left({latex(f)}\\right)"
        else:
            steps.append(
                Step(
                    explanation="Could not determine which Master Theorem case applies",
                    latex="\\text{The Master Theorem may not apply directly to this recurrence.}",
                )
            )
            return SolutionResult(
                method="Master Theorem",
                steps=steps,
                closed_form="",
                applicable=False,
                inapplicable_reason="Could not determine Master Theorem case.",
            )

        # Step 4: Final result
        steps.append(
            Step(
                explanation="State the final result",
                latex=closed_form_latex,
            )
        )

        return SolutionResult(
            method="Master Theorem",
            steps=steps,
            closed_form=closed_form_latex,
            closed_form_sympy=closed,
        )

    def _determine_case(self, f, n, crit_exp) -> tuple[int, int]:
        """Determine which Master Theorem case applies.

        Returns (case_number, k) where k is the log exponent for Case 2.
        case_number: 1, 2, 3, or 0 if indeterminate.
        """
        if f == S.Zero:
            return (1, 0) if crit_exp != 0 else (2, 0)

        n_crit = n**crit_exp

        # Compare by taking limit of f(n) / n^crit_exp as n -> infinity
        try:
            ratio = simplify(f / n_crit)
            lim = limit(ratio, n, oo)
        except Exception:
            return (0, 0)

        if lim == 0:
            # f grows slower => Case 1
            return (1, 0)

        if lim == oo or lim == S.NegativeInfinity:
            # f grows faster => Case 3
            return (3, 0)

        if lim.is_number and lim.is_finite and lim != 0:
            # f ~ Theta(n^crit_exp) => Case 2 with k=0
            return (2, 0)

        # Check for log factors: f(n) / n^crit_exp ~ log^k(n)
        for k in range(1, 5):
            try:
                ratio_with_log = simplify(f / (n_crit * log(n) ** k))
                lim_k = limit(ratio_with_log, n, oo)
                if lim_k.is_number and lim_k.is_finite and lim_k != 0:
                    return (2, k)
            except Exception:
                continue

        # If limit was infinite, likely Case 3
        return (0, 0)
