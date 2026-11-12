import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { notificationService } from '../../services/miscServices'
import { useFetch } from '../../hooks/useFetch'
import Pagination from '../../components/Pagination'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'
import { fmtDate } from '../../utils/format'

export default function NotificationsPage() {
  const nav = useNavigate()
  const [page, setPage] = useState(1)
  const { data, loading, error, reload } = useFetch(
    () => notificationService.list({ page, per_page: 15 }),
    [page]
  )

  const handleMarkAll = async () => {
    try {
      await notificationService.markAllRead()
      reload()
    } catch {
      /* ignore */
    }
  }

  const handleClick = async (n) => {
    if (!n.is_read) await notificationService.markRead(n.notification_id).catch(() => {})
    if (n.related_ticket_id) nav(`/customer/tickets/${n.related_ticket_id}`)
    else reload()
  }

  return (
    <div className="row justify-content-center">
      <div className="col-lg-8">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h1 className="h4 fw-bold mb-0">System Notifications</h1>
            <p className="text-muted small mb-0">Stay informed on ticket responses, status changes, and assignments.</p>
          </div>
          <button className="btn btn-outline-secondary btn-sm" onClick={handleMarkAll}>
            Mark All as Read
          </button>
        </div>

        {loading && <Loading text="Fetching notifications..." />}
        {error && <ErrorMessage error={error} onRetry={reload} />}

        <div className="card shadow-sm border-0">
          <div className="list-group list-group-flush">
            {data?.data?.length === 0 && (
              <div className="p-4 text-center text-muted small">You have no notifications.</div>
            )}
            {data?.data?.map((n) => (
              <button
                key={n.notification_id}
                className={`list-group-item list-group-item-action p-3 text-start ${n.is_read ? '' : 'bg-light fw-medium'}`}
                onClick={() => handleClick(n)}
              >
                <div className="d-flex justify-content-between align-items-start mb-1">
                  <span className="fw-semibold text-primary">{n.title}</span>
                  <span className="small text-muted" style={{ fontSize: '0.75rem' }}>{fmtDate(n.created_at)}</span>
                </div>
                <div className="small text-secondary">{n.message}</div>
              </button>
            ))}
          </div>
        </div>

        <Pagination pagination={data?.pagination} onPage={setPage} />
      </div>
    </div>
  )
}
