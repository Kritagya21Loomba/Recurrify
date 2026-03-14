import pytest
from recurrify.parser.parser import parse
from recurrify.parser.extractor import RecurrenceExtractor
from recurrify.classifier.classifier import Classifier, RecurrenceType, SolverMethod
from recurrify.solvers.master_theorem import MasterTheoremSolver
from recurrify.solvers.recursion_tree import RecursionTreeSolver
from recurrify.solvers.iteration import IterationSolver
from recurrify.solvers.characteristic import CharacteristicSolver
from recurrify.verifier.verifier import Verifier


def _parse_and_extract(text, base_cases=None):
    from recurrify.models.ast_nodes import Recurrence
    ast = parse(text)
    if base_cases:
        ast = Recurrence(ast.func_name, ast.var_name, ast.rhs, base_cases)
    return RecurrenceExtractor().extract(ast)


class TestClassifier:
    def test_divide_and_conquer(self):
        info = _parse_and_extract("T(n) = 2T(n/2) + n")
        result = Classifier().classify(info)
        assert result.recurrence_type == RecurrenceType.DIVIDE_AND_CONQUER
        assert SolverMethod.MASTER_THEOREM in result.applicable_methods

    def test_linear_homogeneous(self):
        info = _parse_and_extract("T(n) = T(n-1) + T(n-2)")
        result = Classifier().classify(info)
        assert result.recurrence_type == RecurrenceType.LINEAR_HOMOGENEOUS

    def test_linear_nonhomogeneous(self):
        info = _parse_and_extract("T(n) = T(n-1) + n")
        result = Classifier().classify(info)
        assert result.recurrence_type == RecurrenceType.LINEAR_NONHOMOGENEOUS


class TestMasterTheorem:
    @pytest.mark.parametrize("input_str,expected_case", [
        ("T(n) = 2T(n/2) + n", 2),      # Case 2: a=2, b=2, f=n, log_2(2)=1
        ("T(n) = 4T(n/2) + n", 1),      # Case 1: a=4, b=2, f=n, log_2(4)=2 > 1
        ("T(n) = 2T(n/2) + n^2", 3),    # Case 3: a=2, b=2, f=n^2, log_2(2)=1 < 2
        ("T(n) = T(n/2) + 1", 2),       # Case 2: a=1, b=2, f=1, log_2(1)=0
        ("T(n) = 9T(n/3) + n", 1),      # Case 1: a=9, b=3, f=n, log_3(9)=2 > 1
    ])
    def test_master_cases(self, input_str, expected_case):
        info = _parse_and_extract(input_str)
        solver = MasterTheoremSolver()
        assert solver.can_solve(info)
        result = solver.solve(info)
        assert result.applicable
        assert len(result.steps) >= 3


class TestRecursionTree:
    def test_basic(self):
        info = _parse_and_extract("T(n) = 2T(n/2) + n")
        solver = RecursionTreeSolver()
        assert solver.can_solve(info)
        result = solver.solve(info)
        assert result.applicable
        assert len(result.steps) >= 4
        # Should have a table
        assert any(s.table is not None for s in result.steps)


class TestIteration:
    def test_divide_and_conquer(self):
        info = _parse_and_extract("T(n) = 2T(n/2) + n")
        solver = IterationSolver()
        result = solver.solve(info)
        assert result.applicable
        assert len(result.steps) >= 3

    def test_linear_telescoping(self):
        info = _parse_and_extract("T(n) = T(n-1) + n", base_cases={1: 1})
        solver = IterationSolver()
        result = solver.solve(info)
        assert result.applicable


class TestCharacteristic:
    def test_fibonacci(self):
        info = _parse_and_extract(
            "T(n) = T(n-1) + T(n-2)", base_cases={0: 0, 1: 1}
        )
        solver = CharacteristicSolver()
        assert solver.can_solve(info)
        result = solver.solve(info)
        assert result.applicable
        assert len(result.steps) >= 3

    def test_exponential(self):
        info = _parse_and_extract(
            "T(n) = 2T(n-1) + 3T(n-2)", base_cases={0: 0, 1: 1}
        )
        solver = CharacteristicSolver()
        result = solver.solve(info)
        assert result.applicable


class TestVerifier:
    def test_numeric_verification(self):
        info = _parse_and_extract("T(n) = 2T(n/2) + n", base_cases={1: 1})
        solver = MasterTheoremSolver()
        result = solver.solve(info)
        assert result.closed_form_sympy is not None

        verifier = Verifier()
        vr = verifier.verify(info, result.closed_form_sympy)
        assert len(vr.numeric_checks) > 0
