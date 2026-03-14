from __future__ import annotations

from sympy import (
    Integer,
    Rational,
    S,
    Symbol,
    latex,
    simplify,
    summation,
    Function,
)

from recurrify.models.ast_nodes import RecurrenceInfo
from recurrify.solvers.base import BaseSolver, SolutionResult, Step, to_sympy_number


class IterationSolver(BaseSolver):
    """Solves recurrences by repeated substitution (telescoping/expansion)."""

    def can_solve(self, info: RecurrenceInfo) -> bool:
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
        a = info.num_subproblems
        b = info.division_factor
        f = info.driving_function
        if f is None:
            f = S.Zero

        steps: list[Step] = []

        # ---------------------------------------------------------------
        # Step 1: State the original recurrence
        # ---------------------------------------------------------------
        steps.append(
            Step(
                explanation="Start with the original recurrence",
                latex=f"T(n) = {a} \\cdot T\\!\\left(\\frac{{n}}{{{b}}}\\right) + {latex(f)}",
            )
        )

        # ---------------------------------------------------------------
        # Step 2-4: Show three concrete expansions
        # ---------------------------------------------------------------
        f_1 = simplify(f.subs(n, n / to_sympy_number(b)))
        cost_1 = simplify(Integer(a) * f_1 + f)
        steps.append(
            Step(
                explanation=f"Expand once: substitute T(n/{b})",
                latex=(
                    f"T(n) = {a}\\Bigl[{a} \\cdot T\\!\\left(\\frac{{n}}{{{b**2}}}\\right) + "
                    f"{latex(f_1)}\\Bigr] + {latex(f)}"
                    f" = {a**2} \\cdot T\\!\\left(\\frac{{n}}{{{b**2}}}\\right) + {latex(cost_1)}"
                ),
            )
        )

        f_2 = simplify(f.subs(n, n / to_sympy_number(b) ** 2))
        cost_2 = simplify(Integer(a) ** 2 * f_2 + Integer(a) * f_1 + f)
        steps.append(
            Step(
                explanation=f"Expand twice: substitute T(n/{b**2})",
                latex=(
                    f"T(n) = {a**3} \\cdot T\\!\\left(\\frac{{n}}{{{b**3}}}\\right) + {latex(cost_2)}"
                ),
            )
        )

        f_3 = simplify(f.subs(n, n / to_sympy_number(b) ** 3))
        cost_3 = simplify(Integer(a) ** 3 * f_3 + Integer(a) ** 2 * f_2 + Integer(a) * f_1 + f)
        steps.append(
            Step(
                explanation=f"Expand three times: substitute T(n/{b**3})",
                latex=(
                    f"T(n) = {a**4} \\cdot T\\!\\left(\\frac{{n}}{{{b**4}}}\\right) + {latex(cost_3)}"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 5: Lay out the costs side-by-side so the pattern is visible
        # ---------------------------------------------------------------
        costs_plain = [
            simplify(Integer(a) ** i * f.subs(n, n / to_sympy_number(b) ** i))
            for i in range(4)
        ]
        # Build a plain list like: f(n) + a·f(n/b) + a²·f(n/b²) + a³·f(n/b³)
        plain_terms = " + ".join(latex(c) for c in costs_plain)
        steps.append(
            Step(
                explanation="Write out the accumulated cost terms to see the pattern",
                latex=(
                    f"\\text{{After }}k\\text{{ expansions the non-recursive cost is:}}\\\\[6pt]"
                    f"\\underbrace{{{latex(costs_plain[0])}}}_{{{latex(Integer(a))}^0 \\cdot f(n/{latex(to_sympy_number(b))}^0)}} "
                    f"\\;+\\; \\underbrace{{{latex(costs_plain[1])}}}_{{{a}^1 \\cdot f(n/{b}^1)}} "
                    f"\\;+\\; \\underbrace{{{latex(costs_plain[2])}}}_{{{a}^2 \\cdot f(n/{b}^2)}} "
                    f"\\;+\\; \\underbrace{{{latex(costs_plain[3])}}}_{{{a}^3 \\cdot f(n/{b}^3)}} "
                    f"\\;+\\; \\cdots"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 6: State the pattern in simple words + simple notation
        # ---------------------------------------------------------------
        steps.append(
            Step(
                explanation="Identify the pattern",
                latex=(
                    f"\\text{{After }} k \\text{{ substitutions:}}\\\\[6pt]"
                    f"T(n) \\;=\\; "
                    f"{a}^k \\cdot T\\!\\left(\\frac{{n}}{{{b}^k}}\\right) "
                    f"\\;+\\; "
                    f"{latex(costs_plain[0])} + {latex(costs_plain[1])} + \\cdots + "
                    f"{a}^{{k-1}} \\cdot f\\!\\left(\\frac{{n}}{{{b}^{{k-1}}}}\\right)"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 7: NOW introduce summation notation as a compact rewrite
        # ---------------------------------------------------------------
        steps.append(
            Step(
                explanation="Express the pattern in summation notation",
                latex=(
                    f"T(n) = {a}^k \\cdot T\\!\\left(\\frac{{n}}{{{b}^k}}\\right) + "
                    f"\\sum_{{i=0}}^{{k-1}} {a}^i \\cdot f\\!\\left(\\frac{{n}}{{{b}^i}}\\right)"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 8: Plug in the stopping condition
        # ---------------------------------------------------------------
        from sympy import log as symlog

        base_val = info.base_cases.get(1, 1)
        steps.append(
            Step(
                explanation=f"The recursion bottoms out when n/{b}^k = 1, i.e. k = log_{b}(n)",
                latex=(
                    f"\\text{{Set }} k = \\log_{{{b}}} n \\quad "
                    f"\\Longrightarrow \\quad "
                    f"T(n) = {a}^{{\\log_{{{b}}} n}} \\cdot T(1) + "
                    f"\\sum_{{i=0}}^{{\\log_{{{b}}} n - 1}} {a}^i \\cdot f\\!\\left(\\frac{{n}}{{{b}^i}}\\right)"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 9: Evaluate the sum and state the closed form
        # ---------------------------------------------------------------
        crit = symlog(Integer(a), to_sympy_number(b))
        crit_simplified = simplify(crit)
        n_crit = n**crit_simplified

        ratio = simplify(Integer(a) * f.subs(n, n / to_sympy_number(b)) / f) if f != S.Zero else S.Zero

        if f == S.Zero:
            closed = n_crit * base_val
            sum_explanation = (
                f"\\text{{Since }} f(n) = 0, \\text{{ only the leaf cost remains: }} "
                f"{a}^{{\\log_{{{b}}} n}} = {latex(n_crit)}"
            )
            closed_form_latex = f"T(n) = \\Theta\\left({latex(n_crit)}\\right)"
        elif ratio == 1:
            closed = f * symlog(n, 2)
            sum_explanation = (
                f"\\text{{Each of the }} \\log_{{{b}}} n \\text{{ levels contributes the same cost }} "
                f"{latex(f)}, \\text{{ so the total is }} {latex(f)} \\cdot \\log_{{{b}}} n"
            )
            closed_form_latex = f"T(n) = \\Theta\\left({latex(f)} \\cdot \\log n\\right)"
        elif ratio.is_number and ratio < 1:
            closed = f
            sum_explanation = (
                f"\\text{{The terms shrink by a factor of }} {latex(ratio)} < 1 "
                f"\\text{{ each level, so the sum is dominated by the first (root) term }} {latex(f)}"
            )
            closed_form_latex = f"T(n) = \\Theta\\left({latex(f)}\\right)"
        else:
            closed = n_crit
            sum_explanation = (
                f"\\text{{The terms grow by a factor of }} {latex(ratio)} > 1 "
                f"\\text{{ each level, so the sum is dominated by the last (leaf) term }} {latex(n_crit)}"
            )
            closed_form_latex = f"T(n) = \\Theta\\left({latex(n_crit)}\\right)"

        steps.append(
            Step(
                explanation="Evaluate the sum",
                latex=sum_explanation,
            )
        )

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

    def _solve_linear(self, info: RecurrenceInfo) -> SolutionResult:
        """Iterate T(n) = c*T(n-1) + g(n) by telescoping."""
        n = Symbol("n", positive=True, integer=True)

        steps: list[Step] = []

        coeffs = info.coefficients
        g = info.nonhomogeneous_part

        # Simple case: single T(n-1) coefficient
        if len(coeffs) == 1 and coeffs[0][0] == 1:
            c = coeffs[0][1]

            if c == 1 and g is not None:
                return self._solve_telescoping(info, g, n, steps)
            elif c != 1:
                return self._solve_linear_first_order(info, c, g, n, steps)

        # Multi-term: can't easily iterate
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
        from sympy import Sum, latex, simplify

        base_val = info.base_cases.get(1, info.base_cases.get(0, 1))
        base_n = min(info.base_cases.keys()) if info.base_cases else 1
        k = Symbol("k", positive=True, integer=True)

        # ---------------------------------------------------------------
        # Step 1: State the recurrence
        # ---------------------------------------------------------------
        steps.append(
            Step(
                explanation="Start with the recurrence",
                latex=f"T(n) = T(n-1) + {latex(g)}",
            )
        )

        # ---------------------------------------------------------------
        # Step 2: Show concrete expansions (3 levels)
        # ---------------------------------------------------------------
        g_n = latex(g)
        g_n1 = latex(simplify(g.subs(n, n - 1)))
        g_n2 = latex(simplify(g.subs(n, n - 2)))
        g_n3 = latex(simplify(g.subs(n, n - 3)))

        steps.append(
            Step(
                explanation="Expand step by step",
                latex=(
                    f"T(n) \\;=\\; T(n-1) + {g_n}\\\\[4pt]"
                    f"\\;=\\; \\bigl[T(n-2) + {g_n1}\\bigr] + {g_n}\\\\[4pt]"
                    f"\\;=\\; \\bigl[T(n-3) + {g_n2}\\bigr] + {g_n1} + {g_n}\\\\[4pt]"
                    f"\\;=\\; \\bigl[T(n-4) + {g_n3}\\bigr] + {g_n2} + {g_n1} + {g_n}"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 3: List out the cost terms plainly
        # ---------------------------------------------------------------
        concrete_terms = [
            simplify(g.subs(n, n - i)) for i in range(4)
        ]
        steps.append(
            Step(
                explanation="List the cost added at each step",
                latex=(
                    f"\\text{{Cost terms (newest first):}}\\\\[6pt]"
                    f"{latex(concrete_terms[0])},\\quad "
                    f"{latex(concrete_terms[1])},\\quad "
                    f"{latex(concrete_terms[2])},\\quad "
                    f"{latex(concrete_terms[3])},\\quad \\ldots"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 4: State the pattern in plain notation
        # ---------------------------------------------------------------
        steps.append(
            Step(
                explanation="Identify the pattern: we are summing g(k) for k from the base case up to n",
                latex=(
                    f"T(n) = T({base_n}) + "
                    f"{latex(g.subs(n, Integer(base_n + 1)))} + "
                    f"{latex(g.subs(n, Integer(base_n + 2)))} + "
                    f"{latex(g.subs(n, Integer(base_n + 3)))} + "
                    f"\\cdots + {g_n}"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 5: NOW introduce summation notation
        # ---------------------------------------------------------------
        steps.append(
            Step(
                explanation="Write this in summation notation",
                latex=(
                    f"T(n) = T({base_n}) + \\sum_{{k={base_n + 1}}}^{{n}} {latex(g.subs(n, k))}"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 6: Evaluate the sum
        # ---------------------------------------------------------------
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

        # ---------------------------------------------------------------
        # Step 7: Final result
        # ---------------------------------------------------------------
        closed = evaluated
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
        from sympy import latex, simplify

        c_sym = Integer(int(c)) if c == int(c) else Rational(c).limit_denominator(1000)

        # ---------------------------------------------------------------
        # Step 1: State the recurrence
        # ---------------------------------------------------------------
        steps.append(
            Step(
                explanation="Start with the recurrence",
                latex=f"T(n) = {latex(c_sym)} \\cdot T(n-1) + {latex(g) if g else '0'}",
            )
        )

        # ---------------------------------------------------------------
        # Step 2-3: Show concrete expansions
        # ---------------------------------------------------------------
        g_n = latex(g) if g else "0"
        g_n1 = latex(simplify(g.subs(n, n - 1))) if g else "0"
        g_n2 = latex(simplify(g.subs(n, n - 2))) if g else "0"

        steps.append(
            Step(
                explanation="Expand step by step",
                latex=(
                    f"T(n) = {latex(c_sym)} \\cdot T(n-1) + {g_n}\\\\[4pt]"
                    f"= {latex(c_sym)}\\bigl[{latex(c_sym)} \\cdot T(n-2) + {g_n1}\\bigr] + {g_n}\\\\[4pt]"
                    f"= {latex(c_sym**2)} \\cdot T(n-2) + {latex(c_sym)} \\cdot {g_n1} + {g_n}\\\\[4pt]"
                    f"= {latex(c_sym**3)} \\cdot T(n-3) + {latex(c_sym**2)} \\cdot {g_n2} "
                    f"+ {latex(c_sym)} \\cdot {g_n1} + {g_n}"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 3: State the pattern plainly
        # ---------------------------------------------------------------
        base_val = info.base_cases.get(0, info.base_cases.get(1, 1))
        steps.append(
            Step(
                explanation="Identify the pattern: after k steps, the recursive part is c^k and we accumulate weighted costs",
                latex=(
                    f"T(n) = {latex(c_sym)}^k \\cdot T(n-k) + "
                    f"{g_n} + {latex(c_sym)} \\cdot {g_n1} + {latex(c_sym**2)} \\cdot {g_n2} + \\cdots"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 4: Now summation notation
        # ---------------------------------------------------------------
        k = Symbol("k", positive=True, integer=True)
        steps.append(
            Step(
                explanation="Express in summation notation (bottom out at T(0))",
                latex=(
                    f"T(n) = {latex(c_sym)}^n \\cdot T(0) + "
                    f"\\sum_{{k=1}}^{{n}} {latex(c_sym)}^{{n-k}} \\cdot {latex(g.subs(n, k)) if g else '0'}"
                ),
            )
        )

        # ---------------------------------------------------------------
        # Step 5: Final result
        # ---------------------------------------------------------------
        closed = c_sym**n
        closed_form_latex = f"T(n) = \\Theta\\left({latex(c_sym)}^n\\right)"

        steps.append(
            Step(
                explanation="The exponential term c^n dominates the sum",
                latex=closed_form_latex,
            )
        )

        return SolutionResult(
            method="Iteration",
            steps=steps,
            closed_form=closed_form_latex,
            closed_form_sympy=closed,
        )
