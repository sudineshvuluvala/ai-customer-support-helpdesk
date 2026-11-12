import { useState } from 'react'
import { analyticsService } from '../../services/miscServices'
import { useFetch } from '../../hooks/useFetch'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'
import { fmtDate, StatusBadge, PriorityBadge } from '../../utils/format'

export default function ReportsPage() {
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')

  const { data, loading, error, reload } = useFetch(
    () => analyticsService.reports({ from: from || undefined, to: to || undefined }),
    [from, to]
  )

  const handleDownloadCsv = () => {
    analyticsService.downloadCsv({ from: from || undefined, to: to || undefined })
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">Reports &amp; Data Export</h1>
          <p className="text-muted small mb-0">Generate operational reports, agent resolution records, and CSV exports.</p>
        </div>
        <button className="btn btn-success btn-sm" onClick={handleDownloadCsv}>
          <i className="bi bi-file-earmark-excel me-1" />Export to CSV
        </button>
      </div>

      <div className="card shadow-sm border-0 mb-4 p-3">
        <div className="row g-3 align-items-end">
          <div className="col-md-3">
            <label className="form-label small fw-medium">From Date</label>
            <input type="date" className="form-control form-control-sm" value={from} onChange={(e) => setFrom(e.target.value)} />
          </div>
          <div className="col-md-3">
            <label className="form-label small fw-medium">To Date</label>
            <input type="date" className="form-control form-control-sm" value={to} onChange={(e) => setTo(e.target.value)} />
          </div>
          <div className="col-md-2">
            <button className="btn btn-outline-secondary btn-sm w-100" onClick={() => { setFrom(''); setTo('') }}>
              Reset Dates
            </button>
          </div>
        </div>
      </div>

      {loading && <Loading text="Generating report..." />}
      {error && <ErrorMessage error={error} onRetry={reload} />}

      {data && (
        <>
          <div className="row g-3 mb-4">
            <div className="col-md-4">
              <div className="card shadow-sm border-0 p-3">
                <div className="text-muted small">Total Filtered Tickets</div>
                <div className="fs-3 fw-bold">{data.summary.total}</div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card shadow-sm border-0 p-3">
                <div className="text-muted small">SLA Compliance Rate</div>
                <div className="fs-3 fw-bold text-success">{data.sla.compliance_rate != null ? `${data.sla.compliance_rate}%` : 'N/A'}</div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card shadow-sm border-0 p-3">
                <div className="text-muted small">Active Agents Evaluated</div>
                <div className="fs-3 fw-bold">{data.agent_performance.length}</div>
              </div>
            </div>
          </div>

          {/* Agent Performance Table */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white fw-bold">Agent Performance &amp; SLA Adherence</div>
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0 small">
                <thead>
                  <tr>
                    <th>Agent</th>
                    <th>Email</th>
                    <th>Active Load</th>
                    <th>Resolved Tickets</th>
                    <th>Avg. Resolution</th>
                  </tr>
                </thead>
                <tbody>
                  {data.agent_performance.map((a) => (
                    <tr key={a.user_id}>
                      <td className="fw-semibold">{a.name.replace(' [SEED]', '')}</td>
                      <td>{a.email}</td>
                      <td><span className="badge bg-primary">{a.active_tickets}</span></td>
                      <td><span className="badge bg-success">{a.resolved_tickets}</span></td>
                      <td>{a.avg_resolution_hours != null ? `${a.avg_resolution_hours} hrs` : 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
