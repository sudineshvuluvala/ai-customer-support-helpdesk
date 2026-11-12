export default function DashboardCard({ title, value, icon, tone = 'primary', hint, to, onClick }) {
  const body = (
    <div className={`stat-card tone-${tone}`}>
      <div className="stat-icon" aria-hidden="true"><i className={`bi ${icon || 'bi-bar-chart'}`} /></div>
      <div className="min-w-0 flex-grow-1">
        <div className="stat-value">{value ?? '-'}</div>
        <div className="stat-title">{title}</div>
        {hint && <div className="stat-hint">{hint}</div>}
      </div>
    </div>
  )
  if (to) return <a href={to} className="text-decoration-none stat-link d-block" onClick={(e) => { if (onClick) { e.preventDefault(); onClick() } }}>{body}</a>
  return body
}
