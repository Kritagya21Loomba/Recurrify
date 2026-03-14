from __future__ import annotations

from sympy import (
    Integer,
    Rational,
    S,
    Symbol,
    latex,
    log,
    simplify,
    summation,
)

from recurrify.models.ast_nodes import RecurrenceInfo
from recurrify.solvers.base import BaseSolver, SolutionResult, Step, TableData


class RecursionTreeSolver(BaseSolver):
    """Solves divide-and-conquer recurrences by building a recursion tree."""

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
                method="Recursion Tree",
                steps=[],
                closed_form="",
                applicable=False,
                inapplicable_reason="Not a divide-and-conquer recurrence.",
            )

        n = Symbol("n", positive=True)
        a = info.num_subproblems
        b = info.division_factor
        f = info.driving_function
        if f is None:
            f = S.Zero

        steps: list[Step] = []
        i = Symbol("i", nonnegative=True, integer=True)

        # Step 1: Describe tree structure
        steps.append(
            Step(
                explanation="Describe the recursion tree structure",
                latex=(
                    f"\\text{{Each node has }} {a} \\text{{ children. }}"
                    f"\\text{{At level }} i\\text{{, there are }} {a}^i \\text{{ nodes, }}"
                    f"\\text{{each solving a subproblem of size }} n/{b}^i."
                ),
            )
        )

        # Step 2: Cost per level
        # At level i: a^i nodes, each contributes f(n/b^i)
        # Level cost: a^i * f(n/b^i)
        f_at_level = f.subs(n, n / Integer(b) ** i)
        level_cost = Integer(a) ** i * f_at_level
        level_cost_simplified = simplify(level_cost)

        steps.append(
            Step(
                explanation="Compute the cost at level i",
                latex=(
                    f"\\text{{Cost at level }} i = {a}^i \\cdot f\\!\\left(\\frac{{n}}{{{b}^i}}\\right)"
                    f" = {latex(level_cost_simplified)}"
                ),
            )
        )

        # Step 3: Show table for first few levels
        table_rows = []
        for level in range(4):
            nodes = a**level
            size = f"n/{b**level}" if level > 0 else "n"
            cost_per_node = latex(f.subs(n, n / Integer(b) ** level))
            total_cost = latex(simplify(Integer(a) ** level * f.subs(n, n / Integer(b) ** level)))
            table_rows.append([str(level), str(nodes), size, cost_per_node, total_cost])

        steps.append(
            Step(
                explanation="Build the level-cost table",
                latex="",
                table=TableData(
                    headers=["Level", "Nodes", "Problem Size", "Cost/Node", "Level Cost"],
                    rows=table_rows,
                ),
            )
        )

        # Step 4: Number of levels
        num_levels_latex = f"\\log_{{{b}}} n"
        steps.append(
            Step(
                explanation="Determine the number of levels",
                latex=(
                    f"\\text{{The tree has }} {num_levels_latex} + 1 \\text{{ levels "
                    f"(from level 0 to level }} {num_levels_latex}\\text{{).}}"
                ),
            )
        )

        # Step 5: Sum costs
        # Total = sum_{i=0}^{log_b(n)} a^i * f(n/b^i)
        # Try to evaluate the sum symbolically
        steps.append(
            Step(
                explanation="Sum costs across all levels",
                latex=(
                    f"T(n) = \\sum_{{i=0}}^{{\\log_{{{b}}} n}} {latex(level_cost_simplified)}"
                ),
            )
        )

        # Step 6: Identify the series type and compute closed form
        # Compute the ratio of successive level costs
        ratio = simplify(Integer(a) * f.subs(n, n / Integer(b)) / f) if f != S.Zero else S.Zero
        ratio_simplified = simplify(ratio)

        closed_form, closed_form_latex = self._sum_series(
            a, b, f, n, ratio_simplified, steps
        )

        steps.append(
            Step(
                explanation="State the final result",
                latex=closed_form_latex,
            )
        )

        return SolutionResult(
            method="Recursion Tree",
            steps=steps,
            closed_form=closed_form_latex,
            closed_form_sympy=closed_form,
        )

    def _sum_series(self, a, b, f, n, ratio, steps) -> tuple:
        """Compute the total cost by summing the geometric-like series."""
        from sympy import log as symlog

        crit = symlog(Integer(a), Integer(b))
        crit_simplified = simplify(crit)
        n_crit = n**crit_simplified

        ratio_val = simplify(ratio)

        if ratio_val == 1:
            # Each level costs the same => total = f(n) * (log_b(n) + 1) = Theta(f(n) * log n)
            steps.append(
                Step(
                    explanation="The cost at each level is the same (balanced tree)",
                    latex=(
                        f"\\text{{Ratio of successive levels}} = {latex(ratio_val)} "
                        f"\\Rightarrow \\text{{each level contributes }} \\Theta({latex(f)})"
                    ),
                )
            )
            closed = f * symlog(n, 2)
            closed_form_latex = f"T(n) = \\Theta\\left({latex(f)} \\cdot \\log n\\right)"
        elif ratio_val.is_number and ratio_val < 1:
            # Geometrically decreasing => dominated by root cost (level 0)
            steps.append(
                Step(
                    explanation="Costs decrease geometrically (root-dominated)",
                    latex=(
                        f"\\text{{Ratio}} = {latex(ratio_val)} < 1 "
                        f"\\Rightarrow \\text{{total is dominated by the root level cost}}"
                    ),
                )
            )
            closed = f
            closed_form_latex = f"T(n) = \\Theta\\left({latex(f)}\\right)"
        else:
            # Geometrically increasing => dominated by leaf cost
            # Number of leaves: a^{log_b n} = n^{log_b a}
            steps.append(
                Step(
                    explanation="Costs increase geometrically (leaf-dominated)",
                    latex=(
                        f"\\text{{Ratio}} = {latex(ratio_val)} > 1 "
                        f"\\Rightarrow \\text{{total is dominated by the leaf level}}"
                    ),
                )
            )
            steps.append(
                Step(
                    explanation="Count the leaves",
                    latex=(
                        f"\\text{{Number of leaves}} = {a}^{{\\log_{{{b}}} n}} = n^{{\\log_{{{b}}} {a}}} "
                        f"= {latex(n_crit)}"
                    ),
                )
            )
            closed = n_crit
            closed_form_latex = f"T(n) = \\Theta\\left({latex(n_crit)}\\right)"

        return closed, closed_form_latex
