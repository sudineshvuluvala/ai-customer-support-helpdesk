import { Navigate, Outlet } from 'react-router-dom'
import { useAuth, homeFor } from '../context/AuthContext'

export default function RoleBasedRoute({ allowedRoles }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />
  }
  return <Outlet />
}
