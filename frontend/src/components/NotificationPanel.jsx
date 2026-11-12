import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { notificationService } from '../services/miscServices'
import { timeAgo } from '../utils/format'

export default function NotificationPanel({ role }) {
  const nav = useNavigate()
  const [open, setOpen] = useState(false)
  const [items, setItems] = useState([])
  const [unread, setUnread] = useState(0)
  const ref = useRef(null)

  const load = () => notificationService.list({ per_page: 8 })
    .then((r) => { setItems(r.data); setUnread(r.unread_count) }).catch(() => {})

  useEffect(() => {
    load()
    const t = setInterval(load, 30000)
    return () => clearInterval(t)
  }, [])
  useEffect(() => {
    const h = (e) => ref.current && !ref.current.contains(e.target) && setOpen(false)
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  const click = async (n) => {
    if (!n.is_read) await notificationService.markRead(n.notification_id).catch(() => {})
    setOpen(false); load()
    if (n.related_ticket_id) nav(`/${role}/tickets/${n.related_ticket_id}`)
  }
  const readAll = async () => { await notificationService.markAllRead(); load() }

  return (
    <div className="position-relative" ref={ref}>
      <button className="btn btn-icon position-relative" aria-label={`Notifications (${unread} unread)`}
        aria-expanded={open} onClick={() => { setOpen(!open); if (!open) load() }}>
        <i className="bi bi-bell fs-5" />
        {unread > 0 && <span className="badge-dot">{unread > 9 ? '9+' : unread}</span>}
      </button>
      {open && (
        <div className="notif-dropdown shadow">
          <div className="d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
            <strong>Notifications</strong>
            <button className="btn btn-link btn-sm p-0" onClick={readAll} disabled={!unread}>Mark all read</button>
          </div>
          <div className="notif-list">
            {items.length === 0 && <div className="p-3 text-muted small">No notifications yet.</div>}
            {items.map((n) => (
              <button key={n.notification_id} className={`notif-item ${n.is_read ? '' : 'unread'}`} onClick={() => click(n)}>
                <div className="fw-semibold small">{n.title}</div>
                <div className="small text-muted">{n.message}</div>
                <div className="small text-muted opacity-75">{timeAgo(n.created_at)}</div>
              </button>
            ))}
          </div>
          <button className="btn btn-link w-100 border-top py-2" onClick={() => { setOpen(false); nav(`/${role}/notifications`) }}>View all</button>
        </div>
      )}
    </div>
  )
}
