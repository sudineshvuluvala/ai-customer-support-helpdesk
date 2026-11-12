import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Loading from '../components/Loading'

export default function ProtectedRoute() {
  const { user, loading } = useAuth()
  if (loading) return <div className="vh-100 d-flex align-items-center justify-content-center"><Loading text="Authenticating..." /></div>
  if (!user) return <Navigate to="/login" replace />
  return <Outlet />
}
