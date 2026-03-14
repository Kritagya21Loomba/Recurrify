import type { VerificationResult } from "../types/models";
import { useState } from "react";

interface VerificationBadgeProps {
  verification: VerificationResult;
}

export function VerificationBadge({ verification }: VerificationBadgeProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`verification-badge ${verification.passed ? "passed" : "failed"}`}>
      <button
        className="verification-toggle"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="verification-icon">
          {verification.passed ? "\u2713" : "\u2717"}
        </span>
        <span>
          Verification: {verification.passed ? "Passed" : "Check Details"}
        </span>
        <span className="toggle-arrow">{expanded ? "\u25B2" : "\u25BC"}</span>
      </button>

      {expanded && (
        <div className="verification-details">
          <div className="symbolic-check">
            <h4>Symbolic Check</h4>
            <pre>{verification.symbolic_check}</pre>
          </div>

          {verification.numeric_checks.length > 0 && (
            <div className="numeric-check">
              <h4>Numeric Verification</h4>
              <table className="verification-table">
                <thead>
                  <tr>
                    <th>n</th>
                    <th>Recurrence Value</th>
                    <th>Formula Value</th>
                    <th>Match</th>
                  </tr>
                </thead>
                <tbody>
                  {verification.numeric_checks.map((row, i) => {
                    const match =
                      Math.abs(row.recurrence_value - row.formula_value) <
                      0.01 * Math.max(Math.abs(row.recurrence_value), 1);
                    return (
                      <tr key={i}>
                        <td>{row.n}</td>
                        <td>{row.recurrence_value}</td>
                        <td>{row.formula_value}</td>
                        <td>{match ? "\u2713" : "\u2248"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
