import Loading from './Loading'

// columns: [{ key, label, render?(row), className? }]
export default function DataTable({ columns, rows, loading, empty = 'No records found.', onRowClick, rowKey }) {
  if (loading) return <Loading />
  if (!rows || rows.length === 0) {
    return <div className="empty-state"><i className="bi bi-inbox" aria-hidden="true" /><p>{empty}</p></div>
  }
  return (
    <div className="table-responsive data-table">
      <table className="table table-hover align-middle mb-0">
        <thead>
          <tr>{columns.map((c) => <th key={c.key} className={c.className}>{c.label}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={rowKey ? r[rowKey] : i} onClick={onRowClick ? () => onRowClick(r) : undefined} className={onRowClick ? 'clickable' : ''}>
              {columns.map((c) => (
                <td key={c.key} data-label={c.label} className={c.className}>{c.render ? c.render(r) : r[c.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
