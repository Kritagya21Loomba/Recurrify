from __future__ import annotations

from fastapi import APIRouter, HTTPException

from recurrify.classifier.classifier import Classifier, SolverMethod
from recurrify.models.api_models import (
    ClassificationModel,
    SolutionResultModel,
    SolveRequest,
    SolveResponse,
    StepModel,
    TableModel,
    VerificationModel,
)
from recurrify.models.ast_nodes import Recurrence
from recurrify.parser.extractor import RecurrenceExtractor
from recurrify.parser.parser import ParseError, parse
from recurrify.solvers.base import SolutionResult
from recurrify.solvers.characteristic import CharacteristicSolver
from recurrify.solvers.iteration import IterationSolver
from recurrify.solvers.master_theorem import MasterTheoremSolver
from recurrify.solvers.recursion_tree import RecursionTreeSolver
from recurrify.verifier.verifier import Verifier

router = APIRouter()

_SOLVERS = {
    SolverMethod.MASTER_THEOREM: MasterTheoremSolver(),
    SolverMethod.RECURSION_TREE: RecursionTreeSolver(),
    SolverMethod.ITERATION: IterationSolver(),
    SolverMethod.CHARACTERISTIC_EQUATION: CharacteristicSolver(),
}


def _solution_to_model(result: SolutionResult) -> SolutionResultModel:
    steps = []
    for s in result.steps:
        table = None
        if s.table:
            table = TableModel(headers=s.table.headers, rows=s.table.rows)
        substeps = None
        if s.substeps:
            substeps = [
                StepModel(
                    explanation=sub.explanation,
                    latex=sub.latex,
                    table=TableModel(headers=sub.table.headers, rows=sub.table.rows)
                    if sub.table
                    else None,
                )
                for sub in s.substeps
            ]
        steps.append(
            StepModel(explanation=s.explanation, latex=s.latex, substeps=substeps, table=table)
        )

    verification = None
    if result.verification:
        verification = VerificationModel(
            passed=result.verification.passed,
            symbolic_check=result.verification.symbolic_check,
            numeric_checks=result.verification.numeric_checks,
        )

    return SolutionResultModel(
        method=result.method,
        applicable=result.applicable,
        inapplicable_reason=result.inapplicable_reason,
        steps=steps,
        closed_form=result.closed_form,
        verification=verification,
    )


@router.post("/solve", response_model=SolveResponse)
async def solve_recurrence(request: SolveRequest):
    try:
        ast = parse(request.input)
        if request.base_cases:
            ast = Recurrence(ast.func_name, ast.var_name, ast.rhs, request.base_cases)
        info = RecurrenceExtractor().extract(ast)
        classification = Classifier().classify(info)
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse recurrence: {e}")

    # Determine which solvers to run
    if request.method:
        methods = [m for m in classification.applicable_methods if m.value == request.method]
        if not methods:
            methods = classification.applicable_methods
    else:
        methods = classification.applicable_methods

    verifier = Verifier()
    solutions: list[SolutionResultModel] = []

    for method in methods:
        solver = _SOLVERS.get(method)
        if solver is None:
            continue
        result = solver.solve(info)
        cf = result.closed_form_sympy
        if result.applicable and cf is not None:
            # Guard: skip verification for nan/zoo/infinite closed forms
            from sympy import zoo, oo, nan as sp_nan
            if cf not in (zoo, oo, -oo, sp_nan) and not (hasattr(cf, 'is_finite') and cf.is_finite is False):
                try:
                    result.verification = verifier.verify(info, cf)
                except Exception:
                    pass
        solutions.append(_solution_to_model(result))

    return SolveResponse(
        input=request.input,
        classification=ClassificationModel(
            recurrence_type=classification.recurrence_type.value,
            applicable_methods=[m.value for m in classification.applicable_methods],
            preferred_method=classification.preferred_method.value,
            reasoning=classification.reasoning,
        ),
        solutions=solutions,
    )
