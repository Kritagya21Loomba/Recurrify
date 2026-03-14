import { useState } from "react";
import type { GuidedQuestion, GuidedFeedback } from "../../types/models";
import { MathBlock } from "../common/MathBlock";

interface QuestionCardProps {
  question: GuidedQuestion;
  onSubmit: (answer: string) => void;
  feedback: GuidedFeedback | null;
  loading: boolean;
}

export function QuestionCard({
  question,
  onSubmit,
  feedback,
  loading,
}: QuestionCardProps) {
  const [answer, setAnswer] = useState("");

  const handleSubmit = () => {
    if (answer.trim()) {
      onSubmit(answer);
      setAnswer("");
    }
  };

  return (
    <div className="question-card">
      <p className="question-text">{question.prompt_text}</p>
      {question.prompt_latex && <MathBlock latex={question.prompt_latex} />}

      {question.answer_type === "multiple_choice" && question.choices ? (
        <div className="choices">
          {question.choices.map((choice, i) => (
            <button
              key={i}
              className={`choice-btn ${answer === choice ? "selected" : ""}`}
              onClick={() => {
                setAnswer(choice);
                onSubmit(choice);
              }}
              disabled={loading}
            >
              {choice}
            </button>
          ))}
        </div>
      ) : (
        <div className="answer-input-row">
          <input
            type="text"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder={
              question.answer_type === "numeric"
                ? "Enter a number..."
                : "Type your answer..."
            }
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSubmit();
            }}
            disabled={loading}
            className="answer-input"
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !answer.trim()}
            className="btn btn-primary"
          >
            Submit
          </button>
        </div>
      )}

      {feedback && (
        <div
          className={`feedback ${feedback.correct ? "correct" : "incorrect"}`}
        >
          <p>{feedback.feedback_text}</p>
          {feedback.feedback_latex && (
            <MathBlock latex={feedback.feedback_latex} />
          )}
        </div>
      )}
    </div>
  );
}
