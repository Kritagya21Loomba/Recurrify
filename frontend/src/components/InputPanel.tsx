import { useState } from "react";

interface InputPanelProps {
  onSolve: (input: string, baseCases: Record<number, number>) => void;
  onStartGuided: (input: string) => void;
  loading: boolean;
}

const EXAMPLES = [
  { label: "Merge Sort", value: "T(n) = 2T(n/2) + n" },
  { label: "Binary Search", value: "T(n) = T(n/2) + 1" },
  { label: "Karatsuba", value: "T(n) = 3T(n/2) + n" },
  { label: "Strassen", value: "T(n) = 7T(n/2) + n^2" },
  { label: "Linear Scan", value: "T(n) = T(n-1) + n" },
  { label: "Fibonacci", value: "T(n) = T(n-1) + T(n-2)" },
  { label: "Tower of Hanoi", value: "T(n) = 2T(n-1) + 1" },
  { label: "Stooge Sort", value: "T(n) = 3T(2n/3) + 1" },
];

export function InputPanel({ onSolve, onStartGuided, loading }: InputPanelProps) {
  const [input, setInput] = useState("T(n) = 2T(n/2) + n");
  const [showBaseCases, setShowBaseCases] = useState(false);
  const [baseCaseEntries, setBaseCaseEntries] = useState<{ n: string; val: string }[]>([
    { n: "1", val: "1" },
  ]);

  const buildBaseCases = (): Record<number, number> => {
    const bc: Record<number, number> = {};
    for (const entry of baseCaseEntries) {
      const n = parseInt(entry.n);
      const v = parseFloat(entry.val);
      if (!isNaN(n) && !isNaN(v)) {
        bc[n] = v;
      }
    }
    return bc;
  };

  return (
    <div className="input-panel">
      <div className="input-wrapper">
        <span className="input-icon">f(x)</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter a recurrence, e.g. T(n) = 2T(n/2) + n"
          className="recurrence-input"
          onKeyDown={(e) => {
            if (e.key === "Enter") onSolve(input, buildBaseCases());
          }}
        />
      </div>

      <div className="btn-group">
        <button
          onClick={() => onSolve(input, buildBaseCases())}
          disabled={loading || !input.trim()}
          className="btn btn-primary"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ marginRight: 6 }}>
            <path d="M6 12l4-4-4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Solve
        </button>
        <button
          onClick={() => onStartGuided(input)}
          disabled={loading || !input.trim()}
          className="btn btn-ghost"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ marginRight: 6 }}>
            <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" />
            <path d="M6.5 6a1.5 1.5 0 0 1 3 0c0 1-1.5 1-1.5 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            <circle cx="8" cy="11" r="0.5" fill="currentColor" />
          </svg>
          Guided Mode
        </button>
      </div>

      <div className="examples">
        <span className="examples-label">Try an example:</span>
        <div className="example-chips">
          {EXAMPLES.map((ex) => (
            <button
              key={ex.value}
              className="example-chip"
              onClick={() => setInput(ex.value)}
            >
              <span className="chip-label">{ex.label}</span>
              <span className="chip-formula">{ex.value}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="base-cases-section">
        <button
          className="base-cases-toggle"
          onClick={() => setShowBaseCases(!showBaseCases)}
        >
          <svg
            width="14" height="14" viewBox="0 0 14 14" fill="none"
            className={`chevron ${showBaseCases ? "open" : ""}`}
          >
            <path d="M5 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Base Cases
          <span className="base-cases-count">{baseCaseEntries.length}</span>
        </button>

        {showBaseCases && (
          <div className="base-cases">
            {baseCaseEntries.map((entry, i) => (
              <div key={i} className="base-case-row">
                <span className="bc-label">T(</span>
                <input
                  type="text"
                  value={entry.n}
                  onChange={(e) => {
                    const updated = [...baseCaseEntries];
                    updated[i] = { ...entry, n: e.target.value };
                    setBaseCaseEntries(updated);
                  }}
                  className="base-case-input"
                />
                <span className="bc-label">) =</span>
                <input
                  type="text"
                  value={entry.val}
                  onChange={(e) => {
                    const updated = [...baseCaseEntries];
                    updated[i] = { ...entry, val: e.target.value };
                    setBaseCaseEntries(updated);
                  }}
                  className="base-case-input"
                />
                <button
                  className="btn-icon-sm"
                  onClick={() => {
                    setBaseCaseEntries(baseCaseEntries.filter((_, j) => j !== i));
                  }}
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M4 4l6 6M10 4l-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                  </svg>
                </button>
              </div>
            ))}
            <button
              className="btn-link"
              onClick={() =>
                setBaseCaseEntries([...baseCaseEntries, { n: "", val: "" }])
              }
            >
              + Add base case
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
