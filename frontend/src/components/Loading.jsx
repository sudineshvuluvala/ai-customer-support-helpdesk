export const Loading = ({ text = 'Loading...', inline = false }) => (
  <div className={`d-flex align-items-center justify-content-center gap-2 text-muted ${inline ? '' : 'py-5'}`} role="status" aria-live="polite">
    <span className="spinner-border spinner-border-sm text-primary" aria-hidden="true" />
    <span>{text}</span>
  </div>
)
export default Loading
