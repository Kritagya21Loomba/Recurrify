import { useState } from "react";
import type { SolveResponse, GuidedQuestion } from "./types/models";
import { InputPanel } from "./components/InputPanel";
import { SolutionDisplay } from "./components/SolutionDisplay";
import { GuidedPanel } from "./components/GuidedMode/GuidedPanel";
import { ErrorAlert } from "./components/common/ErrorAlert";
import api from "./api/client";
import "./styles/index.css";

function App() {
  const [mode, setMode] = useState<"idle" | "solve" | "guided">("idle");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [solveResult, setSolveResult] = useState<SolveResponse | null>(null);

  // Guided mode state
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
      const msg =
        err.response?.data?.detail || err.message || "Failed to solve";
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
      const msg =
        err.response?.data?.detail || err.message || "Failed to start guided mode";
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
      <header className="app-header">
        <h1>Recurrify</h1>
        <p className="subtitle">
          Recurrence relation solver, explainer &amp; verifier
        </p>
      </header>

      <main className="app-main">
        <InputPanel
          onSolve={handleSolve}
          onStartGuided={handleStartGuided}
          loading={loading}
        />

        {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

        {mode === "solve" && solveResult && (
          <SolutionDisplay result={solveResult} />
        )}

        {mode === "guided" &&
          guidedSessionId &&
          guidedFirstQuestion && (
            <GuidedPanel
              sessionId={guidedSessionId}
              totalQuestions={guidedTotalQuestions}
              firstQuestion={guidedFirstQuestion}
              onComplete={handleGuidedComplete}
            />
          )}
      </main>

      <footer className="app-footer">
        <p>Built for algorithm students. Learn the reasoning, not just the answer.</p>
      </footer>
    </div>
  );
}

export default App;
