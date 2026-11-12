import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { authService } from '../../services/authService'
import ErrorMessage from '../../components/ErrorMessage'

export default function ResetPasswordPage() {
  const [params] = useSearchParams()
  const token = params.get('token') || ''
  const nav = useNavigate()

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErr(null)
    if (password !== confirmPassword) {
      setErr({ message: 'Passwords do not match.' })
      return
    }
    if (password.length < 8) {
      setErr({ message: 'Password must be at least 8 characters long.' })
      return
    }
    setLoading(true)
    try {
      await authService.resetPassword(token, password)
      setSuccess(true)
      setTimeout(() => nav('/login'), 3000)
    } catch (ex) {
      setErr(ex)
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="text-center py-4">
        <div className="alert alert-danger small">
          Invalid or missing password reset token.
        </div>
        <Link to="/forgot-password" className="btn btn-outline-primary btn-sm">Request New Link</Link>
      </div>
    )
  }

  return (
    <div>
      <h3 className="h5 fw-bold mb-2">Create New Password</h3>
      <p className="text-muted small mb-4">Choose a strong password of at least 8 characters.</p>

      {success ? (
        <div className="alert alert-success small">
          <div className="fw-semibold mb-1">Password reset successful!</div>
          Your password has been updated. Redirecting you to login...
          <div className="mt-3">
            <Link to="/login" className="btn btn-primary btn-sm">Sign In Now</Link>
          </div>
        </div>
      ) : (
        <>
          <ErrorMessage error={err} />
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label small fw-medium">New Password</label>
              <input
                type="password"
                required
                className="form-control"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <div className="form-text small">At least 8 characters, including upper, lower &amp; digits.</div>
            </div>

            <div className="mb-3">
              <label className="form-label small fw-medium">Confirm New Password</label>
              <input
                type="password"
                required
                className="form-control"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary w-100 py-2 fw-medium">
              {loading ? 'Updating password...' : 'Update Password'}
            </button>
          </form>

          <div className="mt-4 pt-3 border-top text-center">
            <Link to="/login" className="small fw-semibold text-decoration-none">
              <i className="bi bi-arrow-left me-1" /> Back to Login
            </Link>
          </div>
        </>
      )}
    </div>
  )
}
