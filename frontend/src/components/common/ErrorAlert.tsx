interface ErrorAlertProps {
  message: string;
  onDismiss?: () => void;
}

export function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  return (
    <div className="error-alert">
      <span>{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="error-dismiss">
          &times;
        </button>
      )}
    </div>
  );
}
