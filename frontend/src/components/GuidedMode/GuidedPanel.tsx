import { useState } from "react";
import type { GuidedQuestion, GuidedFeedback } from "../../types/models";
import { QuestionCard } from "./QuestionCard";
import { ProgressTracker } from "./ProgressTracker";
import api from "../../api/client";

interface GuidedPanelProps {
  sessionId: string;
  totalQuestions: number;
  firstQuestion: GuidedQuestion;
  onComplete: () => void;
}

export function GuidedPanel({
  sessionId,
  totalQuestions,
  firstQuestion,
  onComplete,
}: GuidedPanelProps) {
  const [currentQuestion, setCurrentQuestion] =
    useState<GuidedQuestion>(firstQuestion);
  const [feedback, setFeedback] = useState<GuidedFeedback | null>(null);
  const [history, setHistory] = useState<
    { question: GuidedQuestion; answer: string; feedback: GuidedFeedback }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [complete, setComplete] = useState(false);

  const handleSubmit = async (answer: string) => {
    setLoading(true);
    try {
      const res = await api.post(`/guided/${sessionId}/answer`, { answer });
      const fb: GuidedFeedback = res.data.feedback;
      setFeedback(fb);

      if (fb.correct) {
        setHistory([
          ...history,
          { question: currentQuestion, answer, feedback: fb },
        ]);
        if (fb.session_complete) {
          setComplete(true);
        } else if (fb.next_question) {
          setCurrentQuestion(fb.next_question);
          setFeedback(null);
        }
      }
    } catch {
      setFeedback({
        correct: false,
        feedback_text: "Error submitting answer. Please try again.",
        show_hint: false,
        session_complete: false,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="guided-panel">
      <ProgressTracker current={history.length} total={totalQuestions} />

      <div className="guided-history">
        {history.map((item, i) => (
          <div key={i} className="history-item">
            <div className="history-question">
              <strong>Q{i + 1}:</strong> {item.question.prompt_text}
            </div>
            <div className="history-answer correct">
              <strong>A:</strong> {item.answer}
            </div>
          </div>
        ))}
      </div>

      {complete ? (
        <div className="guided-complete">
          <h3>Session Complete!</h3>
          <p>
            You've worked through all the reasoning steps. Great job!
          </p>
          <button onClick={onComplete} className="btn btn-primary">
            Solve to see full solution
          </button>
        </div>
      ) : (
        <QuestionCard
          question={currentQuestion}
          onSubmit={handleSubmit}
          feedback={feedback}
          loading={loading}
        />
      )}
    </div>
  );
}
