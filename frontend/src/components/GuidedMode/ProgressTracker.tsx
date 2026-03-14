interface ProgressTrackerProps {
  current: number;
  total: number;
}

export function ProgressTracker({ current, total }: ProgressTrackerProps) {
  return (
    <div className="progress-tracker">
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${(current / total) * 100}%` }}
        />
      </div>
      <span className="progress-text">
        Question {Math.min(current + 1, total)} of {total}
      </span>
    </div>
  );
}
