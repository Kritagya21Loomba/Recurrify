import { useState } from "react";

interface InputPanelProps {
  onSolve: (input: string, baseCases: Record<number, number>) => void;
  onStartGuided: (input: string) => void;
  loading: boolean;
}

const EXAMPLE_RECURRENCES = [
  "T(n) = 2T(n/2) + n",
  "T(n) = 4T(n/2) + n",
  "T(n) = 2T(n/2) + n^2",
  "T(n) = T(n/2) + 1",
  "T(n) = T(n-1) + n",
  "T(n) = T(n-1) + T(n-2)",
  "T(n) = 2T(n-1) + 3T(n-2)",
  "T(n) = 9T(n/3) + n",
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
      <div className="input-row">
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
        <button
          onClick={() => onSolve(input, buildBaseCases())}
          disabled={loading || !input.trim()}
          className="btn btn-primary"
        >
          {loading ? "Solving..." : "Solve"}
        </button>
        <button
          onClick={() => onStartGuided(input)}
          disabled={loading || !input.trim()}
          className="btn btn-secondary"
        >
          Guided Mode
        </button>
      </div>

      <div className="examples">
        <span className="examples-label">Examples:</span>
        {EXAMPLE_RECURRENCES.map((ex) => (
          <button
            key={ex}
            className="example-btn"
            onClick={() => setInput(ex)}
          >
            {ex}
          </button>
        ))}
      </div>

      <div className="base-cases-toggle">
        <button
          className="btn-link"
          onClick={() => setShowBaseCases(!showBaseCases)}
        >
          {showBaseCases ? "Hide" : "Show"} Base Cases
        </button>
      </div>

      {showBaseCases && (
        <div className="base-cases">
          {baseCaseEntries.map((entry, i) => (
            <div key={i} className="base-case-row">
              <span>T(</span>
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
              <span>) =</span>
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
                className="btn-icon"
                onClick={() => {
                  setBaseCaseEntries(baseCaseEntries.filter((_, j) => j !== i));
                }}
              >
                &times;
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
  );
}
