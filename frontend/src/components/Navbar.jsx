import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import NotificationPanel from './NotificationPanel'
import UserAvatar from './UserAvatar'

export default function Navbar({ onMenu, role }) {
  const { user, logout } = useAuth()
  const nav = useNavigate()
  const out = async () => { await logout(); nav('/login') }
  return (
    <header className="topbar">
      <button className="btn btn-icon d-lg-none" aria-label="Open menu" onClick={onMenu}><i className="bi bi-list fs-4" /></button>
      <div className="flex-grow-1" />
      <NotificationPanel role={role} />
      <div className="dropdown">
        <button className="user-chip" data-bs-toggle="dropdown" aria-expanded="false" aria-label="Account menu">
          <UserAvatar user={user} size={32} />
          <span className="d-none d-md-block text-start lh-sm">
            <span className="d-block fw-semibold small">{user?.name?.replace(' [SEED]', '')}</span>
            <span className="d-block small text-muted text-capitalize">{user?.role}</span>
          </span>
          <i className="bi bi-chevron-down small" />
        </button>
        <ul className="dropdown-menu dropdown-menu-end shadow">
          <li><button className="dropdown-item" onClick={() => nav(`/${role}/profile`)}><i className="bi bi-person me-2" />My profile</button></li>
          <li><hr className="dropdown-divider" /></li>
          <li><button className="dropdown-item text-danger" onClick={out}><i className="bi bi-box-arrow-right me-2" />Log out</button></li>
        </ul>
      </div>
    </header>
  )
}
