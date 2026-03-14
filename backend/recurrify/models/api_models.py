from __future__ import annotations

from pydantic import BaseModel


class ParseRequest(BaseModel):
    input: str


class ClassificationModel(BaseModel):
    recurrence_type: str
    applicable_methods: list[str]
    preferred_method: str
    reasoning: str


class ParseResponse(BaseModel):
    canonical_form: str
    recurrence_type: str
    applicable_methods: list[str]


class SolveRequest(BaseModel):
    input: str
    method: str | None = None
    base_cases: dict[int, float] | None = None


class TableModel(BaseModel):
    headers: list[str]
    rows: list[list[str]]


class StepModel(BaseModel):
    explanation: str
    latex: str
    substeps: list[StepModel] | None = None
    table: TableModel | None = None


class VerificationModel(BaseModel):
    passed: bool
    symbolic_check: str
    numeric_checks: list[dict]


class SolutionResultModel(BaseModel):
    method: str
    applicable: bool
    inapplicable_reason: str | None = None
    steps: list[StepModel]
    closed_form: str
    verification: VerificationModel | None = None


class SolveResponse(BaseModel):
    input: str
    classification: ClassificationModel
    solutions: list[SolutionResultModel]


class GuidedStartRequest(BaseModel):
    input: str


class GuidedQuestionModel(BaseModel):
    question_id: str
    prompt_text: str
    prompt_latex: str | None = None
    hint: str | None = None
    answer_type: str  # "multiple_choice" | "free_text" | "numeric"
    choices: list[str] | None = None


class GuidedStartResponse(BaseModel):
    session_id: str
    total_questions: int
    first_question: GuidedQuestionModel


class GuidedAnswerRequest(BaseModel):
    answer: str


class GuidedFeedbackModel(BaseModel):
    correct: bool
    feedback_text: str
    feedback_latex: str | None = None
    show_hint: bool = False
    session_complete: bool = False
    next_question: GuidedQuestionModel | None = None


class GuidedAnswerResponse(BaseModel):
    feedback: GuidedFeedbackModel
