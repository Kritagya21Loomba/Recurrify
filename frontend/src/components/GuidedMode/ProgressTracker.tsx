interface ProgressTrackerProps {
  current: number;
  total: number;
}

export function ProgressTracker({ current, total }: ProgressTrackerProps) {
  const pct = Math.round((current / total) * 100);
  return (
    <div className="progress-tracker">
      <div className="progress-meta">
        <span className="progress-text">
          Question {Math.min(current + 1, total)} of {total}
        </span>
        <span className="progress-pct">{pct}%</span>
      </div>
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
