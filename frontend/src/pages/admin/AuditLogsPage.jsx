import { useState } from 'react'
import { analyticsService } from '../../services/miscServices'
import { useFetch } from '../../hooks/useFetch'
import DataTable from '../../components/DataTable'
import Pagination from '../../components/Pagination'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'
import { fmtDate } from '../../utils/format'

export default function AuditLogsPage() {
  const [page, setPage] = useState(1)
  const { data, loading, error, reload } = useFetch(
    () => analyticsService.auditLogs({ page, per_page: 20 }),
    [page]
  )

  const columns = [
    { key: 'created_at', label: 'Timestamp', render: (l) => <span className="small text-muted">{fmtDate(l.created_at)}</span> },
    { key: 'user', label: 'Actor', render: (l) => (l.user ? l.user.name.replace(' [SEED]', '') : 'System') },
    { key: 'action', label: 'Action', render: (l) => <span className="badge bg-light text-dark border">{l.action}</span> },
    { key: 'entity', label: 'Target Entity', render: (l) => `${l.entity_type} ${l.entity_id ? `#${l.entity_id}` : ''}` },
    { key: 'description', label: 'Audit Trail Details' },
  ]

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">System Security &amp; Audit Logs</h1>
          <p className="text-muted small mb-0">Immutable records of authentication, ticket updates, role changes, and admin operations.</p>
        </div>
        <button className="btn btn-outline-secondary btn-sm" onClick={reload}><i className="bi bi-arrow-clockwise me-1" />Refresh</button>
      </div>

      <ErrorMessage error={error} onRetry={reload} />
      <DataTable columns={columns} rows={data?.data || []} loading={loading} rowKey="log_id" />
      <Pagination pagination={data?.pagination} onPage={setPage} />
    </div>
  )
}
