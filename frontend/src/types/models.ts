export interface Step {
  explanation: string;
  latex: string;
  substeps?: Step[];
  table?: { headers: string[]; rows: string[][] };
}

export interface VerificationResult {
  passed: boolean;
  symbolic_check: string;
  numeric_checks: { n: number; recurrence_value: number; formula_value: number }[];
}

export interface Solution {
  method: string;
  applicable: boolean;
  inapplicable_reason?: string;
  steps: Step[];
  closed_form: string;
  verification?: VerificationResult;
}

export interface Classification {
  recurrence_type: string;
  applicable_methods: string[];
  preferred_method: string;
  reasoning: string;
}

export interface SolveResponse {
  input: string;
  classification: Classification;
  solutions: Solution[];
}

export interface GuidedQuestion {
  question_id: string;
  prompt_text: string;
  prompt_latex?: string;
  hint?: string;
  answer_type: "multiple_choice" | "free_text" | "numeric";
  choices?: string[];
}

export interface GuidedFeedback {
  correct: boolean;
  feedback_text: string;
  feedback_latex?: string;
  show_hint: boolean;
  session_complete: boolean;
  next_question?: GuidedQuestion;
}

export interface GuidedStartResponse {
  session_id: string;
  total_questions: number;
  first_question: GuidedQuestion;
}

export interface AppState {
  mode: "solve" | "guided";
  input: string;
  baseCases: Record<number, number>;
  loading: boolean;
  error: string | null;
  solveResult: SolveResponse | null;
  selectedMethod: string | null;
  guidedSessionId: string | null;
  currentQuestion: GuidedQuestion | null;
  questionHistory: {
    question: GuidedQuestion;
    answer: string;
    feedback: GuidedFeedback;
  }[];
  totalQuestions: number;
}
