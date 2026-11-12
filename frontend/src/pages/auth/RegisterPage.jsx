import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../../services/authService'
import ErrorMessage from '../../components/ErrorMessage'

export default function RegisterPage() {
  const nav = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(null)
  const [success, setSuccess] = useState(false)

  const handleRegister = async (e) => {
    e.preventDefault()
    setErr(null)
    setLoading(true)
    try {
      await authService.register(name, email, password)
      setSuccess(true)
    } catch (ex) {
      setErr(ex)
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="text-center py-3">
        <div className="text-success mb-2"><i className="bi bi-check-circle-fill fs-1" /></div>
        <h4 className="h5 fw-bold">Registration Successful</h4>
        <p className="text-muted small">Your customer support account has been created. You can now log in.</p>
        <button className="btn btn-primary btn-sm mt-2" onClick={() => nav('/login')}>Go to Sign In</button>
      </div>
    )
  }

  return (
    <div>
      <h3 className="h5 fw-bold mb-3">Create Customer Account</h3>
      <ErrorMessage error={err} />
      <form onSubmit={handleRegister}>
        <div className="mb-3">
          <label className="form-label small fw-medium">Full Name</label>
          <input
            type="text"
            required
            className="form-control"
            placeholder="John Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
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
        <div className="mb-3">
          <label className="form-label small fw-medium">Password</label>
          <input
            type="password"
            required
            className="form-control"
            placeholder="At least 8 chars with letters & numbers"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <div className="form-text small">Minimum 8 characters with letters and digits.</div>
        </div>
        <button type="submit" disabled={loading} className="btn btn-primary w-100 py-2 fw-medium">
          {loading ? 'Creating account...' : 'Create Account'}
        </button>
      </form>

      <div className="mt-4 pt-3 border-top text-center">
        <span className="small text-muted">Already have an account? </span>
        <Link to="/login" className="small fw-semibold text-decoration-none">Sign In</Link>
      </div>
    </div>
  )
}
