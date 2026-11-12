import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth, homeFor } from '../../context/AuthContext'
import ErrorMessage from '../../components/ErrorMessage'

export default function LoginPage() {
  const { login, notice } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(null)

  const handleLogin = async (e) => {
    e.preventDefault()
    setErr(null)
    setLoading(true)
    try {
      const u = await login(email, password)
      nav(homeFor(u.role), { replace: true })
    } catch (ex) {
      setErr(ex)
    } finally {
      setLoading(false)
    }
  }

  const fillQuick = (e, p) => {
    setEmail(e)
    setPassword(p)
  }

  return (
    <div>
      <h3 className="h5 fw-bold mb-3">Sign In to Your Account</h3>
      {notice && <div className="alert alert-info py-2 small">{notice}</div>}
      <ErrorMessage error={err} />
      <form onSubmit={handleLogin}>
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
          <div className="d-flex justify-content-between align-items-center mb-1">
            <label className="form-label small fw-medium mb-0">Password</label>
            <Link to="/forgot-password" className="small text-decoration-none">Forgot password?</Link>
          </div>
          <input
            type="password"
            required
            className="form-control"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type="submit" disabled={loading} className="btn btn-primary w-100 py-2 fw-medium">
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>

      <div className="mt-4 pt-3 border-top text-center">
        <span className="small text-muted">Don't have an account? </span>
        <Link to="/register" className="small fw-semibold text-decoration-none">Register as Customer</Link>
      </div>

      <div className="mt-4 p-3 bg-light rounded border text-start">
        <div className="small fw-bold text-uppercase text-muted mb-2">Development Demo Logins</div>
        <div className="d-flex flex-wrap gap-1">
          <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => fillQuick('admin@helpdesk.local', 'Demo@12345')}>
            Admin
          </button>
          <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => fillQuick('agent1@helpdesk.local', 'Demo@12345')}>
            Agent Alice
          </button>
          <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => fillQuick('customer1@helpdesk.local', 'Demo@12345')}>
            Customer Carol
          </button>
        </div>
      </div>
    </div>
  )
}
