import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '../../services/authService'
import ErrorMessage from '../../components/ErrorMessage'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(null)
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErr(null)
    setLoading(true)
    try {
      await authService.forgotPassword(email)
      setSent(true)
    } catch (ex) {
      setErr(ex)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="h5 fw-bold mb-2">Forgot Password</h3>
      <p className="text-muted small mb-4">
        Enter your registered email address and we'll send you a link to reset your password.
      </p>

      {sent ? (
        <div className="alert alert-success small">
          <div className="fw-semibold mb-1">Check your inbox</div>
          If an account exists for <strong>{email}</strong>, a password reset link has been sent. Please check your spam folder if you do not receive it in a few minutes.
          <div className="mt-3">
            <Link to="/login" className="btn btn-outline-primary btn-sm">Return to Login</Link>
          </div>
        </div>
      ) : (
        <>
          <ErrorMessage error={err} />
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label small fw-medium">Email Address</label>
              <input
                type="email"
                required
                className="form-control"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <button type="submit" disabled={loading} className="btn btn-primary w-100 py-2 fw-medium">
              {loading ? 'Sending link...' : 'Send Reset Link'}
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
