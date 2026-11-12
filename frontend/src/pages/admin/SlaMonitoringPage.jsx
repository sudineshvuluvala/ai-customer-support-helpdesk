import { analyticsService } from '../../services/miscServices'
import { useFetch } from '../../hooks/useFetch'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'
import { SlaBadge, PriorityBadge, fmtDate } from '../../utils/format'

export default function SlaMonitoringPage() {
  const { data, loading, error, reload } = useFetch(analyticsService.sla)

  if (loading) return <Loading text="Fetching SLA tracking matrix..." />
  if (error) return <ErrorMessage error={error} onRetry={reload} />

  const { summary, at_risk_tickets, settings } = data

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">Service Level Agreement (SLA) Tracking</h1>
          <p className="text-muted small mb-0">Real-time deadline enforcement, risk alerts, and breach diagnostics.</p>
        </div>
        <button className="btn btn-outline-secondary btn-sm" onClick={reload}><i className="bi bi-arrow-clockwise me-1" />Refresh</button>
      </div>

      {summary && (
        <div className="row g-3 mb-4">
          <div className="col-sm-6 col-md-3">
            <div className="card shadow-sm border-0 p-3">
              <div className="text-muted small">SLA Compliance Rate</div>
              <div className="fs-3 fw-bold text-success">{summary.compliance_rate != null ? `${summary.compliance_rate}%` : 'N/A'}</div>
            </div>
          </div>
          <div className="col-sm-6 col-md-3">
            <div className="card shadow-sm border-0 p-3">
              <div className="text-muted small">On Track</div>
              <div className="fs-3 fw-bold text-primary">{summary.on_track}</div>
            </div>
          </div>
          <div className="col-sm-6 col-md-3">
            <div className="card shadow-sm border-0 p-3">
              <div className="text-muted small">At Risk (&lt;25% Time Left)</div>
              <div className="fs-3 fw-bold text-warning">{summary.at_risk}</div>
            </div>
          </div>
          <div className="col-sm-6 col-md-3">
            <div className="card shadow-sm border-0 p-3">
              <div className="text-muted small">Breached Deadlines</div>
              <div className="fs-3 fw-bold text-danger">{summary.breached}</div>
            </div>
          </div>
        </div>
      )}

      {/* At-Risk or Breached Tickets */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-header bg-white fw-bold">Active Incidents Requiring Escalation</div>
        <div className="card-body p-0">
          {at_risk_tickets.length === 0 ? (
            <div className="p-4 text-center text-muted small">No active tickets are currently at risk or breached.</div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0 small">
                <thead>
                  <tr>
                    <th>Ticket #</th>
                    <th>Subject</th>
                    <th>Priority</th>
                    <th>Assigned Agent</th>
                    <th>Response Target</th>
                    <th>Resolution Target</th>
                    <th>SLA State</th>
                  </tr>
                </thead>
                <tbody>
                  {at_risk_tickets.map((t) => (
                    <tr key={t.ticket_id}>
                      <td className="fw-semibold text-primary">{t.ticket_number}</td>
                      <td>{t.subject}</td>
                      <td><PriorityBadge priority={t.priority} /></td>
                      <td>{t.assigned_agent?.name.replace(' [SEED]', '') || <span className="text-danger fst-italic">Unassigned</span>}</td>
                      <td>{fmtDate(t.sla?.response_due_at)}</td>
                      <td>{fmtDate(t.sla?.resolution_due_at)}</td>
                      <td><SlaBadge sla={t.sla} /></td>
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
