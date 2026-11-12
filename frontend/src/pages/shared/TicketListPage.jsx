import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useFetch, useDebounce } from '../../hooks/useFetch'
import { ticketService } from '../../services/ticketService'
import { StatusBadge, PriorityBadge, SlaBadge, fmtDate, STATUSES, PRIORITIES } from '../../utils/format'
import DataTable from '../../components/DataTable'
import SearchBar from '../../components/SearchBar'
import FilterPanel from '../../components/FilterPanel'
import Pagination from '../../components/Pagination'
import ErrorMessage from '../../components/ErrorMessage'

export default function TicketListPage({ role = 'customer' }) {
  const nav = useNavigate()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({ status: '', priority: '' })
  const debouncedSearch = useDebounce(search, 300)

  const fetcher = () => {
    const params = {
      page,
      per_page: 10,
      q: debouncedSearch || undefined,
      status: filters.status || undefined,
      priority: filters.priority || undefined,
    }
    if (role === 'admin') return ticketService.adminList(params)
    return ticketService.list(params)
  }

  const { data, loading, error, reload } = useFetch(fetcher, [page, debouncedSearch, filters.status, filters.priority])

  const columns = [
    { key: 'ticket_number', label: 'Ticket #', render: (r) => <span className="fw-semibold text-primary">{r.ticket_number}</span> },
    { key: 'subject', label: 'Subject', render: (r) => <span className="fw-medium">{r.subject}</span> },
    ...(role === 'admin' ? [{ key: 'customer', label: 'Customer', render: (r) => r.customer?.name.replace(' [SEED]', '') || '-' }] : []),
    ...(role !== 'agent' ? [{ key: 'assigned_agent', label: 'Agent', render: (r) => r.assigned_agent?.name.replace(' [SEED]', '') || <span className="text-muted fst-italic">Unassigned</span> }] : []),
    { key: 'priority', label: 'Priority', render: (r) => <PriorityBadge priority={r.priority} /> },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
    { key: 'sla', label: 'SLA Status', render: (r) => <SlaBadge sla={r.sla} /> },
    { key: 'created_at', label: 'Created', render: (r) => <span className="small text-muted">{fmtDate(r.created_at)}</span> },
  ]

  const filterFields = [
    { name: 'status', label: 'Status', options: STATUSES.map((s) => ({ value: s, label: s.replace('_', ' ').toUpperCase() })) },
    { name: 'priority', label: 'Priority', options: PRIORITIES.map((p) => ({ value: p, label: p.toUpperCase() })) },
  ]

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h4 fw-bold mb-0">
            {role === 'admin' ? 'Ticket Master Directory' : role === 'agent' ? 'Assigned Support Tickets' : 'My Support Tickets'}
          </h1>
          <p className="text-muted small mb-0">Track, filter, and inspect support inquiries and progress.</p>
        </div>
        {role === 'customer' && (
          <button className="btn btn-primary btn-sm" onClick={() => nav('/customer/tickets/create')}>
            <i className="bi bi-plus-circle me-1" /> Create Ticket
          </button>
        )}
      </div>

      <div className="row g-2 mb-3">
        <div className="col-md-6">
          <SearchBar value={search} onChange={setSearch} placeholder="Search by number, subject, content..." />
        </div>
      </div>

      <FilterPanel
        fields={filterFields}
        values={filters}
        onChange={(k, v) => { setFilters({ ...filters, [k]: v }); setPage(1) }}
        onReset={() => { setFilters({ status: '', priority: '' }); setSearch(''); setPage(1) }}
      />

      <ErrorMessage error={error} onRetry={reload} />

      <DataTable
        columns={columns}
        rows={data?.data || []}
        loading={loading}
        rowKey="ticket_id"
        onRowClick={(r) => nav(`/${role}/tickets/${r.ticket_id}`)}
      />

      <Pagination pagination={data?.pagination} onPage={setPage} />
    </div>
  )
}
