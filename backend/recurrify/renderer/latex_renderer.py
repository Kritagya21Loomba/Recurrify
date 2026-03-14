from __future__ import annotations

from sympy import latex as sympy_latex


class LaTeXRenderer:
    """Wraps SymPy's latex() with customizations for recurrence notation."""

    def render_expr(self, expr) -> str:
        return sympy_latex(expr)

    def render_recurrence(self, info) -> str:
        """Render the original recurrence in canonical form."""
        parts = []
        fname = info.func_name
        var = info.var

        if info.num_subproblems is not None and info.division_factor is not None:
            a = info.num_subproblems
            b = info.division_factor
            f = info.driving_function

            if a == 1:
                parts.append(f"{fname}\\!\\left(\\frac{{{var}}}{{{b}}}\\right)")
            else:
                parts.append(
                    f"{a} {fname}\\!\\left(\\frac{{{var}}}{{{b}}}\\right)"
                )

            if f is not None:
                from sympy import S

                if f != S.Zero:
                    parts.append(f"+ {sympy_latex(f)}")

        elif info.coefficients:
            for offset, coeff in info.coefficients:
                c = int(coeff) if coeff == int(coeff) else coeff
                if c == 1:
                    parts.append(f"{fname}({var}-{offset})")
                else:
                    parts.append(f"{c} {fname}({var}-{offset})")

            if info.nonhomogeneous_part is not None:
                from sympy import S

                if info.nonhomogeneous_part != S.Zero:
                    parts.append(f"+ {sympy_latex(info.nonhomogeneous_part)}")

        rhs = " + ".join(parts).replace("+ +", "+").replace("+ -", "-")
        return f"{fname}({var}) = {rhs}"
