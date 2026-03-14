interface MethodSelectorProps {
  methods: string[];
  selected: string;
  onSelect: (method: string) => void;
}

export function MethodSelector({ methods, selected, onSelect }: MethodSelectorProps) {
  return (
    <div className="method-selector">
      <span className="method-selector-label">Solution Method</span>
      <div className="method-tabs">
        {methods.map((method) => (
          <button
            key={method}
            className={`method-tab ${selected === method ? "active" : ""}`}
            onClick={() => onSelect(method)}
          >
            {method}
          </button>
        ))}
      </div>
    </div>
  );
}
