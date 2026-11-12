import { Link } from 'react-router-dom'
import { useAuth, homeFor } from '../../context/AuthContext'

export default function UnauthorizedPage() {
  const { user } = useAuth()
  return (
    <div className="text-center py-5">
      <div className="text-danger mb-3"><i className="bi bi-shield-x fs-1" /></div>
      <h2 className="h4 fw-bold">Access Denied</h2>
      <p className="text-muted">You do not have permission to access the requested resource or administrative functionality.</p>
      {user ? (
        <Link to={homeFor(user.role)} className="btn btn-primary btn-sm">Return to Dashboard</Link>
      ) : (
        <Link to="/login" className="btn btn-primary btn-sm">Sign In</Link>
      )}
    </div>
  )
}
