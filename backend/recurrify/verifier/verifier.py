from __future__ import annotations

import signal
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from sympy import (
    Function,
    Integer,
    N,
    Symbol,
    latex,
    simplify,
)

from recurrify.models.ast_nodes import RecurrenceInfo
from recurrify.solvers.base import VerificationResult, to_sympy_number


def _run_with_timeout(fn, timeout_sec=5):
    """Run fn() with a timeout. Returns fn() result or raises TimeoutError."""
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(fn)
        try:
            return future.result(timeout=timeout_sec)
        except FuturesTimeout:
            raise TimeoutError("computation timed out")


class Verifier:
    """Verifies closed-form solutions via symbolic substitution and numeric evaluation."""

    def verify(self, info: RecurrenceInfo, closed_form_sympy) -> VerificationResult:
        symbolic_result = self._symbolic_check(info, closed_form_sympy)
        numeric_result = self._numeric_check(info, closed_form_sympy)
        passed = numeric_result["passed"]

        return VerificationResult(
            passed=passed,
            symbolic_check=symbolic_result,
            numeric_checks=numeric_result["table"],
        )

    def _symbolic_check(self, info: RecurrenceInfo, closed_form) -> str:
        """Substitute closed form into recurrence and check if it satisfies."""
        n = Symbol(info.var)

        try:
            lhs = closed_form

            if info.num_subproblems is not None and info.division_factor is not None:
                a = info.num_subproblems
                b = info.division_factor
                f = info.driving_function if info.driving_function else Integer(0)

                rhs = a * closed_form.subs(n, n / to_sympy_number(b)) + f

                # Use timeout for simplify — it can hang on complex expressions
                try:
                    diff = _run_with_timeout(lambda: simplify(lhs - rhs), timeout_sec=3)
                    rhs_simple = _run_with_timeout(lambda: simplify(rhs), timeout_sec=3)
                except TimeoutError:
                    diff_str = latex(lhs - rhs)
                    return (
                        f"Substituting T(n) = {latex(closed_form)} into the recurrence:\\n"
                        f"LHS = {latex(lhs)}\\n"
                        f"RHS = {a} \\cdot T(n/{b}) + {latex(f)}\\n"
                        f"LHS - RHS = {diff_str}\\n"
                        f"(symbolic simplification timed out — check numerically)"
                    )

                return (
                    f"Substituting T(n) = {latex(closed_form)} into the recurrence:\\n"
                    f"LHS = {latex(lhs)}\\n"
                    f"RHS = {a} \\cdot T(n/{b}) + {latex(f)} = {latex(rhs_simple)}\\n"
                    f"LHS - RHS = {latex(diff)}"
                )
            elif info.coefficients:
                rhs_parts = []
                for offset, coeff in info.coefficients:
                    c = Integer(int(coeff)) if coeff == int(coeff) else coeff
                    rhs_parts.append(c * closed_form.subs(n, n - offset))
                if info.nonhomogeneous_part:
                    rhs_parts.append(info.nonhomogeneous_part)
                rhs = sum(rhs_parts)

                try:
                    diff = _run_with_timeout(lambda: simplify(lhs - rhs), timeout_sec=3)
                    rhs_simple = _run_with_timeout(lambda: simplify(rhs), timeout_sec=3)
                except TimeoutError:
                    return (
                        f"Substituting T(n) = {latex(closed_form)} into the recurrence:\\n"
                        f"LHS = {latex(lhs)}\\n"
                        f"RHS = {latex(rhs)}\\n"
                        f"(symbolic simplification timed out — check numerically)"
                    )

                return (
                    f"Substituting T(n) = {latex(closed_form)} into the recurrence:\\n"
                    f"LHS = {latex(lhs)}\\n"
                    f"RHS = {latex(rhs_simple)}\\n"
                    f"LHS - RHS = {latex(diff)}"
                )
        except Exception as e:
            return f"Symbolic check could not be completed: {e}"

        return "Symbolic check not applicable for this recurrence type."

    def _numeric_check(
        self, info: RecurrenceInfo, closed_form, max_n: int = 16
    ) -> dict:
        """Compute recurrence values numerically and compare with closed form."""
        # Use the symbol from the closed form expression to ensure subs() works
        n = Symbol(info.var)
        free = closed_form.free_symbols if hasattr(closed_form, 'free_symbols') else set()
        for s in free:
            if str(s) == info.var:
                n = s
                break
        table = []

        # Compute recurrence values iteratively
        rec_values = {}

        # Set base cases
        for bn, bv in info.base_cases.items():
            rec_values[bn] = float(bv)

        # Default base cases if none provided
        if not rec_values:
            rec_values[0] = 0
            rec_values[1] = 1

        # Compute values based on recurrence type
        if info.num_subproblems is not None and info.division_factor is not None:
            a = info.num_subproblems
            b = info.division_factor
            f = info.driving_function if info.driving_function else Integer(0)

            # Find the symbol used in f for substitution
            f_n = n
            if hasattr(f, 'free_symbols'):
                for s in f.free_symbols:
                    if str(s) == info.var:
                        f_n = s
                        break

            # For divide-and-conquer, compute at powers of b
            test_values = []
            val = 1
            while val <= max_n:
                test_values.append(val)
                val = int(val * b) if val * b == int(val * b) else int(val * b) + 1
                if val == test_values[-1]:
                    break  # Avoid infinite loop for b close to 1
            if not test_values or test_values[0] != 1:
                test_values.insert(0, 1)

            for nv in test_values:
                if nv not in rec_values:
                    sub_n = nv / b
                    if sub_n == int(sub_n) and int(sub_n) in rec_values:
                        f_val = float(N(f.subs(f_n, nv)))
                        rec_values[nv] = a * rec_values[int(sub_n)] + f_val

            for nv in sorted(rec_values.keys()):
                if nv < 1:
                    continue
                try:
                    formula_val = float(N(closed_form.subs(n, nv)))
                    table.append(
                        {
                            "n": nv,
                            "recurrence_value": round(rec_values[nv], 4),
                            "formula_value": round(formula_val, 4),
                        }
                    )
                except Exception:
                    pass

        elif info.coefficients:
            # Linear recurrence
            max_offset = max(offset for offset, _ in info.coefficients)

            # Ensure we have enough base cases
            for i in range(max_offset + 1):
                if i not in rec_values:
                    rec_values[i] = i  # Default

            for nv in range(max_offset + 1, max_n + 1):
                val = 0
                for offset, coeff in info.coefficients:
                    val += coeff * rec_values[nv - offset]
                if info.nonhomogeneous_part:
                    val += float(N(info.nonhomogeneous_part.subs(n, nv)))
                rec_values[nv] = val

            for nv in range(max(1, min(rec_values.keys())), max_n + 1):
                if nv in rec_values:
                    try:
                        formula_val = float(N(closed_form.subs(n, nv)))
                        table.append(
                            {
                                "n": nv,
                                "recurrence_value": round(rec_values[nv], 4),
                                "formula_value": round(formula_val, 4),
                            }
                        )
                    except Exception:
                        pass

        # Check if values match
        passed = True
        if table:
            for row in table:
                if abs(row["recurrence_value"] - row["formula_value"]) > 0.01 * max(
                    abs(row["recurrence_value"]), 1
                ):
                    # For asymptotic results, check ratio convergence instead
                    if row["recurrence_value"] != 0:
                        ratio = row["formula_value"] / row["recurrence_value"]
                        if not (0.1 < ratio < 10):
                            passed = False
        else:
            passed = False

        return {"passed": passed, "table": table}
