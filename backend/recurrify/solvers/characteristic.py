from __future__ import annotations

from sympy import (
    Eq,
    Integer,
    Matrix,
    Rational,
    S,
    Symbol,
    latex,
    linsolve,
    roots,
    simplify,
    solve,
    symbols,
)

from recurrify.models.ast_nodes import RecurrenceInfo
from recurrify.solvers.base import BaseSolver, SolutionResult, Step


class CharacteristicSolver(BaseSolver):
    """Solves linear recurrences with constant coefficients using the characteristic equation."""

    def can_solve(self, info: RecurrenceInfo) -> bool:
        return bool(info.coefficients)

    def solve(self, info: RecurrenceInfo) -> SolutionResult:
        if not self.can_solve(info):
            return SolutionResult(
                method="Characteristic Equation",
                steps=[],
                closed_form="",
                applicable=False,
                inapplicable_reason="Not a linear recurrence with constant coefficients.",
            )

        n = Symbol("n", positive=True, integer=True)
        r = Symbol("r")
        steps: list[Step] = []

        coeffs = info.coefficients  # list of (offset, coeff): e.g., [(1, 2), (2, 3)]
        has_nonhom = info.nonhomogeneous_part is not None

        # Step 1: Write the recurrence
        terms = []
        for offset, coeff in coeffs:
            c = Integer(int(coeff)) if coeff == int(coeff) else Rational(coeff).limit_denominator(1000)
            terms.append(f"{latex(c)} \\cdot T(n-{offset})")
        rhs_str = " + ".join(terms)
        if has_nonhom:
            rhs_str += f" + {latex(info.nonhomogeneous_part)}"

        steps.append(
            Step(
                explanation="Write the recurrence",
                latex=f"T(n) = {rhs_str}",
            )
        )

        # Step 2: Form the characteristic equation
        order = max(offset for offset, _ in coeffs)
        # Characteristic equation: r^order - c1*r^{order-1} - c2*r^{order-2} - ... = 0
        char_eq = r**order
        for offset, coeff in coeffs:
            c = Integer(int(coeff)) if coeff == int(coeff) else Rational(coeff).limit_denominator(1000)
            char_eq -= c * r ** (order - offset)

        steps.append(
            Step(
                explanation="Form the characteristic equation by substituting T(n) = r^n",
                latex=f"{latex(char_eq)} = 0",
            )
        )

        # Step 3: Solve for roots
        root_dict = roots(char_eq, r)
        if not root_dict:
            # Fall back to solve()
            root_list = solve(char_eq, r)
            root_dict = {root: 1 for root in root_list}

        if not root_dict:
            return SolutionResult(
                method="Characteristic Equation",
                steps=steps,
                closed_form="",
                applicable=False,
                inapplicable_reason="Could not solve the characteristic equation.",
            )

        root_strs = []
        for root_val, mult in root_dict.items():
            if mult > 1:
                root_strs.append(f"r = {latex(root_val)} \\text{{ (multiplicity {mult})}}")
            else:
                root_strs.append(f"r = {latex(root_val)}")

        steps.append(
            Step(
                explanation="Solve the characteristic equation",
                latex="\\quad".join(root_strs),
            )
        )

        # Step 4: Write the general solution
        const_symbols = []
        general_terms = []
        idx = 0
        for root_val, mult in root_dict.items():
            for m in range(mult):
                c_sym = Symbol(f"c_{{{idx + 1}}}")
                const_symbols.append(c_sym)
                if m == 0:
                    term = c_sym * root_val**n
                    general_terms.append(f"{latex(c_sym)} \\cdot {latex(root_val)}^n")
                else:
                    term = c_sym * n**m * root_val**n
                    general_terms.append(
                        f"{latex(c_sym)} \\cdot n^{{{m}}} \\cdot {latex(root_val)}^n"
                    )
                idx += 1

        general_expr_parts = []
        idx = 0
        for root_val, mult in root_dict.items():
            for m in range(mult):
                c_sym = const_symbols[idx]
                general_expr_parts.append(c_sym * n**m * root_val**n)
                idx += 1

        general_expr = sum(general_expr_parts)
        general_str = " + ".join(general_terms)

        steps.append(
            Step(
                explanation="Write the general solution",
                latex=f"T(n) = {general_str}",
            )
        )

        # Step 5: Apply base cases to find constants
        if info.base_cases and len(info.base_cases) >= len(const_symbols):
            equations = []
            sorted_bases = sorted(info.base_cases.items())

            for base_n, base_val in sorted_bases[: len(const_symbols)]:
                eq = general_expr.subs(n, base_n) - base_val
                equations.append(eq)

            solutions = solve(equations, const_symbols, dict=True)
            if solutions:
                sol = solutions[0]
                final_expr = general_expr.subs(sol)
                final_expr = simplify(final_expr)

                base_eq_strs = [
                    f"T({bn}) = {bv}: \\quad {latex(general_expr.subs(n, bn))} = {bv}"
                    for bn, bv in sorted_bases[: len(const_symbols)]
                ]
                steps.append(
                    Step(
                        explanation="Apply base cases to determine constants",
                        latex="\\\\".join(base_eq_strs),
                    )
                )

                const_strs = [f"{latex(c)} = {latex(sol[c])}" for c in const_symbols if c in sol]
                steps.append(
                    Step(
                        explanation="Solve for the constants",
                        latex=", \\quad ".join(const_strs),
                    )
                )

                steps.append(
                    Step(
                        explanation="Write the final closed-form solution",
                        latex=f"T(n) = {latex(final_expr)}",
                    )
                )

                # Determine asymptotic behavior
                dominant_root = max(root_dict.keys(), key=lambda x: abs(complex(x)))
                dominant_mult = root_dict[dominant_root] - 1

                if dominant_mult > 0:
                    closed_form_latex = f"T(n) = \\Theta\\left(n^{{{dominant_mult}}} \\cdot {latex(dominant_root)}^n\\right)"
                else:
                    closed_form_latex = f"T(n) = \\Theta\\left({latex(dominant_root)}^n\\right)"

                steps.append(
                    Step(
                        explanation="State the asymptotic complexity",
                        latex=closed_form_latex,
                    )
                )

                return SolutionResult(
                    method="Characteristic Equation",
                    steps=steps,
                    closed_form=closed_form_latex,
                    closed_form_sympy=final_expr,
                )

        # No base cases or insufficient — give general form
        dominant_root = max(root_dict.keys(), key=lambda x: abs(complex(x)))
        dominant_mult = root_dict[dominant_root] - 1

        if dominant_mult > 0:
            closed = f"T(n) = \\Theta\\left(n^{{{dominant_mult}}} \\cdot {latex(dominant_root)}^n\\right)"
        else:
            closed = f"T(n) = \\Theta\\left({latex(dominant_root)}^n\\right)"

        steps.append(
            Step(
                explanation="Determine asymptotic growth from the dominant root",
                latex=closed,
            )
        )

        return SolutionResult(
            method="Characteristic Equation",
            steps=steps,
            closed_form=closed,
            closed_form_sympy=dominant_root**n,
        )
