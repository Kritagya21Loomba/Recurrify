import type { VerificationResult } from "../types/models";
import { useState } from "react";

interface VerificationBadgeProps {
  verification: VerificationResult;
}

export function VerificationBadge({ verification }: VerificationBadgeProps) {
  const [expanded, setExpanded] = useState(false);
  const passed = verification.passed;

  return (
    <div className={`verification-badge ${passed ? "passed" : "failed"}`}>
      <button
        className="verification-toggle"
        onClick={() => setExpanded(!expanded)}
      >
        <span className={`verification-dot ${passed ? "dot-pass" : "dot-fail"}`} />
        <span className="verification-label">
          Verification {passed ? "Passed" : "— Check Details"}
        </span>
        <svg
          width="14" height="14" viewBox="0 0 14 14" fill="none"
          className={`toggle-chevron ${expanded ? "open" : ""}`}
        >
          <path d="M4 5l3 3 3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {expanded && (
        <div className="verification-details">
          <div className="verification-section">
            <h4>Symbolic Check</h4>
            <pre>{verification.symbolic_check}</pre>
          </div>

          {verification.numeric_checks.length > 0 && (
            <div className="verification-section">
              <h4>Numeric Verification</h4>
              <div className="table-scroll">
                <table className="verification-table">
                  <thead>
                    <tr>
                      <th>n</th>
                      <th>Recurrence</th>
                      <th>Formula</th>
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
                          <td>{Number(row.recurrence_value.toFixed(4))}</td>
                          <td>{Number(row.formula_value.toFixed(4))}</td>
                          <td>
                            <span className={`match-icon ${match ? "match-yes" : "match-approx"}`}>
                              {match ? "\u2713" : "\u2248"}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
