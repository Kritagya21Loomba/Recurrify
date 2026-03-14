import type { Step } from "../types/models";
import { MathBlock } from "./common/MathBlock";

interface StepCardProps {
  step: Step;
  index: number;
}

export function StepCard({ step, index }: StepCardProps) {
  return (
    <div className="step-card">
      <div className="step-header">
        <span className="step-number">Step {index + 1}</span>
        <span className="step-explanation">{step.explanation}</span>
      </div>
      {step.latex && <MathBlock latex={step.latex} />}
      {step.table && (
        <div className="step-table-wrapper">
          <table className="step-table">
            <thead>
              <tr>
                {step.table.headers.map((h, i) => (
                  <th key={i}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {step.table.rows.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {step.substeps?.map((sub, i) => (
        <div key={i} className="substep">
          <StepCard step={sub} index={i} />
        </div>
      ))}
    </div>
  );
}

interface StepListProps {
  steps: Step[];
}

export function StepList({ steps }: StepListProps) {
  return (
    <div className="step-list">
      {steps.map((step, i) => (
        <StepCard key={i} step={step} index={i} />
      ))}
    </div>
  );
}
