import { useNavigate } from 'react-router-dom'
import { useFetch } from '../../hooks/useFetch'
import { dashboardService } from '../../services/miscServices'
import DashboardCard from '../../components/DashboardCard'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'
import { StatusBadge, PriorityBadge, fmtDate } from '../../utils/format'

export default function AgentDashboardPage() {
  const nav = useNavigate()
  const { data, loading, error, reload } = useFetch(dashboardService.agent)

  if (loading) return <Loading text="Loading your support queue..." />
  if (error) return <ErrorMessage error={error} onRetry={reload} />

  const { tickets, recent_tickets } = data

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">Agent Workspace</h1>
          <p className="text-muted small mb-0">Manage customer assignments, pending responses, and SLA performance.</p>
        </div>
        <button className="btn btn-outline-secondary btn-sm" onClick={reload}><i className="bi bi-arrow-clockwise me-1" />Refresh</button>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-md-3">
          <DashboardCard title="Assigned Tickets" value={tickets.total} tone="primary" icon="bi-ticket-detailed" to="/agent/tickets" />
        </div>
        <div className="col-sm-6 col-md-3">
          <DashboardCard title="Pending Response" value={tickets.pending_responses} tone="danger" icon="bi-chat-left-dots" hint="Awaiting agent reply" to="/agent/tickets" />
        </div>
        <div className="col-sm-6 col-md-3">
          <DashboardCard title="In Progress" value={tickets.in_progress} tone="warning" icon="bi-hourglass-split" to="/agent/tickets" />
        </div>
        <div className="col-sm-6 col-md-3">
          <DashboardCard title="Resolved by You" value={tickets.resolved} tone="success" icon="bi-check-circle" to="/agent/tickets" />
        </div>
      </div>

      {/* Queue summary */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-header bg-white d-flex justify-content-between align-items-center">
          <span className="fw-bold">Recently Updated Assigned Tickets</span>
          <button className="btn btn-link btn-sm p-0" onClick={() => nav('/agent/tickets')}>View Queue</button>
        </div>
        <div className="card-body p-0">
          {recent_tickets?.length === 0 ? (
            <div className="p-4 text-center text-muted small">No tickets currently assigned to you.</div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0 small">
                <thead>
                  <tr>
                    <th>Ticket #</th>
                    <th>Customer</th>
                    <th>Subject</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Last Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {recent_tickets.map((t) => (
                    <tr key={t.ticket_id} className="clickable" onClick={() => nav(`/agent/tickets/${t.ticket_id}`)}>
                      <td className="fw-semibold text-primary">{t.ticket_number}</td>
                      <td>{t.customer?.name.replace(' [SEED]', '')}</td>
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
    </div>
  )
}
