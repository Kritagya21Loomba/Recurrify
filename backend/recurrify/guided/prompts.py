from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from recurrify.classifier.classifier import ClassificationResult, RecurrenceType, SolverMethod
from recurrify.models.ast_nodes import RecurrenceInfo


@dataclass
class GuidedQuestion:
    question_id: str
    prompt_text: str
    prompt_latex: str | None = None
    hint: str | None = None
    expected_answers: list[str] = field(default_factory=list)  # Acceptable answers
    answer_type: str = "free_text"  # "multiple_choice" | "free_text" | "numeric"
    choices: list[str] | None = None


def build_questions_divide_and_conquer(
    info: RecurrenceInfo, classification: ClassificationResult
) -> list[GuidedQuestion]:
    """Build guided questions for a divide-and-conquer recurrence."""
    from sympy import log, Integer, simplify, latex

    a = info.num_subproblems
    b = info.division_factor
    f = info.driving_function

    questions = [
        GuidedQuestion(
            question_id="q1_form",
            prompt_text="What form does this recurrence take?",
            prompt_latex=f"T(n) = {a}T(n/{b}) + {latex(f)}" if f else None,
            hint="Look at the structure: T(n) = a*T(n/b) + f(n)",
            expected_answers=[
                "divide and conquer",
                "divide-and-conquer",
                "master theorem",
                "T(n) = aT(n/b) + f(n)",
            ],
            answer_type="multiple_choice",
            choices=[
                "Divide-and-conquer: T(n) = aT(n/b) + f(n)",
                "Linear: T(n) = cT(n-1) + g(n)",
                "Homogeneous: T(n) = c₁T(n-1) + c₂T(n-2)",
            ],
        ),
        GuidedQuestion(
            question_id="q2_subproblems",
            prompt_text="How many subproblems are created at each step?",
            hint=f"Count the number of recursive calls: a = ?",
            expected_answers=[str(a)],
            answer_type="numeric",
        ),
        GuidedQuestion(
            question_id="q3_size",
            prompt_text="What is the size of each subproblem relative to n?",
            hint=f"Look at the argument of T: n/b where b = ?",
            expected_answers=[f"n/{b}", str(b)],
            answer_type="free_text",
        ),
        GuidedQuestion(
            question_id="q4_outside",
            prompt_text="What is the cost of the work done outside the recursion (f(n))?",
            hint="This is the non-recursive part of the recurrence.",
            expected_answers=[str(f), latex(f)] if f else ["0", "none"],
            answer_type="free_text",
        ),
    ]

    # Add Master Theorem questions
    crit_exp = simplify(log(Integer(a), Integer(b)))
    questions.append(
        GuidedQuestion(
            question_id="q5_critical",
            prompt_text="What is log_b(a)?",
            prompt_latex=f"\\log_{{{b}}} {a} = \\,?",
            hint=f"Compute log base {b} of {a}.",
            expected_answers=[str(float(crit_exp)), str(crit_exp), latex(crit_exp)],
            answer_type="free_text",
        )
    )

    questions.append(
        GuidedQuestion(
            question_id="q6_case",
            prompt_text="Which Master Theorem case applies?",
            hint="Compare the growth of f(n) with n^(log_b a).",
            expected_answers=["1", "2", "3", "case 1", "case 2", "case 3"],
            answer_type="multiple_choice",
            choices=["Case 1: f(n) grows slower", "Case 2: f(n) grows at the same rate", "Case 3: f(n) grows faster"],
        )
    )

    questions.append(
        GuidedQuestion(
            question_id="q7_result",
            prompt_text="What is the final asymptotic complexity?",
            hint="Apply the Master Theorem case you identified.",
            expected_answers=[],  # Validated more loosely
            answer_type="free_text",
        )
    )

    return questions


def build_questions_linear(
    info: RecurrenceInfo, classification: ClassificationResult
) -> list[GuidedQuestion]:
    """Build guided questions for a linear recurrence."""
    from sympy import latex

    coeffs = info.coefficients

    questions = [
        GuidedQuestion(
            question_id="q1_form",
            prompt_text="What form does this recurrence take?",
            hint="Look at how the subproblem size decreases: by subtraction or division?",
            expected_answers=["linear", "linear recurrence"],
            answer_type="multiple_choice",
            choices=[
                "Linear: T(n) = cT(n-1) + g(n)",
                "Divide-and-conquer: T(n) = aT(n/b) + f(n)",
                "Homogeneous: T(n) = c₁T(n-1) + c₂T(n-2)",
            ],
        ),
    ]

    if len(coeffs) >= 2 and info.nonhomogeneous_part is None:
        # Homogeneous — characteristic equation questions
        questions.append(
            GuidedQuestion(
                question_id="q2_char_eq",
                prompt_text="What is the characteristic equation?",
                hint="Substitute T(n) = r^n and divide by the lowest power of r.",
                expected_answers=[],
                answer_type="free_text",
            )
        )
        questions.append(
            GuidedQuestion(
                question_id="q3_roots",
                prompt_text="What are the roots of the characteristic equation?",
                hint="Solve the polynomial equation for r.",
                expected_answers=[],
                answer_type="free_text",
            )
        )
    elif info.nonhomogeneous_part is not None:
        questions.append(
            GuidedQuestion(
                question_id="q2_method",
                prompt_text="Which method would you use to solve this?",
                hint="For T(n) = T(n-1) + g(n), telescoping/iteration works well.",
                expected_answers=["iteration", "telescoping", "expansion"],
                answer_type="multiple_choice",
                choices=["Iteration/Telescoping", "Characteristic Equation", "Recursion Tree"],
            )
        )

    questions.append(
        GuidedQuestion(
            question_id="q_result",
            prompt_text="What is the final asymptotic complexity?",
            hint="Apply the method you chose and simplify.",
            expected_answers=[],
            answer_type="free_text",
        )
    )

    return questions


def build_questions(
    info: RecurrenceInfo, classification: ClassificationResult
) -> list[GuidedQuestion]:
    """Build guided questions based on the recurrence type."""
    if classification.recurrence_type == RecurrenceType.DIVIDE_AND_CONQUER:
        return build_questions_divide_and_conquer(info, classification)
    else:
        return build_questions_linear(info, classification)
