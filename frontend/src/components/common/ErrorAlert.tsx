interface ErrorAlertProps {
  message: string;
  onDismiss?: () => void;
}

export function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  return (
    <div className="error-alert">
      <div className="error-content">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" className="error-icon">
          <circle cx="9" cy="9" r="7.5" stroke="currentColor" strokeWidth="1.5" />
          <path d="M9 5.5v4M9 12v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
        <span>{message}</span>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="error-dismiss" aria-label="Dismiss">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M4 4l6 6M10 4l-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      )}
    </div>
  );
}
