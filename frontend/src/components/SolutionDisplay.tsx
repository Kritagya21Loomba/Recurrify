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
      <div className="classification-box">
        <h3>Classification</h3>
        <p>{result.classification.reasoning}</p>
        <p>
          <strong>Type:</strong>{" "}
          {result.classification.recurrence_type.replace("_", " ")}
        </p>
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
              <h3>{currentSolution.method}</h3>
              <StepList steps={currentSolution.steps} />

              {currentSolution.closed_form && (
                <div className="closed-form-box">
                  <h4>Result</h4>
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
          <p>No applicable solution methods found for this recurrence.</p>
          {result.solutions
            .filter((s) => !s.applicable)
            .map((s, i) => (
              <p key={i}>
                {s.method}: {s.inapplicable_reason}
              </p>
            ))}
        </div>
      )}
    </div>
  );
}
