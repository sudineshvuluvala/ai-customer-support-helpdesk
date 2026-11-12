import { useNavigate } from 'react-router-dom'
import { useFetch } from '../../hooks/useFetch'
import { dashboardService } from '../../services/miscServices'
import DashboardCard from '../../components/DashboardCard'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'
import { StatusBadge, PriorityBadge, fmtDate } from '../../utils/format'

export default function AdminDashboardPage() {
  const nav = useNavigate()
  const { data, loading, error, reload } = useFetch(dashboardService.admin)

  if (loading) return <Loading text="Loading operational analytics..." />
  if (error) return <ErrorMessage error={error} onRetry={reload} />

  const { users, tickets, category_distribution, priority_distribution, agent_workload, avg_resolution_hours, recent_activity } = data

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">System Control Center</h1>
          <p className="text-muted small mb-0">Platform overview, ticket distribution, and operational metrics.</p>
        </div>
        <button className="btn btn-outline-secondary btn-sm" onClick={reload}><i className="bi bi-arrow-clockwise me-1" />Refresh Data</button>
      </div>

      {/* Ticket Stats */}
      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-xl-3">
          <DashboardCard title="Total Tickets" value={tickets.total} tone="primary" icon="bi-ticket-detailed" to="/admin/tickets" />
        </div>
        <div className="col-sm-6 col-xl-3">
          <DashboardCard title="Unassigned" value={tickets.unassigned} tone="danger" icon="bi-person-exclamation" hint="Requires agent routing" to="/admin/tickets" />
        </div>
        <div className="col-sm-6 col-xl-3">
          <DashboardCard title="In Progress" value={tickets.in_progress} tone="warning" icon="bi-hourglass-split" to="/admin/tickets" />
        </div>
        <div className="col-sm-6 col-xl-3">
          <DashboardCard title="Resolved" value={tickets.resolved} tone="success" icon="bi-check-circle" to="/admin/tickets" />
        </div>
      </div>

      {/* Secondary Stats */}
      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-md-3">
          <div className="card shadow-sm border-0 p-3 h-100">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted small">Active Customers</span>
              <i className="bi bi-people text-primary fs-5" />
            </div>
            <div className="fs-3 fw-bold">{users.customers}</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="card shadow-sm border-0 p-3 h-100">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted small">Support Agents</span>
              <i className="bi bi-person-badge text-info fs-5" />
            </div>
            <div className="fs-3 fw-bold">{users.agents}</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="card shadow-sm border-0 p-3 h-100">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted small">Overdue / SLA Breached</span>
              <i className="bi bi-shield-exclamation text-danger fs-5" />
            </div>
            <div className={`fs-3 fw-bold ${tickets.overdue > 0 ? 'text-danger' : 'text-success'}`}>{tickets.overdue}</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="card shadow-sm border-0 p-3 h-100">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted small">Avg. Resolution Time</span>
              <i className="bi bi-speedometer2 text-warning fs-5" />
            </div>
            <div className="fs-3 fw-bold">{avg_resolution_hours != null ? `${avg_resolution_hours} hrs` : 'N/A'}</div>
          </div>
        </div>
      </div>

      <div className="row g-3 mb-4">
        {/* Priority & Category Breakdown */}
        <div className="col-lg-6">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold">Ticket Volume by Category</div>
            <div className="card-body p-0">
              <ul className="list-group list-group-flush">
                {category_distribution.map((c, i) => (
                  <li key={i} className="list-group-item d-flex justify-content-between align-items-center py-2">
                    <span className="small">{c.label}</span>
                    <span className="badge bg-light text-dark border">{c.count}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold">Agent Workload &amp; Capacity</div>
            <div className="card-body p-0">
              <ul className="list-group list-group-flush">
                {agent_workload.map((a) => (
                  <li key={a.user_id} className="list-group-item d-flex justify-content-between align-items-center py-2">
                    <div>
                      <div className="fw-semibold small">{a.name.replace(' [SEED]', '')}</div>
                      <div className="text-muted" style={{ fontSize: '0.75rem' }}>{a.email}</div>
                    </div>
                    <div>
                      <span className="badge bg-primary me-2">{a.active_tickets} Active</span>
                      <span className="badge bg-secondary">{a.total_tickets} Total</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity Audit */}
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white fw-bold">Recent System Activity (Audit Logs)</div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0 small">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {recent_activity.map((l) => (
                  <tr key={l.log_id}>
                    <td>{fmtDate(l.created_at)}</td>
                    <td>{l.user ? l.user.name.replace(' [SEED]', '') : 'System'}</td>
                    <td><span className="badge bg-light text-dark border">{l.action}</span></td>
                    <td>{l.entity_type} {l.entity_id ? `#${l.entity_id}` : ''}</td>
                    <td>{l.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
