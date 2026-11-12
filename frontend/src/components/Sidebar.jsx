import { NavLink } from 'react-router-dom'
import BrandLogo from './BrandLogo'

export default function Sidebar({ items, open, onClose, roleLabel }) {
  return (
    <>
      {open && <div className="sidebar-backdrop" onClick={onClose} />}
      <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Main navigation">
        <div className="sidebar-brand">
          <BrandLogo size={36} />
          <div><div className="fw-bold lh-1 text-white">Helpdesk AI</div><div className="small opacity-75 mt-1">{roleLabel} portal</div></div>
        </div>
        <nav className="sidebar-nav">
          {items.map((it) => (
            <NavLink key={it.to} to={it.to} end={it.end} onClick={onClose}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <i className={`bi ${it.icon}`} aria-hidden="true" /><span>{it.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  )
}
