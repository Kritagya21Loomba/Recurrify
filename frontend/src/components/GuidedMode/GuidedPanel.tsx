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
      <div className="guided-header">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
          <path d="M8 7a2 2 0 0 1 4 0c0 1.5-2 1.5-2 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <circle cx="10" cy="14" r="0.75" fill="currentColor" />
        </svg>
        <h3>Guided Reasoning</h3>
      </div>

      <ProgressTracker current={history.length} total={totalQuestions} />

      {history.length > 0 && (
        <div className="guided-history">
          {history.map((item, i) => (
            <div key={i} className="history-item">
              <div className="history-q">
                <span className="history-badge">Q{i + 1}</span>
                {item.question.prompt_text}
              </div>
              <div className="history-a">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M3 7l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {item.answer}
              </div>
            </div>
          ))}
        </div>
      )}

      {complete ? (
        <div className="guided-complete">
          <div className="complete-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2" />
              <path d="M10 16l4 4 8-8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <h3>Session Complete!</h3>
          <p>You've worked through all the reasoning steps. Great job!</p>
          <button onClick={onComplete} className="btn btn-primary">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ marginRight: 6 }}>
              <path d="M6 12l4-4-4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            See Full Solution
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
