import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="text-center py-5">
      <div className="text-muted mb-3"><i className="bi bi-question-circle fs-1" /></div>
      <h2 className="h4 fw-bold">Page Not Found</h2>
      <p className="text-muted">The page you were looking for doesn't exist or has moved.</p>
      <Link to="/" className="btn btn-primary btn-sm">Go to Home</Link>
    </div>
  )
}
