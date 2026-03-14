import { useState } from "react";
import type { SolveResponse, GuidedQuestion } from "./types/models";
import { InputPanel } from "./components/InputPanel";
import { SolutionDisplay } from "./components/SolutionDisplay";
import { GuidedPanel } from "./components/GuidedMode/GuidedPanel";
import { ErrorAlert } from "./components/common/ErrorAlert";
import api from "./api/client";
import "./styles/index.css";

function getErrorMessage(err: any, fallback: string): string {
  if (err.response?.data?.detail) return err.response.data.detail;
  if (err.code === "ECONNABORTED") return "Request timed out — is the backend running?";
  if (err.code === "ERR_NETWORK") return "Cannot reach backend — start it with: cd backend && py -3.11 -m uvicorn main:app --reload";
  return err.message || fallback;
}

function App() {
  const [mode, setMode] = useState<"idle" | "solve" | "guided">("idle");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [solveResult, setSolveResult] = useState<SolveResponse | null>(null);

  const [guidedSessionId, setGuidedSessionId] = useState<string | null>(null);
  const [guidedTotalQuestions, setGuidedTotalQuestions] = useState(0);
  const [guidedFirstQuestion, setGuidedFirstQuestion] =
    useState<GuidedQuestion | null>(null);
  const [lastInput, setLastInput] = useState("");

  const handleSolve = async (
    input: string,
    baseCases: Record<number, number>
  ) => {
    setLoading(true);
    setError(null);
    setSolveResult(null);
    setMode("solve");
    setLastInput(input);

    try {
      const res = await api.post("/solve", {
        input,
        base_cases: Object.keys(baseCases).length > 0 ? baseCases : undefined,
      });
      setSolveResult(res.data);
    } catch (err: any) {
      const msg = getErrorMessage(err, "Failed to solve");
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleStartGuided = async (input: string) => {
    setLoading(true);
    setError(null);
    setSolveResult(null);
    setMode("guided");
    setLastInput(input);

    try {
      const res = await api.post("/guided/start", { input });
      setGuidedSessionId(res.data.session_id);
      setGuidedTotalQuestions(res.data.total_questions);
      setGuidedFirstQuestion(res.data.first_question);
    } catch (err: any) {
      const msg = getErrorMessage(err, "Failed to start guided mode");
      setError(msg);
      setMode("idle");
    } finally {
      setLoading(false);
    }
  };

  const handleGuidedComplete = () => {
    handleSolve(lastInput, {});
  };

  return (
    <div className="app">
      <div className="glow glow-1" />
      <div className="glow glow-2" />

      <header className="app-header">
        <div className="logo-mark">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <rect width="36" height="36" rx="10" fill="url(#lg)" />
            <path d="M10 24V12l4.5 6.5L19 12v12" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="25" cy="18" r="4" stroke="#fff" strokeWidth="2.2" />
            <defs>
              <linearGradient id="lg" x1="0" y1="0" x2="36" y2="36">
                <stop stopColor="#6c8cff" />
                <stop offset="1" stopColor="#a78bfa" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div>
          <h1>Recurrify</h1>
          <p className="subtitle">
            Step-by-step recurrence relation solver for algorithm students
          </p>
        </div>
      </header>

      <main className="app-main">
        <InputPanel
          onSolve={handleSolve}
          onStartGuided={handleStartGuided}
          loading={loading}
        />

        {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

        {loading && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Analyzing recurrence...</p>
          </div>
        )}

        {mode === "solve" && solveResult && !loading && (
          <div className="fade-in">
            <SolutionDisplay result={solveResult} />
          </div>
        )}

        {mode === "guided" &&
          guidedSessionId &&
          guidedFirstQuestion &&
          !loading && (
            <div className="fade-in">
              <GuidedPanel
                sessionId={guidedSessionId}
                totalQuestions={guidedTotalQuestions}
                firstQuestion={guidedFirstQuestion}
                onComplete={handleGuidedComplete}
              />
            </div>
          )}
      </main>

      <footer className="app-footer">
        <p>Built for algorithm students &middot; Learn the reasoning, not just the answer</p>
      </footer>
    </div>
  );
}

export default App;
