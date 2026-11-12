export default function Pagination({ pagination, onPage }) {
  if (!pagination || pagination.pages <= 1) {
    return pagination ? <div className="small text-muted pt-2">{pagination.total} record{pagination.total === 1 ? '' : 's'}</div> : null
  }
  const { page, pages, total } = pagination
  const nums = []
  for (let i = Math.max(1, page - 2); i <= Math.min(pages, page + 2); i++) nums.push(i)
  return (
    <nav className="d-flex flex-wrap justify-content-between align-items-center gap-2 pt-3" aria-label="Pagination">
      <span className="small text-muted">Page {page} of {pages} · {total} records</span>
      <ul className="pagination pagination-sm mb-0">
        <li className={`page-item ${page === 1 ? 'disabled' : ''}`}><button className="page-link" onClick={() => onPage(page - 1)}>Previous</button></li>
        {nums.map((n) => (
          <li key={n} className={`page-item ${n === page ? 'active' : ''}`}><button className="page-link" onClick={() => onPage(n)}>{n}</button></li>
        ))}
        <li className={`page-item ${page === pages ? 'disabled' : ''}`}><button className="page-link" onClick={() => onPage(page + 1)}>Next</button></li>
      </ul>
    </nav>
  )
}
