import { analyticsService } from '../../services/miscServices'
import { useFetch } from '../../hooks/useFetch'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'

export default function AnalyticsPage() {
  const { data, loading, error, reload } = useFetch(analyticsService.overview)

  if (loading) return <Loading text="Aggregating performance analytics..." />
  if (error) return <ErrorMessage error={error} onRetry={reload} />

  const { status_counts, avg_resolution_hours, overdue, priority_distribution, category_distribution, creation_trend } = data

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">Helpdesk Analytics &amp; KPI Metrics</h1>
          <p className="text-muted small mb-0">Real-time volume trends, resolution velocity, and ticket priority.</p>
        </div>
        <button className="btn btn-outline-secondary btn-sm" onClick={reload}><i className="bi bi-arrow-clockwise me-1" />Refresh</button>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-md-3">
          <div className="card shadow-sm border-0 p-3">
            <div className="text-muted small">Avg. Resolution Duration</div>
            <div className="fs-4 fw-bold mt-1 text-primary">{avg_resolution_hours != null ? `${avg_resolution_hours} hrs` : 'N/A'}</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="card shadow-sm border-0 p-3">
            <div className="text-muted small">SLA Overdue Incidents</div>
            <div className="fs-4 fw-bold mt-1 text-danger">{overdue}</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="card shadow-sm border-0 p-3">
            <div className="text-muted small">Open Tickets</div>
            <div className="fs-4 fw-bold mt-1 text-warning">{status_counts.open + status_counts.assigned + status_counts.in_progress}</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="card shadow-sm border-0 p-3">
            <div className="text-muted small">Resolved &amp; Closed</div>
            <div className="fs-4 fw-bold mt-1 text-success">{status_counts.resolved + status_counts.closed}</div>
          </div>
        </div>
      </div>

      <div className="row g-4 mb-4">
        {/* Creation Trend Timeline */}
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold">Ticket Volume Trend (Last 14 Days)</div>
            <div className="card-body">
              <div className="d-flex align-items-end gap-2 h-100 pb-3" style={{ minHeight: '180px' }}>
                {creation_trend.map((d, i) => {
                  const max = Math.max(...creation_trend.map((x) => x.count), 5)
                  const heightPct = Math.max((d.count / max) * 100, 8)
                  return (
                    <div key={i} className="flex-grow-1 d-flex flex-column align-items-center h-100 justify-content-end">
                      <span className="small text-muted mb-1" style={{ fontSize: '0.7rem' }}>{d.count}</span>
                      <div
                        className="w-100 bg-primary rounded-top"
                        style={{ height: `${heightPct}%`, minWidth: '16px', opacity: d.count > 0 ? 1 : 0.2 }}
                      />
                      <span className="small text-muted mt-2 text-truncate" style={{ fontSize: '0.65rem', maxWidth: '38px' }}>
                        {d.date.slice(5)}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Priority Breakdown */}
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold">Distribution by Priority</div>
            <div className="card-body p-0">
              <ul className="list-group list-group-flush">
                {priority_distribution.map((p) => (
                  <li key={p.label} className="list-group-item d-flex justify-content-between align-items-center py-2 text-capitalize">
                    <span>{p.label}</span>
                    <span className="badge bg-light text-dark border">{p.count}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
