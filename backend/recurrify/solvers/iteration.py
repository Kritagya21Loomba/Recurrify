from __future__ import annotations

from sympy import (
    Integer,
    S,
    Symbol,
    latex,
    simplify,
    summation,
    Function,
)

from recurrify.models.ast_nodes import RecurrenceInfo
from recurrify.solvers.base import BaseSolver, SolutionResult, Step


class IterationSolver(BaseSolver):
    """Solves recurrences by repeated substitution (telescoping/expansion)."""

    def can_solve(self, info: RecurrenceInfo) -> bool:
        # Can attempt iteration on both divide-and-conquer and linear recurrences
        return (
            (info.num_subproblems is not None and info.division_factor is not None)
            or bool(info.coefficients)
        )

    def solve(self, info: RecurrenceInfo) -> SolutionResult:
        if not self.can_solve(info):
            return SolutionResult(
                method="Iteration",
                steps=[],
                closed_form="",
                applicable=False,
                inapplicable_reason="Cannot apply iteration to this recurrence.",
            )

        if info.num_subproblems is not None and info.division_factor is not None:
            return self._solve_divide_and_conquer(info)
        else:
            return self._solve_linear(info)

    def _solve_divide_and_conquer(self, info: RecurrenceInfo) -> SolutionResult:
        """Iterate T(n) = aT(n/b) + f(n) by repeated substitution."""
        n = Symbol("n", positive=True)
        k = Symbol("k", nonnegative=True, integer=True)
        a = info.num_subproblems
        b = info.division_factor
        f = info.driving_function
        if f is None:
            f = S.Zero

        steps: list[Step] = []

        # Show 3 expansions
        steps.append(
            Step(
                explanation="Start with the original recurrence",
                latex=f"T(n) = {a} \\cdot T\\!\\left(\\frac{{n}}{{{b}}}\\right) + {latex(f)}",
            )
        )

        # Expansion 1: substitute T(n/b)
        f_1 = f.subs(n, n / Integer(b))
        expanded_1 = Integer(a) ** 2 * Function("T")(n / Integer(b) ** 2)
        cost_1 = Integer(a) * f_1 + f
        steps.append(
            Step(
                explanation=f"Substitute T(n/{b}) = {a} T(n/{b**2}) + f(n/{b})",
                latex=(
                    f"T(n) = {a}\\left[{a} \\cdot T\\!\\left(\\frac{{n}}{{{b**2}}}\\right) + "
                    f"{latex(f_1)}\\right] + {latex(f)}"
                    f" = {a**2} \\cdot T\\!\\left(\\frac{{n}}{{{b**2}}}\\right) + {latex(simplify(cost_1))}"
                ),
            )
        )

        # Expansion 2: substitute again
        f_2 = f.subs(n, n / Integer(b) ** 2)
        cost_2 = Integer(a) ** 2 * f_2 + Integer(a) * f_1 + f
        steps.append(
            Step(
                explanation=f"Substitute again: T(n/{b**2}) = {a} T(n/{b**3}) + f(n/{b**2})",
                latex=(
                    f"T(n) = {a**3} \\cdot T\\!\\left(\\frac{{n}}{{{b**3}}}\\right) + "
                    f"{latex(simplify(cost_2))}"
                ),
            )
        )

        # General pattern after k steps
        general_sum = sum(
            Integer(a) ** i * f.subs(n, n / Integer(b) ** i) for i in range(1)
        )
        # Symbolic pattern
        steps.append(
            Step(
                explanation="Identify the pattern after k substitutions",
                latex=(
                    f"T(n) = {a}^k \\cdot T\\!\\left(\\frac{{n}}{{{b}^k}}\\right) + "
                    f"\\sum_{{i=0}}^{{k-1}} {a}^i \\cdot f\\!\\left(\\frac{{n}}{{{b}^i}}\\right)"
                ),
            )
        )

        # Base case: k = log_b(n) => n/b^k = 1
        from sympy import log as symlog

        base_val = info.base_cases.get(1, 1)
        steps.append(
            Step(
                explanation=f"Set k = log_{b}(n) so that n/{b}^k = 1",
                latex=(
                    f"\\text{{At }} k = \\log_{{{b}}} n: \\quad "
                    f"T(n) = {a}^{{\\log_{{{b}}} n}} \\cdot T(1) + "
                    f"\\sum_{{i=0}}^{{\\log_{{{b}}} n - 1}} {a}^i \\cdot f\\!\\left(\\frac{{n}}{{{b}^i}}\\right)"
                ),
            )
        )

        # Evaluate the sum using the same logic as recursion tree
        crit = symlog(Integer(a), Integer(b))
        crit_simplified = simplify(crit)
        n_crit = n**crit_simplified

        # Determine closed form from the series
        ratio = simplify(Integer(a) * f.subs(n, n / Integer(b)) / f) if f != S.Zero else S.Zero

        if f == S.Zero:
            closed = n_crit * base_val
            closed_form_latex = f"T(n) = \\Theta\\left({latex(n_crit)}\\right)"
        elif ratio == 1:
            closed = f * symlog(n, 2)
            closed_form_latex = f"T(n) = \\Theta\\left({latex(f)} \\cdot \\log n\\right)"
        elif ratio.is_number and ratio < 1:
            closed = f
            closed_form_latex = f"T(n) = \\Theta\\left({latex(f)}\\right)"
        else:
            closed = n_crit
            closed_form_latex = f"T(n) = \\Theta\\left({latex(n_crit)}\\right)"

        steps.append(
            Step(
                explanation="Evaluate the sum to obtain the closed form",
                latex=closed_form_latex,
            )
        )

        return SolutionResult(
            method="Iteration",
            steps=steps,
            closed_form=closed_form_latex,
            closed_form_sympy=closed,
        )

    def _solve_linear(self, info: RecurrenceInfo) -> SolutionResult:
        """Iterate T(n) = c*T(n-1) + g(n) by telescoping."""
        n = Symbol("n", positive=True, integer=True)
        k = Symbol("k", positive=True, integer=True)

        steps: list[Step] = []

        coeffs = info.coefficients
        g = info.nonhomogeneous_part

        # Simple case: single T(n-1) coefficient
        if len(coeffs) == 1 and coeffs[0][0] == 1:
            c = coeffs[0][1]

            if c == 1 and g is not None:
                # T(n) = T(n-1) + g(n) => telescoping
                return self._solve_telescoping(info, g, n, steps)
            elif c != 1:
                return self._solve_linear_first_order(info, c, g, n, steps)

        # Multi-term: can't easily iterate, mark as less applicable
        return SolutionResult(
            method="Iteration",
            steps=[
                Step(
                    explanation="This recurrence has multiple recursive terms",
                    latex="\\text{Iteration is complex for multi-term linear recurrences. "
                    "The characteristic equation method is preferred.}",
                )
            ],
            closed_form="",
            applicable=False,
            inapplicable_reason="Multi-term linear recurrence; use characteristic equation instead.",
        )

    def _solve_telescoping(self, info, g, n, steps) -> SolutionResult:
        """T(n) = T(n-1) + g(n) by telescoping."""
        from sympy import Sum, latex, simplify, factorial, Rational

        steps.append(
            Step(
                explanation="This is a telescoping recurrence",
                latex=f"T(n) = T(n-1) + {latex(g)}",
            )
        )

        # Expand a few steps
        steps.append(
            Step(
                explanation="Telescope by repeated substitution",
                latex=(
                    f"T(n) = T(n-1) + {latex(g)}\n"
                    f"     = T(n-2) + {latex(g.subs(n, n - 1))} + {latex(g)}\n"
                    f"     = T(n-3) + {latex(g.subs(n, n - 2))} + {latex(g.subs(n, n - 1))} + {latex(g)}"
                ),
            )
        )

        # General pattern
        k = Symbol("k", positive=True, integer=True)
        base_val = info.base_cases.get(1, info.base_cases.get(0, 1))
        base_n = min(info.base_cases.keys()) if info.base_cases else 1

        steps.append(
            Step(
                explanation="Write the general telescoped form",
                latex=(
                    f"T(n) = T({base_n}) + \\sum_{{k={base_n + 1}}}^{{n}} {latex(g.subs(n, k))}"
                ),
            )
        )

        # Evaluate the sum
        the_sum = Sum(g.subs(n, k), (k, base_n + 1, n))
        try:
            evaluated = simplify(the_sum.doit())
        except Exception:
            evaluated = the_sum

        steps.append(
            Step(
                explanation="Evaluate the summation",
                latex=f"\\sum_{{k={base_n + 1}}}^{{n}} {latex(g.subs(n, k))} = {latex(evaluated)}",
            )
        )

        # Extract asymptotic behavior
        from sympy import Pow, log, O, LM, degree

        closed = evaluated
        # Get leading term for the Theta notation
        try:
            from sympy import leading_term
        except ImportError:
            pass

        closed_form_latex = f"T(n) = \\Theta\\left({latex(simplify(evaluated))}\\right)"

        steps.append(
            Step(
                explanation="State the final result",
                latex=closed_form_latex,
            )
        )

        return SolutionResult(
            method="Iteration",
            steps=steps,
            closed_form=closed_form_latex,
            closed_form_sympy=closed,
        )

    def _solve_linear_first_order(self, info, c, g, n, steps) -> SolutionResult:
        """T(n) = c*T(n-1) + g(n) with c != 1."""
        from sympy import latex, simplify, Sum, Pow

        c_sym = Integer(int(c)) if c == int(c) else Rational(c).limit_denominator(1000)
        k = Symbol("k", positive=True, integer=True)

        steps.append(
            Step(
                explanation="Identify the first-order linear recurrence",
                latex=f"T(n) = {latex(c_sym)} \\cdot T(n-1) + {latex(g) if g else '0'}",
            )
        )

        # General solution: T(n) = c^n * T(0) + sum_{k=1}^{n} c^{n-k} * g(k)
        base_val = info.base_cases.get(0, info.base_cases.get(1, 1))

        steps.append(
            Step(
                explanation="Expand by repeated substitution",
                latex=(
                    f"T(n) = {latex(c_sym)}^n \\cdot T(0) + "
                    f"\\sum_{{k=1}}^{{n}} {latex(c_sym)}^{{n-k}} \\cdot {latex(g.subs(n, k)) if g else '0'}"
                ),
            )
        )

        # The dominant term is c^n (exponential growth)
        closed = c_sym**n
        closed_form_latex = f"T(n) = \\Theta\\left({latex(c_sym)}^n\\right)"

        steps.append(
            Step(
                explanation="The exponential term dominates",
                latex=closed_form_latex,
            )
        )

        return SolutionResult(
            method="Iteration",
            steps=steps,
            closed_form=closed_form_latex,
            closed_form_sympy=closed,
        )
