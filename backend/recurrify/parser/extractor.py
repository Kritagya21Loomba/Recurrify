from __future__ import annotations

from sympy import (
    Function,
    Integer,
    Rational,
    Symbol,
    log,
    sqrt,
)

from recurrify.models.ast_nodes import (
    ASTNode,
    BinOp,
    FuncCall,
    Num,
    Recurrence,
    RecurrenceInfo,
    UnaryOp,
    Var,
)


class ExtractionError(Exception):
    pass


class RecurrenceExtractor:
    """Extracts RecurrenceInfo from a parsed Recurrence AST.

    Converts the AST to SymPy expressions and identifies:
    - Divide-and-conquer form: T(n) = a*T(n/b) + f(n)
    - Linear form: T(n) = c1*T(n-1) + c2*T(n-2) + ... + g(n)
    """

    def extract(self, recurrence: Recurrence) -> RecurrenceInfo:
        n = Symbol(recurrence.var_name)
        T = Function(recurrence.func_name)

        rhs_sympy = self._ast_to_sympy(recurrence.rhs, recurrence.var_name)

        info = RecurrenceInfo(
            func_name=recurrence.func_name,
            var=recurrence.var_name,
            sympy_rhs=rhs_sympy,
        )

        if recurrence.base_cases:
            info.base_cases = dict(recurrence.base_cases)

        # Collect all recursive calls T(...)
        calls = self._collect_recursive_calls(rhs_sympy, recurrence.func_name)

        if not calls:
            raise ExtractionError("No recursive calls found in the recurrence")

        # Analyze the form of recursive calls
        divide_conquer_calls = []
        linear_calls = []

        for arg, coeff in calls:
            # Check if argument is n/b (divide-and-conquer)
            ratio = arg / n
            from sympy import simplify

            ratio_simplified = simplify(ratio)
            if ratio_simplified.is_number and ratio_simplified != 1:
                divide_conquer_calls.append((arg, coeff, ratio_simplified))
            else:
                # Check if argument is n - k (linear)
                diff = simplify(n - arg)
                if diff.is_number and diff > 0:
                    linear_calls.append((int(diff), float(coeff)))

        # Determine form
        if divide_conquer_calls and not linear_calls:
            # All same division factor?
            factors = set()
            total_a = 0
            for _arg, coeff, ratio in divide_conquer_calls:
                factors.add(ratio)
                total_a += int(coeff)

            if len(factors) == 1:
                b = 1 / float(factors.pop())
                info.num_subproblems = total_a
                info.division_factor = b

                # Driving function: remove all T(...) terms from RHS
                driving = self._remove_recursive_calls(
                    rhs_sympy, recurrence.func_name
                )
                info.driving_function = driving
        elif linear_calls and not divide_conquer_calls:
            info.coefficients = linear_calls
            # Non-homogeneous part
            nonhom = self._remove_recursive_calls(rhs_sympy, recurrence.func_name)
            from sympy import S

            if nonhom != S.Zero:
                info.nonhomogeneous_part = nonhom
        elif divide_conquer_calls and linear_calls:
            # Mixed — store what we can
            pass

        return info

    def _ast_to_sympy(self, node: ASTNode, var_name: str) -> object:
        from sympy import S

        if isinstance(node, Num):
            if node.value == int(node.value):
                return Integer(int(node.value))
            return Rational(node.value).limit_denominator(1000)

        if isinstance(node, Var):
            return Symbol(node.name)

        if isinstance(node, BinOp):
            left = self._ast_to_sympy(node.left, var_name)
            right = self._ast_to_sympy(node.right, var_name)
            if node.op == "+":
                return left + right
            if node.op == "-":
                return left - right
            if node.op == "*":
                return left * right
            if node.op == "/":
                return left / right
            if node.op == "^":
                return left**right
            raise ExtractionError(f"Unknown operator: {node.op}")

        if isinstance(node, UnaryOp):
            operand = self._ast_to_sympy(node.operand, var_name)
            if node.op == "-":
                return -operand
            raise ExtractionError(f"Unknown unary operator: {node.op}")

        if isinstance(node, FuncCall):
            args = [self._ast_to_sympy(a, var_name) for a in node.args]
            name = node.name

            # Known math functions
            if name in ("log", "lg"):
                if len(args) == 1:
                    return log(args[0], 2)  # CS convention: log = log_2
                if len(args) == 2:
                    return log(args[0], args[1])
            if name == "ln":
                return log(args[0])
            if name == "sqrt":
                return sqrt(args[0])

            # Recursive function call like T(n/2)
            T = Function(name)
            return T(*args)

        raise ExtractionError(f"Unknown AST node type: {type(node)}")

    def _collect_recursive_calls(
        self, expr, func_name: str
    ) -> list[tuple[object, object]]:
        """Find all occurrences of func_name(...) in expr and return (arg, coefficient)."""
        from sympy import Add, Mul, S

        T = Function(func_name)
        results = []

        if expr.func == T.__class__ and hasattr(expr, "name") and expr.name == func_name:
            # Direct call: T(something)
            return [(expr.args[0], S.One)]

        # Check if this is an application of our function
        if hasattr(expr, "func") and isinstance(expr.func, type) and issubclass(expr.func, Function):
            if expr.func.__name__ == func_name:
                return [(expr.args[0], S.One)]

        if expr.is_Add:
            for term in expr.args:
                results.extend(self._collect_recursive_calls(term, func_name))
        elif expr.is_Mul:
            # Look for coefficient * T(...)
            coeff = S.One
            call_arg = None
            for factor in expr.args:
                sub_calls = self._collect_recursive_calls(factor, func_name)
                if sub_calls:
                    call_arg = sub_calls[0][0]
                else:
                    coeff *= factor
            if call_arg is not None:
                results.append((call_arg, coeff))

        return results

    def _remove_recursive_calls(self, expr, func_name: str) -> object:
        """Remove all T(...) terms from expr, returning the driving function."""
        from sympy import Add, S

        if hasattr(expr, "func") and isinstance(expr.func, type) and issubclass(expr.func, Function):
            if expr.func.__name__ == func_name:
                return S.Zero

        if expr.is_Add:
            parts = []
            for term in expr.args:
                cleaned = self._remove_recursive_calls(term, func_name)
                if cleaned != S.Zero:
                    parts.append(cleaned)
            if not parts:
                return S.Zero
            return Add(*parts)

        if expr.is_Mul:
            has_call = False
            for factor in expr.args:
                if hasattr(factor, "func") and isinstance(factor.func, type) and issubclass(factor.func, Function):
                    if factor.func.__name__ == func_name:
                        has_call = True
                        break
            if has_call:
                return S.Zero
            return expr

        return expr
