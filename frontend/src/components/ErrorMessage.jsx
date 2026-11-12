export default function ErrorMessage({ error, onRetry, className = '' }) {
  if (!error) return null
  const msg = typeof error === 'string' ? error : error.message
  const details = typeof error === 'object' && error.details ? Object.entries(error.details) : []
  return (
    <div className={`alert alert-danger d-flex flex-column gap-1 ${className}`} role="alert">
      <div className="d-flex justify-content-between align-items-center gap-2">
        <span>{msg}</span>
        {onRetry && <button className="btn btn-sm btn-outline-danger" onClick={onRetry}>Retry</button>}
      </div>
      {details.length > 0 && (
        <ul className="mb-0 small">{details.map(([k, v]) => <li key={k}><strong>{k}</strong>: {String(v)}</li>)}</ul>
      )}
    </div>
  )
}
