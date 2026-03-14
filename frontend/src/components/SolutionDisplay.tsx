import { useState } from "react";
import type { SolveResponse } from "../types/models";
import { MethodSelector } from "./MethodSelector";
import { StepList } from "./StepCard";
import { VerificationBadge } from "./VerificationBadge";
import { MathBlock } from "./common/MathBlock";

interface SolutionDisplayProps {
  result: SolveResponse;
}

export function SolutionDisplay({ result }: SolutionDisplayProps) {
  const applicableSolutions = result.solutions.filter((s) => s.applicable);
  const [selectedMethod, setSelectedMethod] = useState(
    applicableSolutions[0]?.method || ""
  );

  const currentSolution = applicableSolutions.find(
    (s) => s.method === selectedMethod
  );

  return (
    <div className="solution-display">
      <div className="section-label">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M8 2v12M2 8h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
        Analysis
      </div>

      <div className="classification-box">
        <div className="classification-header">
          <span className="classification-tag">
            {result.classification.recurrence_type.replace(/_/g, " ")}
          </span>
        </div>
        <p className="classification-reasoning">{result.classification.reasoning}</p>
      </div>

      {applicableSolutions.length > 0 ? (
        <>
          <MethodSelector
            methods={applicableSolutions.map((s) => s.method)}
            selected={selectedMethod}
            onSelect={setSelectedMethod}
          />

          {currentSolution && (
            <div className="method-solution">
              <div className="method-title">
                <h3>{currentSolution.method}</h3>
              </div>
              <StepList steps={currentSolution.steps} />

              {currentSolution.closed_form && (
                <div className="closed-form-box">
                  <div className="closed-form-label">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M2 8h12M8 2l6 6-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    Closed Form
                  </div>
                  <MathBlock latex={currentSolution.closed_form} />
                </div>
              )}

              {currentSolution.verification && (
                <VerificationBadge
                  verification={currentSolution.verification}
                />
              )}
            </div>
          )}
        </>
      ) : (
        <div className="no-solution">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
            <path d="M10 6v5M10 13v1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <div>
            <p>No applicable solution methods found for this recurrence.</p>
            {result.solutions
              .filter((s) => !s.applicable)
              .map((s, i) => (
                <p key={i} className="inapplicable-reason">
                  <strong>{s.method}:</strong> {s.inapplicable_reason}
                </p>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
