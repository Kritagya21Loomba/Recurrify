from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from recurrify.classifier.classifier import ClassificationResult
from recurrify.guided.prompts import GuidedQuestion, build_questions
from recurrify.models.ast_nodes import RecurrenceInfo


@dataclass
class GuidedFeedback:
    correct: bool
    feedback_text: str
    feedback_latex: str | None = None
    show_hint: bool = False
    session_complete: bool = False
    next_question: GuidedQuestion | None = None


@dataclass
class GuidedSession:
    session_id: str
    recurrence_input: str
    info: RecurrenceInfo
    classification: ClassificationResult
    questions: list[GuidedQuestion]
    current_question_index: int = 0
    student_answers: list[tuple[str, bool]] = field(default_factory=list)
    attempts_on_current: int = 0

    @classmethod
    def create(
        cls,
        recurrence_input: str,
        info: RecurrenceInfo,
        classification: ClassificationResult,
    ) -> GuidedSession:
        questions = build_questions(info, classification)
        return cls(
            session_id=str(uuid.uuid4()),
            recurrence_input=recurrence_input,
            info=info,
            classification=classification,
            questions=questions,
        )

    def get_current_question(self) -> GuidedQuestion | None:
        if self.current_question_index >= len(self.questions):
            return None
        return self.questions[self.current_question_index]

    def submit_answer(self, answer: str) -> GuidedFeedback:
        question = self.get_current_question()
        if question is None:
            return GuidedFeedback(
                correct=True,
                feedback_text="Session is already complete!",
                session_complete=True,
            )

        self.attempts_on_current += 1
        correct = self._check_answer(answer, question)
        self.student_answers.append((answer, correct))

        if correct:
            self.current_question_index += 1
            self.attempts_on_current = 0
            next_q = self.get_current_question()
            is_complete = next_q is None

            return GuidedFeedback(
                correct=True,
                feedback_text="Correct!",
                session_complete=is_complete,
                next_question=next_q,
            )
        else:
            show_hint = self.attempts_on_current >= 2
            feedback = "Not quite. "
            if show_hint and question.hint:
                feedback += f"Hint: {question.hint}"
            else:
                feedback += "Try again!"

            return GuidedFeedback(
                correct=False,
                feedback_text=feedback,
                show_hint=show_hint,
                next_question=question,  # Same question again
            )

    def _check_answer(self, answer: str, question: GuidedQuestion) -> bool:
        """Flexible answer matching."""
        answer_clean = answer.strip().lower().replace(" ", "")

        # If no expected answers, accept anything (final result questions)
        if not question.expected_answers:
            return True

        for expected in question.expected_answers:
            expected_clean = expected.strip().lower().replace(" ", "")
            if answer_clean == expected_clean:
                return True
            # Partial match for longer expected answers
            if len(expected_clean) > 3 and expected_clean in answer_clean:
                return True

        # For multiple choice, check if they selected the right option index
        if question.answer_type == "multiple_choice" and question.choices:
            for i, choice in enumerate(question.choices):
                choice_clean = choice.strip().lower().replace(" ", "")
                if answer_clean == str(i) or answer_clean == str(i + 1):
                    # Check if this choice matches any expected answer
                    for expected in question.expected_answers:
                        if expected.strip().lower() in choice_clean:
                            return True

        # For numeric, try parsing
        if question.answer_type == "numeric":
            try:
                answer_val = float(answer)
                for expected in question.expected_answers:
                    try:
                        expected_val = float(expected)
                        if abs(answer_val - expected_val) < 0.01:
                            return True
                    except ValueError:
                        pass
            except ValueError:
                pass

        return False
