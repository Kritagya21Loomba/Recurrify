from __future__ import annotations

from fastapi import APIRouter, HTTPException

from recurrify.classifier.classifier import Classifier
from recurrify.guided.session import GuidedSession
from recurrify.models.api_models import (
    GuidedAnswerRequest,
    GuidedAnswerResponse,
    GuidedFeedbackModel,
    GuidedQuestionModel,
    GuidedStartRequest,
    GuidedStartResponse,
)
from recurrify.parser.extractor import RecurrenceExtractor
from recurrify.parser.parser import ParseError, parse

router = APIRouter()

# In-memory session store
_sessions: dict[str, GuidedSession] = {}


def _question_to_model(q) -> GuidedQuestionModel:
    return GuidedQuestionModel(
        question_id=q.question_id,
        prompt_text=q.prompt_text,
        prompt_latex=q.prompt_latex,
        hint=q.hint,
        answer_type=q.answer_type,
        choices=q.choices,
    )


@router.post("/guided/start", response_model=GuidedStartResponse)
async def start_guided(request: GuidedStartRequest):
    try:
        ast = parse(request.input)
        info = RecurrenceExtractor().extract(ast)
        classification = Classifier().classify(info)
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse recurrence: {e}")

    session = GuidedSession.create(request.input, info, classification)
    _sessions[session.session_id] = session

    first_q = session.get_current_question()
    if first_q is None:
        raise HTTPException(status_code=500, detail="No questions generated")

    return GuidedStartResponse(
        session_id=session.session_id,
        total_questions=len(session.questions),
        first_question=_question_to_model(first_q),
    )


@router.post("/guided/{session_id}/answer", response_model=GuidedAnswerResponse)
async def submit_answer(session_id: str, request: GuidedAnswerRequest):
    session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    feedback = session.submit_answer(request.answer)

    next_q = None
    if feedback.next_question:
        next_q = _question_to_model(feedback.next_question)

    return GuidedAnswerResponse(
        feedback=GuidedFeedbackModel(
            correct=feedback.correct,
            feedback_text=feedback.feedback_text,
            feedback_latex=feedback.feedback_latex,
            show_hint=feedback.show_hint,
            session_complete=feedback.session_complete,
            next_question=next_q,
        )
    )
