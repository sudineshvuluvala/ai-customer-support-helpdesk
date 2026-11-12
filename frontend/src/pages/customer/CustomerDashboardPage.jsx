import { useNavigate } from 'react-router-dom'
import { useFetch } from '../../hooks/useFetch'
import { dashboardService } from '../../services/miscServices'
import DashboardCard from '../../components/DashboardCard'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'
import { StatusBadge, PriorityBadge, fmtDate } from '../../utils/format'

export default function CustomerDashboardPage() {
  const nav = useNavigate()
  const { data, loading, error, reload } = useFetch(dashboardService.customer)

  if (loading) return <Loading text="Loading your support portal..." />
  if (error) return <ErrorMessage error={error} onRetry={reload} />

  const { tickets, recent_tickets, recommended_articles, notifications } = data

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">Customer Care Portal</h1>
          <p className="text-muted small mb-0">View your active support tickets, knowledge articles, and updates.</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => nav('/customer/tickets/create')}>
          <i className="bi bi-plus-circle me-1" /> Create Ticket
        </button>
      </div>

      {/* Ticket Metric Cards */}
      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-md-3">
          <DashboardCard title="Total Tickets" value={tickets.total} tone="primary" icon="bi-ticket-detailed" to="/customer/tickets" />
        </div>
        <div className="col-sm-6 col-md-3">
          <DashboardCard title="Open / In Progress" value={tickets.open + tickets.assigned + tickets.in_progress} tone="warning" icon="bi-hourglass-split" to="/customer/tickets" />
        </div>
        <div className="col-sm-6 col-md-3">
          <DashboardCard title="Waiting on You" value={tickets.waiting_for_customer} tone="info" icon="bi-chat-dots" to="/customer/tickets" />
        </div>
        <div className="col-sm-6 col-md-3">
          <DashboardCard title="Resolved &amp; Closed" value={tickets.resolved + tickets.closed} tone="success" icon="bi-check2-circle" to="/customer/tickets" />
        </div>
      </div>

      <div className="row g-4">
        {/* Recent Tickets Table */}
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white d-flex justify-content-between align-items-center">
              <span className="fw-bold">Recently Updated Tickets</span>
              <button className="btn btn-link btn-sm p-0" onClick={() => nav('/customer/tickets')}>View all</button>
            </div>
            <div className="card-body p-0">
              {recent_tickets?.length === 0 ? (
                <div className="p-4 text-center text-muted small">You haven't opened any support tickets yet.</div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0 small">
                    <thead>
                      <tr>
                        <th>Ticket #</th>
                        <th>Subject</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Last Updated</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recent_tickets.map((t) => (
                        <tr key={t.ticket_id} className="clickable" onClick={() => nav(`/customer/tickets/${t.ticket_id}`)}>
                          <td className="fw-semibold text-primary">{t.ticket_number}</td>
                          <td>{t.subject}</td>
                          <td><PriorityBadge priority={t.priority} /></td>
                          <td><StatusBadge status={t.status} /></td>
                          <td className="text-muted">{fmtDate(t.updated_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* AI Virtual Assistant Promo Banner */}
          <div className="card bg-primary-subtle border-0 p-4">
            <div className="d-flex align-items-center gap-3">
              <div className="fs-1 text-primary"><i className="bi bi-robot" /></div>
              <div>
                <h2 className="h5 fw-bold mb-1">Have an instant question?</h2>
                <p className="small text-secondary mb-2">Our AI FAQ assistant searches our official documentation and answers questions 24/7 without waiting.</p>
                <button className="btn btn-primary btn-sm" onClick={() => nav('/customer/assistant')}>
                  Open AI FAQ Assistant
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar: Recommended Knowledge Articles */}
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white fw-bold">Popular Knowledge Base Guides</div>
            <div className="card-body p-0">
              <div className="list-group list-group-flush small">
                {recommended_articles?.map((a) => (
                  <button
                    key={a.article_id}
                    className="list-group-item list-group-item-action text-start"
                    onClick={() => nav(`/customer/knowledge/${a.article_id}`)}
                  >
                    <div className="fw-semibold text-primary mb-1">{a.title}</div>
                    <div className="text-muted small">{a.summary}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
